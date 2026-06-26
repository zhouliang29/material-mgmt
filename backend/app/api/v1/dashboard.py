"""仪表盘统计 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.user import User
from app.models.material import Material, MaterialCategory
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory, StockInOrder, StockOutOrder
from app.models.supplier import Supplier
from app.models.role import Role
from app.core.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats", summary="仪表盘统计数据")
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取仪表盘统计数据"""
    # 物料统计
    material_count = db.query(func.count(Material.id)).filter(Material.is_active == True).scalar()
    category_count = db.query(func.count(MaterialCategory.id)).filter(MaterialCategory.is_active == True).scalar()

    # 仓库统计
    warehouse_count = db.query(func.count(Warehouse.id)).filter(Warehouse.is_active == True).scalar()

    # 供应商统计
    supplier_count = db.query(func.count(Supplier.id)).filter(Supplier.is_active == True).scalar()

    # 用户统计
    user_count = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

    # 库存统计
    total_stock_value = db.query(func.coalesce(func.sum(Inventory.quantity * Inventory.safety_stock), 0)).scalar()
    low_stock_count = db.query(func.count(Inventory.id)).filter(
        Inventory.quantity <= Inventory.safety_stock,
        Inventory.safety_stock > 0,
    ).scalar()

    # 出入库统计
    pending_stock_in = db.query(func.count(StockInOrder.id)).filter(
        StockInOrder.status.in_(["draft", "pending_approval"])
    ).scalar()
    pending_stock_out = db.query(func.count(StockOutOrder.id)).filter(
        StockOutOrder.status.in_(["draft", "pending_approval"])
    ).scalar()
    today_stock_in = db.query(func.count(StockInOrder.id)).filter(
        StockInOrder.status == "done"
    ).scalar()
    today_stock_out = db.query(func.count(StockOutOrder.id)).filter(
        StockOutOrder.status == "done"
    ).scalar()

    # 低库存物料列表（取前10）
    low_stock_items = db.query(Inventory).filter(
        Inventory.quantity <= Inventory.safety_stock,
        Inventory.safety_stock > 0,
    ).limit(10).all()
    low_stock_list = []
    for inv in low_stock_items:
        low_stock_list.append({
            "id": inv.id,
            "material_id": inv.material_id,
            "material_code": inv.material.code if inv.material else None,
            "material_name": inv.material.name if inv.material else None,
            "quantity": inv.quantity,
            "safety_stock": inv.safety_stock,
            "warehouse_name": inv.warehouse.name if inv.warehouse else None,
        })

    return {
        "material_count": material_count,
        "category_count": category_count,
        "warehouse_count": warehouse_count,
        "supplier_count": supplier_count,
        "user_count": user_count,
        "low_stock_count": low_stock_count,
        "pending_stock_in": pending_stock_in,
        "pending_stock_out": pending_stock_out,
        "today_stock_in": today_stock_in,
        "today_stock_out": today_stock_out,
        "low_stock_items": low_stock_list,
    }
