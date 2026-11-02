from typing import Generator
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.security.jwt import decode_access_token
from app.utils.exceptions import AuthenticationError


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise AuthenticationError("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid Authorization format. Expected 'Bearer <token>'")

    token = parts[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise AuthenticationError("Invalid or expired authentication token")

    user_id = payload.get("sub")
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise AuthenticationError("Invalid token subject")

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise AuthenticationError("User associated with token does not exist")

    return user
