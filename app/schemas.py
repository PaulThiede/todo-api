from pydantic import BaseModel, EmailStr, Field

from typing import Optional
from datetime import datetime
from uuid import UUID as uuid
from uuid import uuid4

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class CreateItemRequest(BaseModel): # This extends the BaseModel to create an item class
    title: str
    description: str

class UpdateItemRequest(BaseModel): # This extends the BaseModel to create an item class
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None

class UserRead(BaseModel): # This extends the BaseModel to create an item class
    username: str
    email: str
    hashed_password: str
    token_version: int
    created_at: datetime = Field(default_factory=datetime.now)
    id: uuid = Field(default_factory=uuid4)

    
class ItemRead(BaseModel): # This extends the BaseModel to create an item class
    title: str
    user_id: uuid
    description: Optional[str] = None
    is_done: Optional[bool] = False
    created_at: datetime = Field(default_factory=datetime.now)
    id: uuid = Field(default_factory=uuid4)