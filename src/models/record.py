import uuid

from src.db.database import Base
from sqlalchemy import Column, String, UUID, ForeignKey, Float


class Record(Base):
    __tablename__ = 'records'
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('users.id'))
    amount = Column(Float)
    type = Column(String)
    description = Column(String)
    currency = Column(String)

