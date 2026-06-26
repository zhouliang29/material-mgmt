# 物料管理系统（Material Management）

一套基于 **FastAPI + Vue 3** 的企业级物料管理系统，涵盖物料管理、仓库管理、库存管理、出入库审批、供应商管理、角色权限等核心功能。

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [后端部署](#后端部署)
  - [前端部署](#前端部署)
  - [生产部署](#生产部署)
- [默认账号](#默认账号)
- [API 接口](#api-接口)
- [配置说明](#配置说明)

---

## 功能特性

| 模块 | 功能 |
|------|------|
| **仪表盘** | 物料总数、仓库数量、供应商数、低库存预警、待处理出入库统计 |
| **物料管理** | 物料 CRUD、物料分类管理（树形结构） |
| **仓库管理** | 仓库 CRUD、库位管理 |
| **库存管理** | 库存查询、入库管理（创建/提交/审批/执行）、出库管理（创建/提交/审批/执行）、库存流水 |
| **供应商管理** | 供应商 CRUD |
| **系统管理** | 用户管理、角色权限分配、部门管理（树形结构） |
| **认证** | JWT 登录、修改密码、路由守卫 |

---

## 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** — 高性能异步 Web 框架
- **SQLAlchemy 2.0** — ORM（支持 SQLite / PostgreSQL）
- **Alembic** — 数据库迁移
- **python-jose** — JWT Token
- **bcrypt** — 密码哈希
- **Pydantic v2** — 数据校验

### 前端
- **Vue 3** — 组合式 API + `<script setup>`
- **Vite** — 构建工具
- **Element Plus** — UI 组件库
- **Vue Router** — 路由
- **Pinia** — 状态管理
- **Axios** — HTTP 请求

---

## 项目结构

```
material-mgmt/
├── backend/                        # 后端（FastAPI）
│   ├── app/
│   │   ├── api/v1/                 # API 路由
│   │   │   ├── auth.py             # 认证（登录/注册/修改密码）
│   │   │   ├── users.py            # 用户管理
│   │   │   ├── roles.py            # 角色权限
│   │   │   ├── departments.py      # 部门管理
│   │   │   ├── materials.py        # 物料管理
│   │   │   ├── warehouses.py       # 仓库管理
│   │   │   ├── inventory.py        # 出入库
│   │   │   ├── suppliers.py        # 供应商
│   │   │   └── dashboard.py        # 仪表盘统计
│   │   ├── core/                   # 核心配置
│   │   │   ├── config.py           # 应用配置（读取 .env）
│   │   │   ├── database.py         # 数据库连接
│   │   │   ├── security.py         # JWT / bcrypt
│   │   │   └── deps.py             # 依赖注入（认证/权限）
│   │   ├── models/                 # SQLAlchemy 模型
│   │   ├── schemas/                # Pydantic 请求/响应模型
│   │   ├── services/               # 业务逻辑层
│   │   └── main.py                 # 应用入口 + 初始化
│   ├── migrations/                 # Alembic 迁移
│   ├── .env.example                # 环境变量模板
│   ├── requirements.txt            # Python 依赖
│   └── run.py                      # 启动脚本
│
├── frontend/                       # 前端（Vue 3）
│   ├── src/
│   │   ├── api/                    # API 请求模块
│   │   ├── layout/                 # 布局组件（侧边栏+顶栏）
│   │   ├── router/                 # 路由配置
│   │   ├── stores/                 # Pinia 状态
│   │   ├── utils/                  # 工具函数（axios 封装）
│   │   ├── views/                  # 页面组件
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── material/           # 物料、分类
│   │   │   ├── warehouse/          # 仓库
│   │   │   ├── inventory/          # 库存/出入库/流水
│   │   │   ├── supplier/           # 供应商
│   │   │   └── system/             # 用户/角色/部门
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── vite.config.js              # Vite 配置（含开发代理）
│   └── package.json
│
└── README.md
```

---

## 快速开始

### 环境要求

| 工具 | 版本 |
|------|------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

### 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows 激活：
venv\Scripts\activate

# Linux/macOS 激活：
# source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
copy .env.example .env
# 编辑 .env 修改 SECRET_KEY 等配置（生产环境必须修改）

# 5. 启动后端（开发模式，自动重载）
python run.py

# 或直接使用 uvicorn：
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后访问：
- API 服务：http://localhost:8000
- API 文档（Swagger）：http://localhost:8000/docs
- API 文档（ReDoc）：http://localhost:8000/redoc

### 前端部署

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器（自动代理后端 API）
npm run dev

# 4. 构建生产版本
npm run build
```

启动成功后访问：http://localhost:5173

> 开发模式下，Vite 会将 `/api` 开头的请求自动代理到 `http://localhost:8000`，无需额外配置跨域。

### 生产部署

#### 方式一：前后端分离部署

```bash
# 1. 构建前端
cd frontend && npm run build

# 2. 将 frontend/dist 目录部署到 Nginx
# Nginx 配置示例：
# server {
#     listen 80;
#     server_name your-domain.com;
#
#     # 前端静态文件
#     location / {
#         root /path/to/frontend/dist;
#         try_files $uri $uri/ /index.html;
#     }
#
#     # 后端 API 代理
#     location /api/ {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
# }

# 3. 启动后端（生产模式）
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 方式二：FastAPI 托管前端静态文件

在 `main.py` 中添加静态文件挂载：

```python
from fastapi.staticfiles import StaticFiles

# 在所有路由注册之后添加：
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
```

#### 切换 PostgreSQL（可选）

默认使用 SQLite，生产环境建议使用 PostgreSQL：

1. 安装驱动：`pip install psycopg2-binary`
2. 修改 `.env`：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/material_mgmt
```

3. 执行数据库迁移：

```bash
cd backend
alembic upgrade head
```

---

## 默认账号

首次启动时系统自动初始化以下数据：

| 类型 | 名称 | 说明 |
|------|------|------|
| 管理员账号 | `admin` / `admin123` | 超级管理员，拥有所有权限 |
| 角色 | 管理员（admin） | 系统管理员角色 |
| 角色 | 仓管员（warehouse_keeper） | 仓库管理员角色 |
| 角色 | 领用人（applicant） | 物料领用人角色 |
| 权限 | 26 项 | 覆盖用户、物料、仓库、出入库、供应商管理 |

> ⚠️ 生产环境请务必修改默认管理员密码！

---

## API 接口

所有接口前缀：`/api/v1`

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/register` | 用户注册 |
| GET | `/auth/me` | 获取当前用户信息 |
| PUT | `/auth/password` | 修改密码 |

### 用户管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/users` | 用户列表（分页） |
| POST | `/users` | 创建用户 |
| GET | `/users/{id}` | 用户详情 |
| PUT | `/users/{id}` | 更新用户 |
| DELETE | `/users/{id}` | 删除用户 |

### 角色 & 权限
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/roles` | 角色列表 |
| GET | `/roles/all` | 所有角色（下拉） |
| POST | `/roles` | 创建角色 |
| PUT | `/roles/{id}` | 更新角色 |
| DELETE | `/roles/{id}` | 删除角色 |
| POST | `/roles/{id}/permissions` | 分配角色权限 |
| GET | `/roles/permissions` | 权限列表 |

### 部门管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/departments` | 部门列表 |
| GET | `/departments/tree` | 部门树 |
| GET | `/departments/all` | 所有部门（下拉） |
| POST | `/departments` | 创建部门 |
| PUT | `/departments/{id}` | 更新部门 |
| DELETE | `/departments/{id}` | 删除部门 |

### 物料管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/materials` | 物料列表（分页） |
| POST | `/materials` | 创建物料 |
| GET | `/materials/{id}` | 物料详情 |
| PUT | `/materials/{id}` | 更新物料 |
| DELETE | `/materials/{id}` | 删除物料 |
| GET | `/material-categories` | 分类列表 |
| POST | `/material-categories` | 创建分类 |
| PUT | `/material-categories/{id}` | 更新分类 |
| DELETE | `/material-categories/{id}` | 删除分类 |

### 仓库管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/warehouses` | 仓库列表 |
| POST | `/warehouses` | 创建仓库 |
| PUT | `/warehouses/{id}` | 更新仓库 |
| DELETE | `/warehouses/{id}` | 删除仓库 |
| GET | `/warehouses/{id}/locations` | 库位列表 |
| POST | `/warehouses/{id}/locations` | 创建库位 |

### 库存 & 出入库
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/inventory` | 库存列表 |
| GET | `/stock-in` | 入库单列表 |
| POST | `/stock-in` | 创建入库单 |
| GET | `/stock-in/{id}` | 入库单详情 |
| POST | `/stock-in/{id}/submit` | 提交入库审批 |
| POST | `/stock-in/{id}/approve` | 审批入库单 |
| POST | `/stock-in/{id}/execute` | 执行入库 |
| GET | `/stock-out` | 出库单列表 |
| POST | `/stock-out` | 创建出库单 |
| GET | `/stock-out/{id}` | 出库单详情 |
| POST | `/stock-out/{id}/submit` | 提交出库审批 |
| POST | `/stock-out/{id}/approve` | 审批出库单 |
| POST | `/stock-out/{id}/execute` | 执行出库 |
| GET | `/inventory-transactions` | 库存流水 |

### 供应商管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/suppliers` | 供应商列表 |
| POST | `/suppliers` | 创建供应商 |
| PUT | `/suppliers/{id}` | 更新供应商 |
| DELETE | `/suppliers/{id}` | 删除供应商 |

### 仪表盘
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dashboard/stats` | 统计数据 |

---

## 配置说明

后端配置通过 `.env` 文件管理（参考 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` | 物料管理系统 | 应用名称 |
| `APP_VERSION` | 1.0.0 | 版本号 |
| `DEBUG` | True | 调试模式 |
| `DATABASE_URL` | sqlite:///./material.db | 数据库连接 |
| `SECRET_KEY` | change-this-to-... | JWT 签名密钥（**生产环境必须修改**） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 | Token 有效期（分钟） |
| `CORS_ORIGINS` | ["http://localhost:5173",...] | 允许的跨域来源 |

前端开发代理配置在 `frontend/vite.config.js`：

```js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```
