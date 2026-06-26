<template>
  <div class="page-container">
    <div class="page-header">
      <h3>库存流水</h3>
    </div>

    <!-- 搜索 -->
    <div class="search-bar">
      <el-select v-model="searchWarehouseId" placeholder="选择仓库" clearable style="width: 180px">
        <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
      </el-select>
      <el-select v-model="searchOrderType" placeholder="单据类型" clearable style="width: 150px">
        <el-option label="入库" value="stock_in" />
        <el-option label="出库" value="stock_out" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" stripe border style="width: 100%">
      <el-table-column prop="material_code" label="物料编码" width="130" />
      <el-table-column prop="material_name" label="物料名称" min-width="150" />
      <el-table-column prop="warehouse_name" label="仓库" width="120" />
      <el-table-column prop="order_type" label="类型" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.order_type === 'stock_in' ? 'success' : 'danger'" size="small">
            {{ row.order_type === 'stock_in' ? '入库' : '出库' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="变动数量" width="100" align="center">
        <template #default="{ row }">
          <span :style="{ color: row.quantity > 0 ? '#67c23a' : '#f56c6c', fontWeight: 600 }">
            {{ row.quantity > 0 ? '+' : '' }}{{ row.quantity }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="before_quantity" label="变动前" width="100" align="center" />
      <el-table-column prop="after_quantity" label="变动后" width="100" align="center" />
      <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 16px; display: flex; justify-content: flex-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTransactionList } from '../../api/inventory'
import { getAllWarehouses } from '../../api/warehouse'

const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchWarehouseId = ref(null)
const searchOrderType = ref('')
const warehouseOptions = ref([])

onMounted(async () => {
  loadData()
  try {
    warehouseOptions.value = await getAllWarehouses()
  } catch (e) { /* ignore */ }
})

async function loadData() {
  try {
    const res = await getTransactionList({
      page: page.value,
      page_size: pageSize.value,
      warehouse_id: searchWarehouseId.value || undefined,
      order_type: searchOrderType.value || undefined,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) { /* ignore */ }
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

function resetSearch() {
  searchWarehouseId.value = null
  searchOrderType.value = ''
  page.value = 1
  loadData()
}
</script>
