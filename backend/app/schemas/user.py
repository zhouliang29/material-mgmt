"""用户相关 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== 请求 ==========

class UserLogin(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    real_name: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=20)
    email: str = Field(default="", max_length=100)
    role_ids: List[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


# ========== 响应 ==========

class RoleBrief(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    username: str
    real_name: str
    phone: str
    email: str
    is_active: bool
    is_superuser: bool
    roles: List[RoleBrief] = []
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
