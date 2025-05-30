from pydantic import BaseModel, Field
from sqlalchemy import Column, Boolean, String, TIMESTAMP, Integer
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext

from hashlib import sha256
from datetime import datetime
from uuid import uuid4
from uuid import UUID as uuid
from typing import Optional

from .db import Base

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    token_version = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.now)

    @classmethod
    def create(cls, username: str, email: str, password: str) -> "User":
        return cls(
            username=username,
            email=email,
            token_version=0,
            hashed_password=bcrypt_context.hash(password),
            created_at=datetime.now(),
            id=uuid4()
        )

    @classmethod
    def update_password(cls, password: str):
        return bcrypt_context.hash(password)
    

class Item(Base):
    __tablename__ = "items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String)
    description = Column(String, default="")
    user_id = Column(UUID(as_uuid=True))
    is_done = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.now)

    @classmethod
    def create(cls, title: str, user_id: UUID, description: str = "") -> "User":
        return cls(
            title=title,
            description=description,
            user_id=user_id,
            is_done=False,
            created_at=datetime.now(),
            id=uuid4()
        )



    
class Token(BaseModel):
    access_token: str
    token_type: str


