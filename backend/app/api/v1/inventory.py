"""出入库和库存 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.inventory import Inventory, InventoryTransaction, StockInOrder, StockOutOrder
from app.schemas.inventory import (
    InventoryQuery, InventoryOut,
    StockInOrderCreate, StockInOrderUpdate, StockInOrderOut,
    StockOutOrderCreate, StockOutOrderUpdate, StockOutOrderOut,
)
from app.schemas.common import ResponseBase, PageResult
from app.models.user import User
from app.core.deps import get_current_user, require_permission
from app.services.inventory_service import (
    create_stock_in_order, execute_stock_in,
    create_stock_out_order, execute_stock_out,
    approve_order, submit_for_approval,
)

router = APIRouter(prefix="/inventory", tags=["库存管理"])


# ========== 库存查询 ==========

@router.get("", response_model=PageResult, summary="库存列表")
def list_inventory(
    query: InventoryQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Inventory)
    if query.warehouse_id:
        q = q.filter(Inventory.warehouse_id == query.warehouse_id)
    if query.material_id:
        q = q.filter(Inventory.material_id == query.material_id)
    if query.low_stock:
        q = q.filter(Inventory.quantity <= Inventory.safety_stock)

    total = q.count()
    items = q.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    result = []
    for inv in items:
        d = InventoryOut.model_validate(inv).model_dump()
        d["available_quantity"] = inv.available_quantity
        d["material_code"] = inv.material.code if inv.material else None
        d["material_name"] = inv.material.name if inv.material else None
        d["material_spec"] = inv.material.spec if inv.material else None
        d["material_unit"] = inv.material.unit if inv.material else None
        d["warehouse_name"] = inv.warehouse.name if inv.warehouse else None
        d["location_code"] = inv.location.code if inv.location else None
        result.append(d)
    return PageResult(total=total, page=query.page, page_size=query.page_size, items=result)


# ========== 入库单 ==========

@router.get("/stock-in", response_model=PageResult, summary="入库单列表")
def list_stock_in_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(StockInOrder)
    if status:
        q = q.filter(StockInOrder.status == status)
    total = q.count()
    items = q.order_by(StockInOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(
        total=total, page=page, page_size=page_size,
        items=[StockInOrderOut.model_validate(o).model_dump() for o in items],
    )


@router.post("/stock-in", response_model=StockInOrderOut, summary="创建入库单")
def create_stock_in(body: StockInOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_in:add"))):
    return create_stock_in_order(db, body, current_user.id)


@router.get("/stock-in/{order_id}", response_model=StockInOrderOut, summary="入库单详情")
def get_stock_in(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(StockInOrder).filter(StockInOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="入库单不存在")
    return order


@router.put("/stock-in/{order_id}", response_model=StockInOrderOut, summary="更新入库单(仅草稿)")
def update_stock_in(order_id: int, body: StockInOrderUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_in:edit"))):
    order = db.query(StockInOrder).filter(StockInOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="入库单不存在")
    if order.status != "draft":
        raise HTTPException(status_code=400, detail="只有草稿状态可修改")
    update_data = body.model_dump(exclude_unset=True, exclude={"items"})
    for k, v in update_data.items():
        setattr(order, k, v)
    if body.items is not None:
        # 删旧增新
        for old_item in order.items:
            db.delete(old_item)
        for item_data in body.items:
            item = StockInItem(order_id=order.id, **item_data.model_dump())
            db.add(item)
    db.commit()
    db.refresh(order)
    return order


@router.post("/stock-in/{order_id}/submit", response_model=StockInOrderOut, summary="提交入库单审批")
def submit_stock_in(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_in:submit"))):
    return submit_for_approval(db, "stock_in", order_id)


@router.post("/stock-in/{order_id}/approve", response_model=StockInOrderOut, summary="审批入库单")
def approve_stock_in(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_in:approve"))):
    return approve_order(db, "stock_in", order_id, current_user.id)


@router.post("/stock-in/{order_id}/execute", response_model=StockInOrderOut, summary="执行入库")
def execute_stock_in_api(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_in:execute"))):
    return execute_stock_in(db, order_id, current_user.id)


# ========== 出库单 ==========

@router.get("/stock-out", response_model=PageResult, summary="出库单列表")
def list_stock_out_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(StockOutOrder)
    if status:
        q = q.filter(StockOutOrder.status == status)
    total = q.count()
    items = q.order_by(StockOutOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(
        total=total, page=page, page_size=page_size,
        items=[StockOutOrderOut.model_validate(o).model_dump() for o in items],
    )


@router.post("/stock-out", response_model=StockOutOrderOut, summary="创建出库单")
def create_stock_out(body: StockOutOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_out:add"))):
    return create_stock_out_order(db, body, current_user.id)


@router.get("/stock-out/{order_id}", response_model=StockOutOrderOut, summary="出库单详情")
def get_stock_out(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(StockOutOrder).filter(StockOutOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="出库单不存在")
    return order


@router.put("/stock-out/{order_id}", response_model=StockOutOrderOut, summary="更新出库单(仅草稿)")
def update_stock_out(order_id: int, body: StockOutOrderUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_out:edit"))):
    order = db.query(StockOutOrder).filter(StockOutOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="出库单不存在")
    if order.status != "draft":
        raise HTTPException(status_code=400, detail="只有草稿状态可修改")
    update_data = body.model_dump(exclude_unset=True, exclude={"items"})
    for k, v in update_data.items():
        setattr(order, k, v)
    if body.items is not None:
        for old_item in order.items:
            db.delete(old_item)
        for item_data in body.items:
            item = StockOutItem(order_id=order.id, **item_data.model_dump())
            db.add(item)
    db.commit()
    db.refresh(order)
    return order


@router.post("/stock-out/{order_id}/submit", response_model=StockOutOrderOut, summary="提交出库单审批")
def submit_stock_out(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_out:submit"))):
    return submit_for_approval(db, "stock_out", order_id)


@router.post("/stock-out/{order_id}/approve", response_model=StockOutOrderOut, summary="审批出库单")
def approve_stock_out(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_out:approve"))):
    return approve_order(db, "stock_out", order_id, current_user.id)


@router.post("/stock-out/{order_id}/execute", response_model=StockOutOrderOut, summary="执行出库")
def execute_stock_out_api(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("stock_out:execute"))):
    return execute_stock_out(db, order_id, current_user.id)


# ========== 库存流水 ==========

@router.get("/transactions", response_model=PageResult, summary="库存流水")
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    material_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    order_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(InventoryTransaction)
    if material_id:
        q = q.filter(InventoryTransaction.material_id == material_id)
    if warehouse_id:
        q = q.filter(InventoryTransaction.warehouse_id == warehouse_id)
    if order_type:
        q = q.filter(InventoryTransaction.order_type == order_type)
    total = q.count()
    items = q.order_by(InventoryTransaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(
        total=total, page=page, page_size=page_size,
        items=[{
            "id": t.id,
            "material_id": t.material_id,
            "material_name": t.material.name if t.material else None,
            "material_code": t.material.code if t.material else None,
            "warehouse_id": t.warehouse_id,
            "warehouse_name": t.warehouse.name if t.warehouse else None,
            "order_id": t.order_id,
            "order_type": t.order_type,
            "quantity": t.quantity,
            "before_quantity": t.before_quantity,
            "after_quantity": t.after_quantity,
            "operator_id": t.operator_id,
            "remark": t.remark,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        } for t in items],
    )
