"""物料模型"""
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class MaterialCategory(Base):
    """物料分类（树状结构）"""
    __tablename__ = "material_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_categories.id"), default=None, nullable=True, comment="父分类ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分类名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类编码")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    parent: Mapped["MaterialCategory"] = relationship(remote_side="MaterialCategory.id", lazy="selectin")
    materials: Mapped[list["Material"]] = relationship(back_populates="category", lazy="selectin")


class Material(Base):
    """物料主数据"""
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="物料编码")
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True, comment="物料名称")
    spec: Mapped[str] = mapped_column(String(200), default="", comment="规格型号")
    model: Mapped[str] = mapped_column(String(100), default="", comment="型号")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_categories.id"), nullable=True, comment="分类ID")
    unit: Mapped[str] = mapped_column(String(20), default="个", comment="计量单位")
    safety_stock: Mapped[float] = mapped_column(Float, default=0, comment="安全库存")
    max_stock: Mapped[float] = mapped_column(Float, default=0, comment="最大库存")
    price: Mapped[float] = mapped_column(Float, default=0, comment="参考单价")
    image_url: Mapped[str] = mapped_column(String(500), default="", comment="图片地址")
    remark: Mapped[str] = mapped_column(Text, default="", comment="备注")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    category: Mapped["MaterialCategory"] = relationship(back_populates="materials")
