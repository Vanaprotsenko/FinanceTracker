import uuid

from src.db.database import Base
from sqlalchemy import Column, UUID, String, Float, ForeignKey


class Savings(Base):
    __tablename__ = 'savings'
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)