import request from '../utils/request'

// 仓库列表
export function getWarehouseList(params) {
  return request.get('/warehouses', { params })
}

// 所有仓库（下拉）
export function getAllWarehouses() {
  return request.get('/warehouses/all')
}

// 创建仓库
export function createWarehouse(data) {
  return request.post('/warehouses', data)
}

// 更新仓库
export function updateWarehouse(id, data) {
  return request.put(`/warehouses/${id}`, data)
}

// 删除仓库
export function deleteWarehouse(id) {
  return request.delete(`/warehouses/${id}`)
}

// 库位列表
export function getLocationList(warehouseId) {
  return request.get(`/warehouses/${warehouseId}/locations`)
}

// 创建库位
export function createLocation(data) {
  return request.post('/warehouses/locations', data)
}

// 删除库位
export function deleteLocation(id) {
  return request.delete(`/warehouses/locations/${id}`)
}
