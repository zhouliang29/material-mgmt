"""部门模型"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Department(Base):
    """部门"""
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), default=None, nullable=True, comment="父部门ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="部门编码")
    manager: Mapped[str] = mapped_column(String(50), default="", comment="负责人")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    parent: Mapped["Department"] = relationship(remote_side="Department.id", lazy="selectin")
