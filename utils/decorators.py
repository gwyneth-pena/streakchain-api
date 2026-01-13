
from functools import wraps
from fastapi import Request, Response
from utils.shared import decode_jwt, validation_error


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request')
        response: Response = kwargs.get("response")

        jwt = request.cookies.get("jwt")

        if not jwt:
            return validation_error("jwt", "JWT cookie not found.", "jwt", 401)  
        
        is_valid = False
        try:
            decoded_token = decode_jwt(jwt)
            is_valid = True
        except Exception:
            pass

        if not is_valid:
            response.delete_cookie(
                key="jwt",
                path="/",
                samesite='none',
                secure=True
            )
            return validation_error("jwt", "Invalid JWT cookie.", "jwt", 401)
        
        request.state.user_id = decoded_token['user_id']
        return func(*args, **kwargs)
    
    return wrapper