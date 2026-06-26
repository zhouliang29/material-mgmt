"""仓库/库位相关 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ========== 仓库 ==========

class WarehouseCreate(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    address: str = Field(default="", max_length=300)
    manager: str = Field(default="", max_length=50)
    remark: str = ""


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    manager: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseOut(BaseModel):
    id: int
    name: str
    code: str
    address: str
    manager: str
    remark: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 库位 ==========

class LocationCreate(BaseModel):
    warehouse_id: int
    zone: str = Field(default="", max_length=50)
    rack: str = Field(default="", max_length=50)
    row: str = Field(default="", max_length=50)
    col: str = Field(default="", max_length=50)
    code: str = Field(..., max_length=100)
    remark: str = ""


class LocationUpdate(BaseModel):
    zone: Optional[str] = None
    rack: Optional[str] = None
    row: Optional[str] = None
    col: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None


class LocationOut(BaseModel):
    id: int
    warehouse_id: int
    zone: str
    rack: str
    row: str
    col: str
    code: str
    remark: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
