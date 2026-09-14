from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, UserLogin


def authenticate_user(db: Session, credentials: UserLogin) -> User:
    user = db.scalar(select(User).where(User.username == credentials.username))

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is inactive")

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    return user


def login_user(db: Session, credentials: UserLogin) -> dict:
    user = authenticate_user(db, credentials)

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    role = user.role.value if hasattr(user.role, "value") else str(user.role)

    access_token = create_access_token(user_id=user.id, username=user.username, role=role)

    return {"access_token": access_token, "token_type": "bearer", "role": role}


def get_user_from_token(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

    if not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account is inactive")

    return user


def change_password(db: Session, user: User, payload: ChangePasswordRequest) -> None:
    if not verify_password(payload.old_password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Current password is incorrect")

    if payload.old_password == payload.new_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "New password must differ from the old one")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()