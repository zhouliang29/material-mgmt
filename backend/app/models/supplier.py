"""供应商模型"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Supplier(Base):
    """供应商"""
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="供应商名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="供应商编码")
    contact: Mapped[str] = mapped_column(String(50), default="", comment="联系人")
    phone: Mapped[str] = mapped_column(String(30), default="", comment="电话")
    email: Mapped[str] = mapped_column(String(100), default="", comment="邮箱")
    address: Mapped[str] = mapped_column(String(300), default="", comment="地址")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
