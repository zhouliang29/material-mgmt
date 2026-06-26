<template>
  <div class="page-container">
    <div class="page-header">
      <h3>首页概览</h3>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 24px">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.material_count || 0 }}</div>
          <div class="stat-label">物料总数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.warehouse_count || 0 }}</div>
          <div class="stat-label">仓库数量</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.supplier_count || 0 }}</div>
          <div class="stat-label">供应商数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #e6a23c">{{ stats.low_stock_count || 0 }}</div>
          <div class="stat-label">低库存预警</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #67c23a">{{ stats.pending_stock_in || 0 }}</div>
          <div class="stat-label">待处理入库</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #f56c6c">{{ stats.pending_stock_out || 0 }}</div>
          <div class="stat-label">待处理出库</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 低库存预警 -->
    <el-card shadow="hover">
      <template #header>
        <span style="font-weight: 600">⚠️ 低库存预警</span>
      </template>
      <el-table :data="stats.low_stock_items || []" stripe style="width: 100%" empty-text="暂无低库存预警">
        <el-table-column prop="material_code" label="物料编码" width="140" />
        <el-table-column prop="material_name" label="物料名称" />
        <el-table-column prop="warehouse_name" label="仓库" width="140" />
        <el-table-column prop="quantity" label="当前库存" width="120" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" width="120" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '../api/dashboard'

const stats = ref({})

onMounted(async () => {
  try {
    stats.value = await getDashboardStats()
  } catch (e) {
    // ignore
  }
})
</script>
