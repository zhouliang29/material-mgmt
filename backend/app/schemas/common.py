"""通用响应模型"""
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel):
    """统一响应格式"""
    code: int = 0
    message: str = "success"


class ResponseData(ResponseBase):
    """带数据的响应"""
    data: Optional[dict | list] = None


class PageParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20


class PageResult(BaseModel):
    """分页结果"""
    total: int = 0
    page: int = 1
    page_size: int = 20
    items: List[dict] = []
