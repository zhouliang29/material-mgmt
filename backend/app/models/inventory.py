"""库存和出入库模型"""
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Inventory(Base):
    """库存"""
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("materials.id"), nullable=False, comment="物料ID")
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("storage_locations.id"), nullable=True, comment="库位ID")
    quantity: Mapped[float] = mapped_column(Float, default=0, comment="库存数量")
    frozen_quantity: Mapped[float] = mapped_column(Float, default=0, comment="冻结数量")
    safety_stock: Mapped[float] = mapped_column(Float, default=0, comment="安全库存")
    max_stock: Mapped[float] = mapped_column(Float, default=0, comment="最大库存")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    material: Mapped["Material"] = relationship(lazy="selectin")
    warehouse: Mapped["Warehouse"] = relationship(lazy="selectin")
    location: Mapped["StorageLocation"] = relationship(lazy="selectin")

    @property
    def available_quantity(self) -> float:
        """可用数量 = 库存 - 冻结"""
        return self.quantity - self.frozen_quantity


class InventoryTransaction(Base):
    """库存流水"""
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("materials.id"), nullable=False, comment="物料ID")
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("storage_locations.id"), nullable=True, comment="库位ID")
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="关联单据ID")
    order_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="单据类型: stock_in/stock_out/transfer/check")
    quantity: Mapped[float] = mapped_column(Float, nullable=False, comment="变动数量(正入库/负出库)")
    before_quantity: Mapped[float] = mapped_column(Float, default=0, comment="变动前数量")
    after_quantity: Mapped[float] = mapped_column(Float, default=0, comment="变动后数量")
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人ID")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    material: Mapped["Material"] = relationship(lazy="selectin")
    warehouse: Mapped["Warehouse"] = relationship(lazy="selectin")
    operator: Mapped["User"] = relationship(lazy="selectin")


class StockInOrder(Base):
    """入库单"""
    __tablename__ = "stock_in_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="入库单号")
    order_type: Mapped[str] = mapped_column(String(20), default="purchase", comment="入库类型: purchase/produce/return")
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=True, comment="供应商ID")
    status: Mapped[str] = mapped_column(String(20), default="draft", comment="状态: draft/pending_approval/approved/done/cancelled")
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="申请人ID")
    approver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, comment="审批人ID")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    warehouse: Mapped["Warehouse"] = relationship(lazy="selectin")
    applicant: Mapped["User"] = relationship(foreign_keys=[applicant_id], lazy="selectin")
    approver: Mapped["User"] = relationship(foreign_keys=[approver_id], lazy="selectin")
    items: Mapped[list["StockInItem"]] = relationship(back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class StockInItem(Base):
    """入库单明细"""
    __tablename__ = "stock_in_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_in_orders.id", ondelete="CASCADE"), nullable=False, comment="入库单ID")
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("materials.id"), nullable=False, comment="物料ID")
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("storage_locations.id"), nullable=True, comment="库位ID")
    plan_quantity: Mapped[float] = mapped_column(Float, default=0, comment="计划数量")
    actual_quantity: Mapped[float] = mapped_column(Float, default=0, comment="实际数量")
    unit_price: Mapped[float] = mapped_column(Float, default=0, comment="单价")
    remark: Mapped[str] = mapped_column(String(200), default="", comment="备注")

    # 关系
    order: Mapped["StockInOrder"] = relationship(back_populates="items")
    material: Mapped["Material"] = relationship(lazy="selectin")
    location: Mapped["StorageLocation"] = relationship(lazy="selectin")


class StockOutOrder(Base):
    """出库单"""
    __tablename__ = "stock_out_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="出库单号")
    order_type: Mapped[str] = mapped_column(String(20), default="requisition", comment="出库类型: requisition/return_supplier/scrap")
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    department_id: Mapped[int] = mapped_column(Integer, nullable=True, comment="领用部门ID")
    status: Mapped[str] = mapped_column(String(20), default="draft", comment="状态: draft/pending_approval/approved/done/cancelled")
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="申请人ID")
    approver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, comment="审批人ID")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    warehouse: Mapped["Warehouse"] = relationship(lazy="selectin")
    applicant: Mapped["User"] = relationship(foreign_keys=[applicant_id], lazy="selectin")
    approver: Mapped["User"] = relationship(foreign_keys=[approver_id], lazy="selectin")
    items: Mapped[list["StockOutItem"]] = relationship(back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class StockOutItem(Base):
    """出库单明细"""
    __tablename__ = "stock_out_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_out_orders.id", ondelete="CASCADE"), nullable=False, comment="出库单ID")
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("materials.id"), nullable=False, comment="物料ID")
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("storage_locations.id"), nullable=True, comment="库位ID")
    plan_quantity: Mapped[float] = mapped_column(Float, default=0, comment="计划数量")
    actual_quantity: Mapped[float] = mapped_column(Float, default=0, comment="实际数量")
    unit_price: Mapped[float] = mapped_column(Float, default=0, comment="单价")
    remark: Mapped[str] = mapped_column(String(200), default="", comment="备注")

    # 关系
    order: Mapped["StockOutOrder"] = relationship(back_populates="items")
    material: Mapped["Material"] = relationship(lazy="selectin")
    location: Mapped["StorageLocation"] = relationship(lazy="selectin")
