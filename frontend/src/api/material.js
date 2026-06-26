import request from '../utils/request'

// 物料列表
export function getMaterialList(params) {
  return request.get('/materials', { params })
}

// 物料详情
export function getMaterial(id) {
  return request.get(`/materials/${id}`)
}

// 创建物料
export function createMaterial(data) {
  return request.post('/materials', data)
}

// 更新物料
export function updateMaterial(id, data) {
  return request.put(`/materials/${id}`, data)
}

// 删除物料
export function deleteMaterial(id) {
  return request.delete(`/materials/${id}`)
}

// 分类树
export function getCategoryTree() {
  return request.get('/materials/categories/tree')
}

// 创建分类
export function createCategory(data) {
  return request.post('/materials/categories', data)
}

// 更新分类
export function updateCategory(id, data) {
  return request.put(`/materials/categories/${id}`, data)
}

// 删除分类
export function deleteCategory(id) {
  return request.delete(`/materials/categories/${id}`)
}
