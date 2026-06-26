"""仓库和库位模型"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Warehouse(Base):
    """仓库"""
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="仓库名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="仓库编码")
    address: Mapped[str] = mapped_column(String(300), default="", comment="地址")
    manager: Mapped[str] = mapped_column(String(50), default="", comment="负责人")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    locations: Mapped[list["StorageLocation"]] = relationship(back_populates="warehouse", lazy="selectin")


class StorageLocation(Base):
    """库位"""
    __tablename__ = "storage_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    zone: Mapped[str] = mapped_column(String(50), default="", comment="区")
    rack: Mapped[str] = mapped_column(String(50), default="", comment="架")
    row: Mapped[str] = mapped_column(String(50), default="", comment="排")
    col: Mapped[str] = mapped_column(String(50), default="", comment="位")
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="库位编码")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    warehouse: Mapped["Warehouse"] = relationship(back_populates="locations")
