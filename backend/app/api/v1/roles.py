"""角色和权限管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.role import Role, Permission
from app.models.user import User
from app.core.deps import get_current_user, require_permission
from pydantic import BaseModel, Field

router = APIRouter(prefix="/roles", tags=["角色管理"])


# ========== Schema ==========

class RoleCreate(BaseModel):
    name: str = Field(..., max_length=50)
    code: str = Field(..., max_length=50)
    description: str = Field(default="", max_length=200)


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionOut(BaseModel):
    id: int
    name: str
    code: str
    module: str
    description: str

    class Config:
        from_attributes = True


class RoleOut(BaseModel):
    id: int
    name: str
    code: str
    description: str
    permissions: List[PermissionOut] = []

    class Config:
        from_attributes = True


class AssignPermissions(BaseModel):
    permission_ids: List[int] = []


# ========== 角色接口 ==========

@router.get("", summary="角色列表")
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Role)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [RoleOut.model_validate(r).model_dump() for r in items],
    }


@router.get("/all", summary="所有角色（下拉）")
def all_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    roles = db.query(Role).all()
    return [{"id": r.id, "name": r.name, "code": r.code} for r in roles]


@router.post("", summary="创建角色")
def create_role(body: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("user:edit"))):
    if db.query(Role).filter(Role.code == body.code).first():
        raise HTTPException(status_code=400, detail="角色编码已存在")
    role = Role(name=body.name, code=body.code, description=body.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleOut.model_validate(role).model_dump()


@router.put("/{role_id}", summary="更新角色")
def update_role(role_id: int, body: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("user:edit"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(role, k, v)
    db.commit()
    db.refresh(role)
    return RoleOut.model_validate(role).model_dump()


@router.delete("/{role_id}", summary="删除角色")
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("user:delete"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.code == "admin":
        raise HTTPException(status_code=400, detail="管理员角色不可删除")
    db.delete(role)
    db.commit()
    return {"code": 0, "message": "删除成功"}


@router.post("/{role_id}/permissions", summary="分配角色权限")
def assign_permissions(role_id: int, body: AssignPermissions, db: Session = Depends(get_db), current_user: User = Depends(require_permission("user:edit"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    permissions = db.query(Permission).filter(Permission.id.in_(body.permission_ids)).all()
    role.permissions = permissions
    db.commit()
    return {"code": 0, "message": "权限分配成功"}


# ========== 权限接口 ==========

@router.get("/permissions", summary="权限列表", tags=["权限管理"])
def list_permissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    perms = db.query(Permission).all()
    return [PermissionOut.model_validate(p).model_dump() for p in perms]
