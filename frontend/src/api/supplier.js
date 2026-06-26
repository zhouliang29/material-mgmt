import request from '../utils/request'

// 供应商列表
export function getSupplierList(params) {
  return request.get('/suppliers', { params })
}

// 所有供应商（下拉）
export function getAllSuppliers() {
  return request.get('/suppliers/all')
}

// 创建供应商
export function createSupplier(data) {
  return request.post('/suppliers', data)
}

// 更新供应商
export function updateSupplier(id, data) {
  return request.put(`/suppliers/${id}`, data)
}

// 删除供应商
export function deleteSupplier(id) {
  return request.delete(`/suppliers/${id}`)
}
