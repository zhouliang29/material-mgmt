"""供应商管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from app.schemas.common import ResponseBase, PageResult
from app.models.user import User
from app.core.deps import get_current_user, require_permission

router = APIRouter(prefix="/suppliers", tags=["供应商管理"])


@router.get("", response_model=PageResult, summary="供应商列表")
def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Supplier)
    if keyword:
        query = query.filter(
            (Supplier.name.contains(keyword)) | (Supplier.code.contains(keyword))
        )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(
        total=total, page=page, page_size=page_size,
        items=[SupplierOut.model_validate(s).model_dump() for s in items],
    )


@router.get("/all", response_model=list[SupplierOut], summary="所有供应商(下拉)")
def list_all_suppliers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Supplier).filter(Supplier.is_active == True).all()


@router.get("/{supplier_id}", response_model=SupplierOut, summary="供应商详情")
def get_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier


@router.post("", response_model=SupplierOut, summary="创建供应商")
def create_supplier(body: SupplierCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("supplier:add"))):
    if db.query(Supplier).filter(Supplier.code == body.code).first():
        raise HTTPException(status_code=400, detail="供应商编码已存在")
    supplier = Supplier(**body.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierOut, summary="更新供应商")
def update_supplier(supplier_id: int, body: SupplierUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("supplier:edit"))):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(supplier, k, v)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", response_model=ResponseBase, summary="删除供应商")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("supplier:delete"))):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    supplier.is_active = False
    db.commit()
    return ResponseBase(message="供应商已禁用")
