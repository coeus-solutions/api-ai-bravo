from pydantic import BaseModel, EmailStr, constr, conint, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseDBModel, TimestampModel
from app.core.constants import UserRole, TransactionType, MAX_POST_LENGTH, MAX_COMMENT_LENGTH

# User schemas
class UserBase(BaseModel):
    full_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: constr(min_length=8)
    company_name: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None

class UserInDB(UserBase, BaseDBModel, TimestampModel):
    id: int
    company_id: int
    role: UserRole
    giveable_points: int
    redeemable_points: int
    deleted_at: Optional[datetime] = None

class User(UserInDB):
    pass

# Company schemas
class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase, BaseDBModel, TimestampModel):
    id: int

# Points Transaction schemas
class PointsRecipient(BaseModel):
    user_id: int
    points: conint(gt=0)

class TransactionBase(BaseModel):
    points: conint(gt=0)
    recipients: List[PointsRecipient]

class PostTransactionCreate(TransactionBase):
    content: constr(max_length=MAX_POST_LENGTH)

class CommentTransactionCreate(TransactionBase):
    content: constr(max_length=MAX_COMMENT_LENGTH)
    post_id: int

class Transaction(BaseDBModel, TimestampModel):
    id: int
    sender_id: int
    transaction_type: TransactionType
    points: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    admin_notes: Optional[str] = None

# Post schemas
class PostBase(BaseModel):
    content: constr(max_length=MAX_POST_LENGTH)

class PostCreate(PostBase):
    pass

class Post(PostBase, BaseDBModel, TimestampModel):
    id: int
    author_id: int
    total_points: int
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0)

# Comment schemas
class CommentBase(BaseModel):
    content: constr(max_length=MAX_COMMENT_LENGTH)

class CommentCreate(CommentBase):
    post_id: int

class Comment(CommentBase, BaseDBModel, TimestampModel):
    id: int
    post_id: int
    author_id: int
    total_points: int
    like_count: int = Field(default=0)

# Like schemas
class LikeCreate(BaseModel):
    pass

class Like(BaseDBModel, TimestampModel):
    id: int
    user_id: int

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # JWT subject (user ID) as string
    exp: datetime  # JWT expiration time
    iat: datetime  # Token issued at time
  