import os
import requests
from dotenv import load_dotenv
load_dotenv()
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

bearer = HTTPBearer()
_jwks_cache = None


def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        url = f"{os.getenv('SUPABASE_URL')}/auth/v1/.well-known/jwks.json"
        _jwks_cache = requests.get(url).json()
    return _jwks_cache


def get_user_id(credentials: HTTPAuthorizationCredentials = Security(bearer)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            get_jwks(),
            algorithms=["ES256", "HS256"],
            options={"verify_aud": False}
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token sin user_id")
        return user_id
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
