<template>
  <div class="page-container">
    <div class="page-header">
      <h3>库存查询</h3>
    </div>

    <!-- 搜索 -->
    <div class="search-bar">
      <el-select v-model="searchWarehouseId" placeholder="选择仓库" clearable style="width: 180px">
        <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
      </el-select>
      <el-checkbox v-model="lowStockOnly" label="仅看低库存" />
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" stripe border style="width: 100%">
      <el-table-column prop="material_code" label="物料编码" width="130" />
      <el-table-column prop="material_name" label="物料名称" min-width="150" />
      <el-table-column prop="material_spec" label="规格" width="120" />
      <el-table-column prop="material_unit" label="单位" width="70" align="center" />
      <el-table-column prop="warehouse_name" label="仓库" width="120" />
      <el-table-column prop="location_code" label="库位" width="120" />
      <el-table-column prop="quantity" label="库存数量" width="100" align="center">
        <template #default="{ row }">
          <span :style="{ color: row.quantity <= row.safety_stock && row.safety_stock > 0 ? '#f56c6c' : '', fontWeight: 600 }">
            {{ row.quantity }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="frozen_quantity" label="冻结数量" width="100" align="center" />
      <el-table-column prop="available_quantity" label="可用数量" width="100" align="center">
        <template #default="{ row }">
          <span style="color: #67c23a; font-weight: 600">{{ row.available_quantity }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="safety_stock" label="安全库存" width="100" align="center" />
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 16px; display: flex; justify-content: flex-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInventoryList } from '../../api/inventory'
import { getAllWarehouses } from '../../api/warehouse'

const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchWarehouseId = ref(null)
const lowStockOnly = ref(false)
const warehouseOptions = ref([])

onMounted(async () => {
  loadData()
  try {
    warehouseOptions.value = await getAllWarehouses()
  } catch (e) { /* ignore */ }
})

async function loadData() {
  try {
    const res = await getInventoryList({
      page: page.value,
      page_size: pageSize.value,
      warehouse_id: searchWarehouseId.value || undefined,
      low_stock: lowStockOnly.value || undefined,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) { /* ignore */ }
}

function resetSearch() {
  searchWarehouseId.value = null
  lowStockOnly.value = false
  page.value = 1
  loadData()
}
</script>
