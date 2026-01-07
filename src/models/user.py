import uuid

from sqlalchemy.dialects.postgresql import UUID
from src.db.database import Base
from sqlalchemy import Column, String


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    password = Column(String, nullable=False)