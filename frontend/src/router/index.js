import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', noAuth: true },
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页' },
      },
      // 物料管理
      {
        path: 'material',
        name: 'MaterialList',
        component: () => import('../views/material/MaterialList.vue'),
        meta: { title: '物料列表' },
      },
      {
        path: 'material/category',
        name: 'MaterialCategory',
        component: () => import('../views/material/CategoryList.vue'),
        meta: { title: '物料分类' },
      },
      // 仓库管理
      {
        path: 'warehouse',
        name: 'WarehouseList',
        component: () => import('../views/warehouse/WarehouseList.vue'),
        meta: { title: '仓库管理' },
      },
      // 入库管理
      {
        path: 'stock-in',
        name: 'StockInList',
        component: () => import('../views/inventory/StockInList.vue'),
        meta: { title: '入库管理' },
      },
      // 出库管理
      {
        path: 'stock-out',
        name: 'StockOutList',
        component: () => import('../views/inventory/StockOutList.vue'),
        meta: { title: '出库管理' },
      },
      // 库存查询
      {
        path: 'inventory',
        name: 'InventoryList',
        component: () => import('../views/inventory/InventoryList.vue'),
        meta: { title: '库存查询' },
      },
      // 库存流水
      {
        path: 'transactions',
        name: 'TransactionList',
        component: () => import('../views/inventory/TransactionList.vue'),
        meta: { title: '库存流水' },
      },
      // 供应商管理
      {
        path: 'supplier',
        name: 'SupplierList',
        component: () => import('../views/supplier/SupplierList.vue'),
        meta: { title: '供应商管理' },
      },
      // 系统管理
      {
        path: 'system/users',
        name: 'UserList',
        component: () => import('../views/system/UserList.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'system/roles',
        name: 'RoleList',
        component: () => import('../views/system/RoleList.vue'),
        meta: { title: '角色权限' },
      },
      {
        path: 'system/departments',
        name: 'DepartmentList',
        component: () => import('../views/system/DepartmentList.vue'),
        meta: { title: '部门管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '物料管理系统'} - 物料管理`
  const token = localStorage.getItem('token')
  if (!to.meta.noAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
