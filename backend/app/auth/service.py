from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import UserCreate, UserLogin
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.db.models import User
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == normalize_email(email))
    return db.scalar(statement)


def register_user(db: Session, user_in: UserCreate) -> User:
    email = normalize_email(str(user_in.email))
    existing_user = get_user_by_email(db=db, email=email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        email=email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, credentials: UserLogin) -> User | None:
    user = get_user_by_email(db=db, email=str(credentials.email))
    if user is None:
        return None

    if not verify_password(credentials.password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user


def create_user_access_token(user: User) -> str:
    return create_access_token(subject=user.email)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    user = get_user_by_email(db=db, email=email)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return current_user
