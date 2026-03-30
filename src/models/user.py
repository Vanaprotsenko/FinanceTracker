import uuid

from sqlalchemy.dialects.postgresql import UUID
from src.db.database import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    telegram_id = Column(String, unique=True, nullable=True)
    telegram_username = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    mono_token = Column(String, nullable=True)

    mono_account = relationship("MonoCards", back_populates="user", uselist=False)