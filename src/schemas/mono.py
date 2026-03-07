import uuid
from datetime import datetime
from pydantic import BaseModel

class MonoTransactionOut(BaseModel):
    id: uuid.UUID
    time: datetime
    description: str
    amount: float
    operationAmount: float
    currency: int

    class Config:
        orm_mode = True

class MonoSaveTransactionResponse(BaseModel):
    response: str

class MonoTransactionResponse(BaseModel):
    response: list[MonoTransactionOut]

class MonoCardOut(BaseModel):
    user_id: uuid.UUID
    card_id: str
    currency_code: int
    balance: float
    transactions: list[MonoTransactionOut] = []

    class Config:
        orm_mode = True

class MonoAccountsResponse(BaseModel):
    response: list[MonoCardOut]

class MonoSyncTransactionsResponse(BaseModel):
    response: str
