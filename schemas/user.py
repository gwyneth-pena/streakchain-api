
from typing import Optional
from pydantic import model_validator

from schemas.shared import TrimmedBaseModel

class UserCreate(TrimmedBaseModel):
    firstname: str
    lastname: str
    email: Optional[str] = None 
    password: Optional[str] = None
    method: str = 'email'
    identifier: Optional[str] = None
    token: Optional[str] = None

    @model_validator(mode='after')
    def check_method(cls, values):
        values.identifier = values.identifier.lower() if values.identifier else None
        values.firstname = values.firstname.title()
        values.lastname = values.lastname.title()
        values.method = values.method.lower()
        values.email = values.email.lower() if values.email else None

        method = values.method
        email = values.email
        password = values.password
        token = values.token

        if method == 'email':
            if not email:
                raise ValueError('Email is required for email signup.')
            if '@' not in email:
                raise ValueError('Email must be valid.')
            if not password or len(password) < 8:
                raise ValueError('Password is required and must be at least 8 characters for email signup.')
            values.identifier = email
        else:
            if not token:
                raise ValueError(f'{method} auth method requires a token.')
            
        return values
    

class UserSignIn(TrimmedBaseModel):
    method: str
    identifier: str
    password: Optional[str] = None