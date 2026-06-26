import request from '../utils/request'

// 部门列表
export function getDepartmentList(params) {
  return request.get('/departments', { params })
}

// 所有部门（下拉）
export function getAllDepartments() {
  return request.get('/departments/all')
}

// 部门树
export function getDepartmentTree() {
  return request.get('/departments/tree')
}

// 创建部门
export function createDepartment(data) {
  return request.post('/departments', data)
}

// 更新部门
export function updateDepartment(id, data) {
  return request.put(`/departments/${id}`, data)
}

// 删除部门
export function deleteDepartment(id) {
  return request.delete(`/departments/${id}`)
}
