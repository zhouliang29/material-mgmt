"""模型汇总导入 - 确保所有模型被注册到 Base.metadata"""
from app.models.user import User
from app.models.role import Role, Permission, UserRole, RolePermission
from app.models.material import Material, MaterialCategory
from app.models.warehouse import Warehouse, StorageLocation
from app.models.inventory import (
    Inventory, InventoryTransaction,
    StockInOrder, StockInItem,
    StockOutOrder, StockOutItem,
)
from app.models.supplier import Supplier
from app.models.department import Department

__all__ = [
    "User", "Role", "Permission", "UserRole", "RolePermission",
    "Material", "MaterialCategory",
    "Warehouse", "StorageLocation",
    "Inventory", "InventoryTransaction",
    "StockInOrder", "StockInItem",
    "StockOutOrder", "StockOutItem",
    "Supplier", "Department",
]
