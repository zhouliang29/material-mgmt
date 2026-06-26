"""物料管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.material import Material, MaterialCategory
from app.schemas.material import (
    MaterialCreate, MaterialUpdate, MaterialOut, MaterialListParams,
    CategoryCreate, CategoryUpdate, CategoryOut, CategoryTree,
)
from app.schemas.common import ResponseBase, PageResult
from app.models.user import User
from app.core.deps import get_current_user, require_permission

router = APIRouter(prefix="/materials", tags=["物料管理"])


# ========== 物料分类 ==========

@router.get("/categories/tree", response_model=list[CategoryTree], summary="分类树")
def category_tree(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(MaterialCategory).filter(MaterialCategory.is_active == True).all()
    id_map = {}
    roots = []
    for c in categories:
        node = CategoryTree.model_validate(c)
        node.children = []
        id_map[c.id] = node
    for c in categories:
        if c.parent_id and c.parent_id in id_map:
            id_map[c.parent_id].children.append(id_map[c.id])
        else:
            roots.append(id_map[c.id])
    return roots


@router.post("/categories", response_model=CategoryOut, summary="创建分类")
def create_category(body: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("material:category:add"))):
    if db.query(MaterialCategory).filter(MaterialCategory.code == body.code).first():
        raise HTTPException(status_code=400, detail="分类编码已存在")
    category = MaterialCategory(**body.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryOut, summary="更新分类")
def update_category(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("material:category:edit"))):
    category = db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(category, k, v)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", response_model=ResponseBase, summary="删除分类")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("material:category:delete"))):
    category = db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    if db.query(Material).filter(Material.category_id == category_id).count() > 0:
        raise HTTPException(status_code=400, detail="分类下存在物料，无法删除")
    category.is_active = False
    db.commit()
    return ResponseBase(message="分类已禁用")


# ========== 物料主数据 ==========

@router.get("", response_model=PageResult, summary="物料列表")
def list_materials(params: MaterialListParams = Depends(), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Material)
    if params.keyword:
        query = query.filter(
            (Material.code.contains(params.keyword)) |
            (Material.name.contains(params.keyword)) |
            (Material.spec.contains(params.keyword))
        )
    if params.category_id is not None:
        query = query.filter(Material.category_id == params.category_id)
    if params.is_active is not None:
        query = query.filter(Material.is_active == params.is_active)
    total = query.count()
    items = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    result = []
    for m in items:
        d = MaterialOut.model_validate(m).model_dump()
        d["category_name"] = m.category.name if m.category else None
        result.append(d)
    return PageResult(total=total, page=params.page, page_size=params.page_size, items=result)


@router.get("/{material_id}", response_model=MaterialOut, summary="物料详情")
def get_material(material_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")
    result = MaterialOut.model_validate(material).model_dump()
    result["category_name"] = material.category.name if material.category else None
    return result


@router.post("", response_model=MaterialOut, summary="创建物料")
def create_material(body: MaterialCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("material:add"))):
    if db.query(Material).filter(Material.code == body.code).first():
        raise HTTPException(status_code=400, detail="物料编码已存在")
    material = Material(**body.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.put("/{material_id}", response_model=MaterialOut, summary="更新物料")
def update_material(material_id: int, body: MaterialUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("material:edit"))):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(material, k, v)
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{material_id}", response_model=ResponseBase, summary="删除物料")
def delete_material(material_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("material:delete"))):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")
    material.is_active = False
    db.commit()
    return ResponseBase(message="物料已禁用")
