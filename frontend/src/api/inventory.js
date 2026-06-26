import request from '../utils/request'

// 库存列表
export function getInventoryList(params) {
  return request.get('/inventory', { params })
}

// 入库单列表
export function getStockInList(params) {
  return request.get('/inventory/stock-in', { params })
}

// 创建入库单
export function createStockIn(data) {
  return request.post('/inventory/stock-in', data)
}

// 入库单详情
export function getStockInDetail(id) {
  return request.get(`/inventory/stock-in/${id}`)
}

// 更新入库单
export function updateStockIn(id, data) {
  return request.put(`/inventory/stock-in/${id}`, data)
}

// 提交入库审批
export function submitStockIn(id) {
  return request.post(`/inventory/stock-in/${id}/submit`)
}

// 审批入库单
export function approveStockIn(id) {
  return request.post(`/inventory/stock-in/${id}/approve`)
}

// 执行入库
export function executeStockIn(id) {
  return request.post(`/inventory/stock-in/${id}/execute`)
}

// 出库单列表
export function getStockOutList(params) {
  return request.get('/inventory/stock-out', { params })
}

// 创建出库单
export function createStockOut(data) {
  return request.post('/inventory/stock-out', data)
}

// 出库单详情
export function getStockOutDetail(id) {
  return request.get(`/inventory/stock-out/${id}`)
}

// 更新出库单
export function updateStockOut(id, data) {
  return request.put(`/inventory/stock-out/${id}`, data)
}

// 提交出库审批
export function submitStockOut(id) {
  return request.post(`/inventory/stock-out/${id}/submit`)
}

// 审批出库单
export function approveStockOut(id) {
  return request.post(`/inventory/stock-out/${id}/approve`)
}

// 执行出库
export function executeStockOut(id) {
  return request.post(`/inventory/stock-out/${id}/execute`)
}

// 库存流水
export function getTransactionList(params) {
  return request.get('/inventory/transactions', { params })
}
