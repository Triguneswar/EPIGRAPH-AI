from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    # 1. If valid JWT token is provided, use it
    if token:
        user_id = decode_access_token(token)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user

    # 2. Seamless no-login mode: automatic default active researcher
    user = db.query(User).filter(User.email == "admin@mail.com").first()
    if not user:
        user = db.query(User).first()
    if not user:
        import uuid
        import bcrypt
        user = User(
            id=str(uuid.uuid4()),
            email="researcher@epigraph.ai",
            full_name="EPIGRAPH-AI Researcher",
            hashed_password=bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode(),
            is_admin=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    return user
