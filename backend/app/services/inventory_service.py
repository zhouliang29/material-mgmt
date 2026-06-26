"""库存和出入库服务层 - 核心业务逻辑"""
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.inventory import (
    Inventory, InventoryTransaction,
    StockInOrder, StockInItem,
    StockOutOrder, StockOutItem,
)
from app.models.material import Material
from app.models.warehouse import StorageLocation


def generate_order_no(prefix: str, db: Session) -> str:
    """生成单据编号: RK20240101001 / CK20240101001"""
    today = datetime.now().strftime("%Y%m%d")
    if prefix == "RK":
        count = db.query(StockInOrder).filter(StockInOrder.order_no.like(f"RK{today}%")).count()
    else:
        count = db.query(StockOutOrder).filter(StockOutOrder.order_no.like(f"CK{today}%")).count()
    return f"{prefix}{today}{count + 1:03d}"


# ========== 入库逻辑 ==========

def create_stock_in_order(db: Session, order_data, applicant_id: int) -> StockInOrder:
    """创建入库单"""
    order_no = generate_order_no("RK", db)
    order = StockInOrder(
        order_no=order_no,
        order_type=order_data.order_type,
        warehouse_id=order_data.warehouse_id,
        supplier_id=order_data.supplier_id,
        applicant_id=applicant_id,
        remark=order_data.remark,
        status="draft",
    )
    db.add(order)
    db.flush()  # 获取 order.id

    for item_data in order_data.items:
        item = StockInItem(
            order_id=order.id,
            material_id=item_data.material_id,
            location_id=item_data.location_id,
            plan_quantity=item_data.plan_quantity,
            actual_quantity=item_data.actual_quantity,
            unit_price=item_data.unit_price,
            remark=item_data.remark,
        )
        db.add(item)

    db.commit()
    db.refresh(order)
    return order


def execute_stock_in(db: Session, order_id: int, operator_id: int) -> StockInOrder:
    """执行入库 - 核心事务逻辑"""
    order = db.query(StockInOrder).filter(StockInOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="入库单不存在")
    if order.status != "approved":
        raise HTTPException(status_code=400, detail="入库单未审批，无法执行")

    for item in order.items:
        # 查找或创建库存记录
        inv = db.query(Inventory).filter(
            and_(
                Inventory.material_id == item.material_id,
                Inventory.warehouse_id == order.warehouse_id,
                Inventory.location_id == (item.location_id or None),
            )
        ).first()

        before_qty = inv.quantity if inv else 0
        add_qty = item.actual_quantity

        if inv:
            inv.quantity += add_qty
        else:
            inv = Inventory(
                material_id=item.material_id,
                warehouse_id=order.warehouse_id,
                location_id=item.location_id,
                quantity=add_qty,
                frozen_quantity=0,
            )
            db.add(inv)
            db.flush()

        # 写库存流水
        txn = InventoryTransaction(
            material_id=item.material_id,
            warehouse_id=order.warehouse_id,
            location_id=item.location_id,
            order_id=order.id,
            order_type="stock_in",
            quantity=add_qty,
            before_quantity=before_qty,
            after_quantity=before_qty + add_qty,
            operator_id=operator_id,
        )
        db.add(txn)

    order.status = "done"
    db.commit()
    db.refresh(order)
    return order


# ========== 出库逻辑 ==========

def create_stock_out_order(db: Session, order_data, applicant_id: int) -> StockOutOrder:
    """创建出库单"""
    order_no = generate_order_no("CK", db)
    order = StockOutOrder(
        order_no=order_no,
        order_type=order_data.order_type,
        warehouse_id=order_data.warehouse_id,
        department_id=order_data.department_id,
        applicant_id=applicant_id,
        remark=order_data.remark,
        status="draft",
    )
    db.add(order)
    db.flush()

    for item_data in order_data.items:
        item = StockOutItem(
            order_id=order.id,
            material_id=item_data.material_id,
            location_id=item_data.location_id,
            plan_quantity=item_data.plan_quantity,
            actual_quantity=item_data.actual_quantity,
            unit_price=item_data.unit_price,
            remark=item_data.remark,
        )
        db.add(item)

    db.commit()
    db.refresh(order)
    return order


def execute_stock_out(db: Session, order_id: int, operator_id: int) -> StockOutOrder:
    """执行出库 - 核心事务逻辑"""
    order = db.query(StockOutOrder).filter(StockOutOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="出库单不存在")
    if order.status != "approved":
        raise HTTPException(status_code=400, detail="出库单未审批，无法执行")

    for item in order.items:
        # 查找库存
        inv = db.query(Inventory).filter(
            and_(
                Inventory.material_id == item.material_id,
                Inventory.warehouse_id == order.warehouse_id,
                Inventory.location_id == (item.location_id or None),
            )
        ).first()

        if not inv:
            raise HTTPException(status_code=400, detail=f"物料ID={item.material_id} 无库存记录")

        out_qty = item.actual_quantity
        if inv.available_quantity < out_qty:
            raise HTTPException(
                status_code=400,
                detail=f"物料ID={item.material_id} 可用库存不足(可用:{inv.available_quantity}, 需要:{out_qty})",
            )

        before_qty = inv.quantity
        inv.quantity -= out_qty

        # 写库存流水
        txn = InventoryTransaction(
            material_id=item.material_id,
            warehouse_id=order.warehouse_id,
            location_id=item.location_id,
            order_id=order.id,
            order_type="stock_out",
            quantity=-out_qty,
            before_quantity=before_qty,
            after_quantity=before_qty - out_qty,
            operator_id=operator_id,
        )
        db.add(txn)

    order.status = "done"
    db.commit()
    db.refresh(order)
    return order


# ========== 审批逻辑 ==========

def approve_order(db: Session, order_type: str, order_id: int, approver_id: int):
    """审批单据"""
    if order_type == "stock_in":
        order = db.query(StockInOrder).filter(StockInOrder.id == order_id).first()
    else:
        order = db.query(StockOutOrder).filter(StockOutOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="单据不存在")
    if order.status != "pending_approval":
        raise HTTPException(status_code=400, detail="单据状态不是待审批")

    order.status = "approved"
    order.approver_id = approver_id
    db.commit()
    db.refresh(order)
    return order


def submit_for_approval(db: Session, order_type: str, order_id: int):
    """提交审批"""
    if order_type == "stock_in":
        order = db.query(StockInOrder).filter(StockInOrder.id == order_id).first()
    else:
        order = db.query(StockOutOrder).filter(StockOutOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="单据不存在")
    if order.status != "draft":
        raise HTTPException(status_code=400, detail="只有草稿状态可提交审批")

    order.status = "pending_approval"
    db.commit()
    db.refresh(order)
    return order
