<template>
  <div class="page-container">
    <div class="page-header">
      <h3>入库管理</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新建入库单
      </el-button>
    </div>

    <!-- 搜索 -->
    <div class="search-bar">
      <el-select v-model="searchStatus" placeholder="单据状态" clearable style="width: 150px">
        <el-option label="草稿" value="draft" />
        <el-option label="待审批" value="pending_approval" />
        <el-option label="已审批" value="approved" />
        <el-option label="已完成" value="done" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" stripe border style="width: 100%">
      <el-table-column prop="order_no" label="入库单号" width="160" />
      <el-table-column prop="order_type" label="入库类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag size="small">{{ orderTypeMap[row.order_type] || row.order_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTypeMap[row.status]" size="small" class="status-tag">
            {{ statusMap[row.status] || row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
          <el-button v-if="row.status === 'draft'" type="warning" link size="small" @click="handleSubmit(row)">提交审批</el-button>
          <el-button v-if="row.status === 'pending_approval'" type="success" link size="small" @click="handleApprove(row)">审批</el-button>
          <el-button v-if="row.status === 'approved'" type="success" link size="small" @click="handleExecute(row)">执行入库</el-button>
        </template>
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

    <!-- 新建入库单对话框 -->
    <el-dialog v-model="dialogVisible" title="新建入库单" width="750px" destroy-on-close>
      <el-form :model="form" ref="formRef" label-width="80px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="入库类型">
              <el-select v-model="form.order_type" style="width: 100%">
                <el-option label="采购入库" value="purchase" />
                <el-option label="生产入库" value="produce" />
                <el-option label="退货入库" value="return" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="仓库" prop="warehouse_id">
              <el-select v-model="form.warehouse_id" placeholder="选择仓库" style="width: 100%">
                <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>

        <!-- 入库明细 -->
        <el-divider content-position="left">入库明细</el-divider>
        <div v-for="(item, idx) in form.items" :key="idx" style="margin-bottom: 12px; display: flex; gap: 8px; align-items: center">
          <el-select v-model="item.material_id" placeholder="选择物料" filterable style="width: 200px">
            <el-option v-for="m in materialOptions" :key="m.id" :label="`${m.code} - ${m.name}`" :value="m.id" />
          </el-select>
          <el-input-number v-model="item.plan_quantity" :min="0" :precision="2" placeholder="计划数量" style="width: 140px" />
          <el-input-number v-model="item.actual_quantity" :min="0" :precision="2" placeholder="实际数量" style="width: 140px" />
          <el-input-number v-model="item.unit_price" :min="0" :precision="2" placeholder="单价" style="width: 120px" />
          <el-button type="danger" link @click="form.items.splice(idx, 1)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <el-button type="primary" link @click="form.items.push({ material_id: null, plan_quantity: 0, actual_quantity: 0, unit_price: 0, remark: '' })">
          + 添加明细
        </el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateOrder">创建</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="入库单详情" width="700px" destroy-on-close>
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="入库单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="入库类型">{{ orderTypeMap[currentOrder.order_type] }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTypeMap[currentOrder.status]" size="small">{{ statusMap[currentOrder.status] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentOrder.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="currentOrder?.items || []" stripe border size="small" style="margin-top: 16px">
        <el-table-column prop="material_code" label="物料编码" width="130" />
        <el-table-column prop="material_name" label="物料名称" min-width="150" />
        <el-table-column prop="plan_quantity" label="计划数量" width="100" align="center" />
        <el-table-column prop="actual_quantity" label="实际数量" width="100" align="center" />
        <el-table-column prop="unit_price" label="单价" width="100" align="center" />
        <el-table-column prop="remark" label="备注" min-width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getStockInList, createStockIn, getStockInDetail, submitStockIn, approveStockIn, executeStockIn } from '../../api/inventory'
import { getAllWarehouses } from '../../api/warehouse'
import { getMaterialList } from '../../api/material'

const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchStatus = ref('')

const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref()
const currentOrder = ref(null)

const warehouseOptions = ref([])
const materialOptions = ref([])

const defaultForm = { order_type: 'purchase', warehouse_id: null, remark: '', items: [{ material_id: null, plan_quantity: 0, actual_quantity: 0, unit_price: 0, remark: '' }] }
const form = reactive({ ...defaultForm })

const orderTypeMap = { purchase: '采购入库', produce: '生产入库', return: '退货入库' }
const statusMap = { draft: '草稿', pending_approval: '待审批', approved: '已审批', done: '已完成', cancelled: '已取消' }
const statusTypeMap = { draft: 'info', pending_approval: 'warning', approved: 'success', done: '', cancelled: 'danger' }

onMounted(async () => {
  loadData()
  try {
    warehouseOptions.value = await getAllWarehouses()
    const res = await getMaterialList({ page: 1, page_size: 1000 })
    materialOptions.value = res.items || []
  } catch (e) { /* ignore */ }
})

async function loadData() {
  try {
    const res = await getStockInList({ page: page.value, page_size: pageSize.value, status: searchStatus.value || undefined })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) { /* ignore */ }
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

function handleAdd() {
  Object.assign(form, JSON.parse(JSON.stringify(defaultForm)))
  dialogVisible.value = true
}

async function handleCreateOrder() {
  if (!form.warehouse_id) return ElMessage.warning('请选择仓库')
  if (!form.items.length || !form.items.some(i => i.material_id)) return ElMessage.warning('请添加入库明细')
  submitting.value = true
  try {
    await createStockIn(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { /* ignore */ } finally {
    submitting.value = false
  }
}

async function handleView(row) {
  try {
    currentOrder.value = await getStockInDetail(row.id)
    detailDialogVisible.value = true
  } catch (e) { /* ignore */ }
}

async function handleSubmit(row) {
  try {
    await ElMessageBox.confirm('确定提交审批？', '提示')
    await submitStockIn(row.id)
    ElMessage.success('已提交审批')
    loadData()
  } catch (e) { /* ignore */ }
}

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('确定审批通过？', '审批')
    await approveStockIn(row.id)
    ElMessage.success('审批通过')
    loadData()
  } catch (e) { /* ignore */ }
}

async function handleExecute(row) {
  try {
    await ElMessageBox.confirm('确定执行入库？执行后库存将变更！', '执行入库')
    await executeStockIn(row.id)
    ElMessage.success('入库完成')
    loadData()
  } catch (e) { /* ignore */ }
}
</script>
