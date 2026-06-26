"""物料相关 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== 物料分类 ==========

class CategoryCreate(BaseModel):
    parent_id: Optional[int] = None
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryOut(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    code: str
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryTree(CategoryOut):
    """分类树节点"""
    children: List["CategoryTree"] = []


# ========== 物料 ==========

class MaterialCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    spec: str = Field(default="", max_length=200)
    model: str = Field(default="", max_length=100)
    category_id: Optional[int] = None
    unit: str = Field(default="个", max_length=20)
    safety_stock: float = 0
    max_stock: float = 0
    price: float = 0
    image_url: str = Field(default="", max_length=500)
    remark: str = ""


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    spec: Optional[str] = None
    model: Optional[str] = None
    category_id: Optional[int] = None
    unit: Optional[str] = None
    safety_stock: Optional[float] = None
    max_stock: Optional[float] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None


class MaterialOut(BaseModel):
    id: int
    code: str
    name: str
    spec: str
    model: str
    category_id: Optional[int]
    unit: str
    safety_stock: float
    max_stock: float
    price: float
    image_url: str
    remark: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # 嵌套
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


class MaterialListParams(BaseModel):
    """物料列表查询参数"""
    page: int = 1
    page_size: int = 20
    keyword: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
