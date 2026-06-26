"""FastAPI 主应用"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1 import auth, users, materials, warehouses, inventory, suppliers, dashboard, departments, roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭生命周期"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    # 初始化默认数据
    _init_default_data()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(materials.router, prefix="/api/v1")
app.include_router(warehouses.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(departments.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")


@app.get("/", tags=["健康检查"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


def _init_default_data():
    """初始化默认数据：管理员账号、基础角色、权限"""
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.models.role import Role, Permission

        # 检查是否已有管理员
        if not db.query(User).filter(User.username == "admin").first():
            from app.core.security import get_password_hash
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                real_name="系统管理员",
                is_superuser=True,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            import logging
            logging.info("Default admin created: admin / admin123")

        # 初始化角色
        if not db.query(Role).filter(Role.code == "admin").first():
            admin_role = Role(name="管理员", code="admin", description="系统管理员")
            db.add(admin_role)

        if not db.query(Role).filter(Role.code == "warehouse_keeper").first():
            keeper_role = Role(name="仓管员", code="warehouse_keeper", description="仓库管理员")
            db.add(keeper_role)

        if not db.query(Role).filter(Role.code == "applicant").first():
            applicant_role = Role(name="领用人", code="applicant", description="物料领用人")
            db.add(applicant_role)

        # 初始化权限
        default_permissions = [
            ("user:list", "用户列表", "用户管理"),
            ("user:view", "用户详情", "用户管理"),
            ("user:edit", "编辑用户", "用户管理"),
            ("user:delete", "删除用户", "用户管理"),
            ("material:add", "添加物料", "物料管理"),
            ("material:edit", "编辑物料", "物料管理"),
            ("material:delete", "删除物料", "物料管理"),
            ("material:category:add", "添加分类", "物料管理"),
            ("material:category:edit", "编辑分类", "物料管理"),
            ("material:category:delete", "删除分类", "物料管理"),
            ("warehouse:add", "添加仓库", "仓库管理"),
            ("warehouse:edit", "编辑仓库", "仓库管理"),
            ("warehouse:delete", "删除仓库", "仓库管理"),
            ("stock_in:add", "创建入库单", "入库管理"),
            ("stock_in:edit", "编辑入库单", "入库管理"),
            ("stock_in:submit", "提交入库审批", "入库管理"),
            ("stock_in:approve", "审批入库单", "入库管理"),
            ("stock_in:execute", "执行入库", "入库管理"),
            ("stock_out:add", "创建出库单", "出库管理"),
            ("stock_out:edit", "编辑出库单", "出库管理"),
            ("stock_out:submit", "提交出库审批", "出库管理"),
            ("stock_out:approve", "审批出库单", "出库管理"),
            ("stock_out:execute", "执行出库", "出库管理"),
            ("supplier:add", "添加供应商", "供应商管理"),
            ("supplier:edit", "编辑供应商", "供应商管理"),
            ("supplier:delete", "删除供应商", "供应商管理"),
        ]
        for code, name, module in default_permissions:
            if not db.query(Permission).filter(Permission.code == code).first():
                perm = Permission(name=name, code=code, module=module)
                db.add(perm)

        db.commit()
        import logging
        logging.info("Default roles and permissions initialized")

    except Exception as e:
        logging.warning(f"Init data failed: {e}")
    finally:
        db.close()
