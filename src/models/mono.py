import uuid
from sqlalchemy.dialects.postgresql import UUID
from src.db.database import Base
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class MonoCards(Base):

    __tablename__ = 'mono_cards'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    card_id = Column(String, unique=True, nullable=False)
    currency_code = Column(Integer, nullable=False)
    balance = Column(Float)
    mono_card_name = Column(String, nullable=True)

    user = relationship("User", back_populates="mono_account")

    transactions = relationship(
        "MonoTransaction",
        back_populates="card",
        cascade="all, delete-orphan"
    )


class MonoTransaction(Base):

    __tablename__ = 'mono_transaction'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey('mono_cards.id', ondelete="CASCADE"),
        nullable=False
    )

    time = Column(DateTime(timezone=True), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    operationAmount = Column(Float, nullable=False)
    currency = Column(Integer, nullable=False)

    card = relationship("MonoCards", back_populates="transactions")

