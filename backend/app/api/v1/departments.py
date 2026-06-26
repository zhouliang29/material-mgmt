"""部门管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.department import Department
from app.schemas.common import ResponseBase, PageResult
from app.models.user import User
from app.core.deps import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/departments", tags=["部门管理"])


# ========== Schema ==========

class DepartmentCreate(BaseModel):
    parent_id: Optional[int] = None
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    manager: str = Field(default="", max_length=50)
    remark: str = ""


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    manager: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentOut(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    code: str
    manager: str
    remark: str
    is_active: bool

    class Config:
        from_attributes = True


class DepartmentTree(DepartmentOut):
    children: list["DepartmentTree"] = []


# ========== API ==========

@router.get("/tree", response_model=list[DepartmentTree], summary="部门树")
def department_tree(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    departments = db.query(Department).filter(Department.is_active == True).all()
    id_map = {}
    roots = []
    for d in departments:
        node = DepartmentTree.model_validate(d)
        node.children = []
        id_map[d.id] = node
    for d in departments:
        if d.parent_id and d.parent_id in id_map:
            id_map[d.parent_id].children.append(id_map[d.id])
        else:
            roots.append(id_map[d.id])
    return roots


@router.get("/all", response_model=list[DepartmentOut], summary="所有部门(下拉)")
def list_all_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Department).filter(Department.is_active == True).all()


@router.get("", response_model=PageResult, summary="部门列表")
def list_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Department)
    if keyword:
        query = query.filter(
            (Department.name.contains(keyword)) | (Department.code.contains(keyword))
        )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(
        total=total, page=page, page_size=page_size,
        items=[DepartmentOut.model_validate(d).model_dump() for d in items],
    )


@router.post("", response_model=DepartmentOut, summary="创建部门")
def create_department(body: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Department).filter(Department.code == body.code).first():
        raise HTTPException(status_code=400, detail="部门编码已存在")
    dept = Department(**body.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{dept_id}", response_model=DepartmentOut, summary="更新部门")
def update_department(dept_id: int, body: DepartmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(dept, k, v)
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}", response_model=ResponseBase, summary="删除部门")
def delete_department(dept_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    dept.is_active = False
    db.commit()
    return ResponseBase(message="部门已禁用")
