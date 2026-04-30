from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.transactions import service
from app.transactions.schemas import TransactionCreate, TransactionRead


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
) -> TransactionRead:
    return service.create_transaction(db=db, transaction_in=transaction_in)


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[TransactionRead]:
    return service.list_transactions(db=db, limit=limit, offset=offset)
