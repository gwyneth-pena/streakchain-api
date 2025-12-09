from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from models.user_login import UserLogin
from schemas.user import UserCreate, UserSignIn
from argon2 import PasswordHasher
from services.users import authenticate_user, save_user
from utils.shared import create_jwt, validation_error

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create")
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing_email = (
        db.query(User)
        .join(User.logins)
        .filter(User.email == payload.email, 
                UserLogin.method == 'email',
            )
        .first()
    )
    
    if existing_email:
        validation_error("email", "Email already exists.", "email")
    
    hasher = PasswordHasher()
    hashed_password = hasher.hash(payload.password)
    payload.password = hashed_password

    user = save_user(payload, db)
    
    if user:
        jwt_token = create_jwt({"user_id": user.id})
        response.set_cookie(key="jwt", value=jwt_token, httponly=True, max_age=60*60)

    return {"message": "User created successfully."}


@router.post('/login')
def login_user(payload: UserSignIn, response: Response, db: Session = Depends(get_db)):
    user_login = authenticate_user(payload, db)
    
    if not user_login['is_authenticated']:
        validation_error("credentials", "Invalid credentials.", "credentials", 401)

    jwt_token = create_jwt({"user_id": user_login['data'].user_id})

    response.set_cookie(key="jwt", value=jwt_token, httponly=True, max_age=60*60)

    return {"message": "Login successful."}