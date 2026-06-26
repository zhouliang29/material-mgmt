"""供应商相关 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    contact: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=30)
    email: str = Field(default="", max_length=100)
    address: str = Field(default="", max_length=300)
    remark: str = ""


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierOut(BaseModel):
    id: int
    name: str
    code: str
    contact: str
    phone: str
    email: str
    address: str
    remark: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
