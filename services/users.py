
from models.user import User
from models.user_login import UserLogin
from schemas.user import UserCreate
from sqlalchemy.orm import Session


def save_user(payload: UserCreate, db: Session):
    user = User(firstname=payload.firstname, lastname=payload.lastname, email=payload.email)
    user_login = UserLogin(
        user=user,
        method=payload.method,
        identifier=payload.identifier,
        password=payload.password
    )
    user.logins.append(user_login)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user