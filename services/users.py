
from datetime import datetime, timedelta
import secrets
from config import FRONTEND_URL
from models.user import User
from models.user_login import UserLogin
from schemas.user import PasswordReset, PasswordResetToken, UserCreate
from services.email import send_email
from sqlalchemy.orm import Session
from sqlalchemy import func
from utils.shared import decode_and_verify_google_token, verify_password
from fastapi import BackgroundTasks


def save_user(payload: UserCreate, db: Session, background_tasks: BackgroundTasks,):
    if payload.method != 'email':
        decoded_google_token = decode_and_verify_google_token(payload.token)

        payload.email = decoded_google_token.get('email')
        payload.identifier = decoded_google_token.get('sub')
        payload.firstname = decoded_google_token.get('given_name')
        payload.lastname = decoded_google_token.get('family_name')

    
    user = (
        db.query(User)
        .join(User.logins)
        .filter(
                User.is_active == True,
                User.email == payload.email,
            )
        .first()
    )
        
    if user is None:
        user = User(firstname=payload.firstname, lastname=payload.lastname, email=payload.email)
        background_tasks.add_task(send_email, payload.email, "Welcome to StreakChain", "welcome.html", {
            "login_link": f"{FRONTEND_URL}/login"
        })

    has_user_login = False
    if user:
        filtered_user_logins = [
            login for login in user.logins
            if login.method == payload.method and login.identifier == payload.identifier
        ]
        has_user_login = len(filtered_user_logins) > 0

    if has_user_login:
        return user

    user_login = UserLogin(
        user=user,
        method=payload.method,
        identifier=payload.identifier,
        password=payload.password,
        last_login_at=func.now()
    )
    user.logins.append(user_login)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(payload: UserLogin, db: Session):
    if payload.method != 'email' and payload.token is not None:
        decoded_google_token = decode_and_verify_google_token(payload.token)
        payload.identifier = decoded_google_token.get('sub')
        
    user_login = db.query(UserLogin).filter(
        UserLogin.method == payload.method,
        UserLogin.identifier == payload.identifier
    ).first()

    if user_login is None:
        return {
            'is_authenticated': False,
            'data': None
        }
    
    if payload.method == 'email':
        is_correct_password = False

        if payload.password:
            is_correct_password = verify_password(payload.password, user_login.password)
        
        if  not is_correct_password:
            return {
                'is_authenticated': False,
                'data': None
            }

    user_login.last_login_at = func.now()
    db.commit()
    
    return {
        'is_authenticated': True,
        'data': user_login
    }


def generate_password_reset_token(mongo_db, email: str, expires_in_minutes: int = 60):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
    reset_token = PasswordResetToken(email=email, token=token, expires_at=expires_at)

    mongo_db.passwordtokens.insert_one(reset_token.dict())
    mongo_db.passwordtokens.create_index("expires_at", expireAfterSeconds=0)
    
    return reset_token.token


def change_password(payload: PasswordReset, db: Session) :
    user_login = db.query(UserLogin).filter(
        UserLogin.method == 'email',
        UserLogin.identifier == payload.get('email')
    ).first()

    if not user_login:
        return False
    
    user_login.password = payload.get('new_password')
    db.commit()

    return True