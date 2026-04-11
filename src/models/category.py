import uuid

from src.db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, UUID, ForeignKey


class Category(Base):
    __tablename__ = 'category'
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)

    records = relationship('Record', back_populates='category')