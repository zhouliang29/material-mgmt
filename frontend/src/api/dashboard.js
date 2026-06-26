import request from '../utils/request'

// 仪表盘统计
export function getDashboardStats() {
  return request.get('/dashboard/stats')
}
