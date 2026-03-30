import uuid
from datetime import datetime

from src.db.database import Base
from sqlalchemy import Column, String, UUID, ForeignKey, Float, DateTime


class Record(Base):
    __tablename__ = 'records'
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('users.id'))

    amount = Column(Float)
    type = Column(String)
    description = Column(String)
    currency = Column(String)
    mono_card_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)

