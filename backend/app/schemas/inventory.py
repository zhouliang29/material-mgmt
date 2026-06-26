"""库存和出入库相关 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== 库存查询 ==========

class InventoryQuery(BaseModel):
    page: int = 1
    page_size: int = 20
    warehouse_id: Optional[int] = None
    material_id: Optional[int] = None
    keyword: Optional[str] = None
    low_stock: Optional[bool] = None  # 仅查低库存


class InventoryOut(BaseModel):
    id: int
    material_id: int
    warehouse_id: int
    location_id: Optional[int]
    quantity: float
    frozen_quantity: float
    available_quantity: float
    safety_stock: float
    max_stock: float
    updated_at: datetime
    # 嵌套信息
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    material_spec: Optional[str] = None
    material_unit: Optional[str] = None
    warehouse_name: Optional[str] = None
    location_code: Optional[str] = None

    class Config:
        from_attributes = True


# ========== 入库单 ==========

class StockInItemCreate(BaseModel):
    material_id: int
    location_id: Optional[int] = None
    plan_quantity: float = Field(default=0, ge=0)
    actual_quantity: float = Field(default=0, ge=0)
    unit_price: float = 0
    remark: str = ""


class StockInOrderCreate(BaseModel):
    order_type: str = Field(default="purchase")  # purchase/produce/return
    warehouse_id: int
    supplier_id: Optional[int] = None
    remark: str = ""
    items: List[StockInItemCreate]


class StockInOrderUpdate(BaseModel):
    """仅 draft 状态可修改"""
    order_type: Optional[str] = None
    warehouse_id: Optional[int] = None
    supplier_id: Optional[int] = None
    remark: Optional[str] = None
    items: Optional[List[StockInItemCreate]] = None


class StockInItemOut(BaseModel):
    id: int
    material_id: int
    location_id: Optional[int]
    plan_quantity: float
    actual_quantity: float
    unit_price: float
    remark: str
    material_code: Optional[str] = None
    material_name: Optional[str] = None

    class Config:
        from_attributes = True


class StockInOrderOut(BaseModel):
    id: int
    order_no: str
    order_type: str
    warehouse_id: int
    supplier_id: Optional[int]
    status: str
    applicant_id: int
    approver_id: Optional[int]
    remark: str
    created_at: datetime
    updated_at: datetime
    items: List[StockInItemOut] = []

    class Config:
        from_attributes = True


# ========== 出库单 ==========

class StockOutItemCreate(BaseModel):
    material_id: int
    location_id: Optional[int] = None
    plan_quantity: float = Field(default=0, ge=0)
    actual_quantity: float = Field(default=0, ge=0)
    unit_price: float = 0
    remark: str = ""


class StockOutOrderCreate(BaseModel):
    order_type: str = Field(default="requisition")  # requisition/return_supplier/scrap
    warehouse_id: int
    department_id: Optional[int] = None
    remark: str = ""
    items: List[StockOutItemCreate]


class StockOutOrderUpdate(BaseModel):
    order_type: Optional[str] = None
    warehouse_id: Optional[int] = None
    department_id: Optional[int] = None
    remark: Optional[str] = None
    items: Optional[List[StockOutItemCreate]] = None


class StockOutItemOut(BaseModel):
    id: int
    material_id: int
    location_id: Optional[int]
    plan_quantity: float
    actual_quantity: float
    unit_price: float
    remark: str
    material_code: Optional[str] = None
    material_name: Optional[str] = None

    class Config:
        from_attributes = True


class StockOutOrderOut(BaseModel):
    id: int
    order_no: str
    order_type: str
    warehouse_id: int
    department_id: Optional[int]
    status: str
    applicant_id: int
    approver_id: Optional[int]
    remark: str
    created_at: datetime
    updated_at: datetime
    items: List[StockOutItemOut] = []

    class Config:
        from_attributes = True
