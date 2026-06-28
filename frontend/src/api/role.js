import request from '../utils/request'

// 角色列表
export function getRoleList(params) {
  return request.get('/roles', { params })
}

// 所有角色（下拉）
export function getAllRoles() {
  return request.get('/roles/all')
}

// 创建角色
export function createRole(data) {
  return request.post('/roles', data)
}

// 更新角色
export function updateRole(id, data) {
  return request.put(`/roles/${id}`, data)
}

// 删除角色
export function deleteRole(id) {
  return request.delete(`/roles/${id}`)
}

// 角色分配权限
export function assignRolePermissions(roleId, permissionIds) {
  return request.post(`/roles/${roleId}/permissions`, { permission_ids: permissionIds })
}

// 权限列表
export function getPermissionList() {
  return request.get('/roles/permissions')
}
