"""用户管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.schemas.common import ResponseBase, PageResult
from app.core.deps import get_current_user, require_permission

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=PageResult, summary="用户列表")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user:list")),
):
    query = db.query(User)
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) | (User.real_name.contains(keyword))
        )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(
        total=total, page=page, page_size=page_size,
        items=[UserOut.model_validate(u).model_dump() for u in items],
    )


@router.get("/{user_id}", response_model=UserOut, summary="用户详情")
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("user:view"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserOut, summary="更新用户")
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("user:edit"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    update_data = body.model_dump(exclude_unset=True, exclude={"role_ids"})
    for k, v in update_data.items():
        setattr(user, k, v)
    if body.role_ids is not None:
        user.roles = db.query(Role).filter(Role.id.in_(body.role_ids)).all()
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=ResponseBase, summary="删除用户")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("user:delete"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = False
    db.commit()
    return ResponseBase(message="用户已禁用")
