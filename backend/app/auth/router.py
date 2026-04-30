from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schemas import Token, UserCreate, UserLogin, UserRead
from app.db.models import User
from app.db.session import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    return service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    user = service.authenticate_user(db=db, credentials=credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=service.create_user_access_token(user=user))


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(service.get_current_active_user),
) -> UserRead:
    return current_user
