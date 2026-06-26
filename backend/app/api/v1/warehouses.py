"""仓库/库位管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.warehouse import Warehouse, StorageLocation
from app.schemas.warehouse import (
    WarehouseCreate, WarehouseUpdate, WarehouseOut,
    LocationCreate, LocationUpdate, LocationOut,
)
from app.schemas.common import ResponseBase, PageResult
from app.models.user import User
from app.core.deps import get_current_user, require_permission

router = APIRouter(prefix="/warehouses", tags=["仓库管理"])


# ========== 仓库 ==========

@router.get("", response_model=PageResult, summary="仓库列表")
def list_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Warehouse)
    if keyword:
        query = query.filter(
            (Warehouse.name.contains(keyword)) | (Warehouse.code.contains(keyword))
        )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(
        total=total, page=page, page_size=page_size,
        items=[WarehouseOut.model_validate(w).model_dump() for w in items],
    )


@router.get("/all", response_model=list[WarehouseOut], summary="所有仓库(下拉)")
def list_all_warehouses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Warehouse).filter(Warehouse.is_active == True).all()


@router.post("", response_model=WarehouseOut, summary="创建仓库")
def create_warehouse(body: WarehouseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("warehouse:add"))):
    if db.query(Warehouse).filter(Warehouse.code == body.code).first():
        raise HTTPException(status_code=400, detail="仓库编码已存在")
    warehouse = Warehouse(**body.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseOut, summary="更新仓库")
def update_warehouse(warehouse_id: int, body: WarehouseUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("warehouse:edit"))):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(warehouse, k, v)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.delete("/{warehouse_id}", response_model=ResponseBase, summary="删除仓库")
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("warehouse:delete"))):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")
    warehouse.is_active = False
    db.commit()
    return ResponseBase(message="仓库已禁用")


# ========== 库位 ==========

@router.get("/{warehouse_id}/locations", response_model=list[LocationOut], summary="仓库下的库位列表")
def list_locations(warehouse_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(StorageLocation).filter(
        StorageLocation.warehouse_id == warehouse_id,
        StorageLocation.is_active == True,
    ).all()


@router.post("/locations", response_model=LocationOut, summary="创建库位")
def create_location(body: LocationCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("warehouse:add"))):
    if db.query(StorageLocation).filter(StorageLocation.code == body.code).first():
        raise HTTPException(status_code=400, detail="库位编码已存在")
    location = StorageLocation(**body.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.put("/locations/{location_id}", response_model=LocationOut, summary="更新库位")
def update_location(location_id: int, body: LocationUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("warehouse:edit"))):
    location = db.query(StorageLocation).filter(StorageLocation.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="库位不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(location, k, v)
    db.commit()
    db.refresh(location)
    return location


@router.delete("/locations/{location_id}", response_model=ResponseBase, summary="删除库位")
def delete_location(location_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("warehouse:delete"))):
    location = db.query(StorageLocation).filter(StorageLocation.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="库位不存在")
    location.is_active = False
    db.commit()
    return ResponseBase(message="库位已禁用")
