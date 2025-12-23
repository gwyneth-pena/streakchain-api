
from datetime import datetime
from typing import Optional
from argon2 import PasswordHasher
from pydantic import model_validator, EmailStr

from schemas.shared import TrimmedBaseModel
from utils.shared import validation_error

class UserCreate(TrimmedBaseModel):
    firstname: str
    lastname: str
    email: Optional[str] = None 
    password: Optional[str] = None
    method: str = 'email'
    identifier: Optional[str] = None
    token: Optional[str] = None

    @model_validator(mode='before')
    def normalize_fields(cls, values):
        if values.get("identifier"):
            values["identifier"] = values["identifier"].lower()

        if values.get("email"):
            values["email"] = values["email"].lower()

        if values.get("method"):
            values["method"] = values["method"].lower()

        if values.get("firstname"):
            values["firstname"] = values["firstname"].title()

        if values.get("lastname"):
            values["lastname"] = values["lastname"].title()
        return values

    @model_validator(mode='after')
    def validate_fields(cls, values):

        method = values.method
        email = values.email
        password = values.password
        token = values.token

        if method == 'email':
            if not email:
                validation_error('email', 'Email is required for email signup.')
            if '@' not in email:
                validation_error('email', 'Email must be valid.')
            if not password or len(password) < 8:
                validation_error('password', 'Password is required and must be at least 8 characters for email signup.')
            values.identifier = email
        else:
            if not token:
                raise ValueError(f'{method} auth method requires a token.')
            
        if values.password:
            hasher = PasswordHasher()
            hashed_password = hasher.hash(values.password)
            values.password = hashed_password
            
        return values
    

class UserSignIn(TrimmedBaseModel):
    method: str
    identifier: str
    token: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode='after')
    def validate_fields(cls, values):
        method = values.method
        identifier = values.identifier
        password = values.password
        token = values.token

        if method == 'email':
            if not identifier:
                validation_error('identifier', 'Email is required for email login.', 'identifier')
            if '@' not in identifier:
                validation_error('identifier', 'Email must be valid.' , 'identifier')
            if not password:
                validation_error('password', 'Password is required for email login.', 'password')
        else:
            if not token:
                validation_error('token', f'{method} auth method requires a token.', 'token')
            
        return values
    

class UserPasswordResetRequest(TrimmedBaseModel):
    email: EmailStr


class PasswordResetToken(TrimmedBaseModel):
    email: EmailStr
    token: str
    expires_at: datetime


class PasswordReset(TrimmedBaseModel):
    token: str
    new_password: str
    email: Optional[EmailStr] = None

    @model_validator(mode='after')
    def validate_fields(cls, values):
        new_password = values.new_password

        if not new_password:
            validation_error('new_password', 'New password is required.', 'new_password')

        if len(new_password) < 8:
            validation_error('new_password', 'New password must be at least 8 characters.', 'new_password')

        if new_password:
            hasher = PasswordHasher()
            hashed_password = hasher.hash(new_password)
            values.new_password = hashed_password

        return values