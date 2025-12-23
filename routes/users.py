from datetime import datetime
from config import FRONTEND_URL
from fastapi import APIRouter, Depends, Request, Response, BackgroundTasks
from models.user_login import UserLogin
from services.email import send_email
from sqlalchemy.orm import Session
from db import get_db, get_mongo_db
from models.user import User
from schemas.user import PasswordReset, UserCreate, UserPasswordResetRequest, UserSignIn
from services.users import authenticate_user, change_password, generate_password_reset_token, save_user
from utils.decorators import jwt_required
from utils.shared import create_jwt_cookie, validation_error

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create")
def create_user(payload: UserCreate, response: Response, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .join(User.logins)
        .filter(User.email == payload.email, 
                User.is_active == True,
            )
        .first()
    )
    
    if existing_user:
        filtered_user_logins = [
            login for login in existing_user.logins
            if login.method == 'email' and login.identifier == payload.identifier
        ]
        has_user_login = len(filtered_user_logins) > 0
        if has_user_login and payload.method == 'email':
            validation_error("email", "Email already exists.", "email")
    
    user = save_user(payload, db, background_tasks)

    if user:
        create_jwt_cookie(response, {"user_id": user.id})

    return {"message": "User created successfully."}


@router.post('/login')
def login_user(payload: UserSignIn, response: Response, db: Session = Depends(get_db)):
    user_login = authenticate_user(payload, db)
    
    if not user_login['is_authenticated']:
        validation_error("credentials", "Invalid credentials.", "credentials", 401)

    create_jwt_cookie(response, {"user_id": user_login['data'].user_id})
    
    return {"message": "Login successful."}


@router.post("/request-password-reset")
def request_password_reset(payload: UserPasswordResetRequest, background_tasks: BackgroundTasks, response: Response, db: Session = Depends(get_db), mongo_db=Depends(get_mongo_db)):
    user_login = db.query(UserLogin).filter(UserLogin.identifier == payload.email, UserLogin.method == 'email').first()
    if not user_login:
        validation_error("email", "Email does not exist.", "email")
    token = generate_password_reset_token(mongo_db, payload.email, 15)
    background_tasks.add_task(send_email, payload.email, "Password Reset Request", "password_reset.html", {
        "reset_link": f"{FRONTEND_URL}/reset-password?token={token}",
        "expiry": '15 minutes'
    })
    return {"message": "Password reset link has been sent to your email."}


@router.post("/reset-password")
def reset_password(payload: PasswordReset, db: Session = Depends(get_db), mongo_db=Depends(get_mongo_db)):
    token = payload.token
    password_token = mongo_db.passwordtokens.find_one({"token": token})

    if not password_token:
        validation_error("token", "Invalid token.", "token")

    if password_token.get('expires_at') < datetime.now():
        validation_error("token", "Token has expired.", "token")

    
    reset_res = change_password({
        **payload.dict(),
        "email": password_token.get('email')
    }, db)


    if not reset_res:
        validation_error("user", "User does not exist.", "user")

    mongo_db.passwordtokens.delete_one({"token": token})

    return {"message": "Password has been reset successfully."}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("jwt")
    return {"message": "Logout successful."}


@router.get("/me")
@jwt_required
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    if not user_id:
        validation_error("jwt", "JWT cookie not found.", "jwt", 401)

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        validation_error("user", "User not found.", "user", 401)

    return user