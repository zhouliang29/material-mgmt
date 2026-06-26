<template>
  <div class="page-container">
    <div class="page-header">
      <h3>仓库管理</h3>
      <el-button type="primary" @click="handleAddWarehouse">
        <el-icon><Plus /></el-icon> 新增仓库
      </el-button>
    </div>

    <!-- 搜索 -->
    <div class="search-bar">
      <el-input v-model="searchKeyword" placeholder="搜索仓库名称/编码" clearable style="width: 220px" @keyup.enter="loadWarehouses" />
      <el-button type="primary" @click="loadWarehouses">查询</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <!-- 仓库表格 -->
    <el-table :data="warehouseList" stripe border style="width: 100%">
      <el-table-column prop="code" label="仓库编码" width="130" />
      <el-table-column prop="name" label="仓库名称" min-width="150" />
      <el-table-column prop="address" label="地址" min-width="200" />
      <el-table-column prop="manager" label="负责人" width="100" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEditWarehouse(row)">编辑</el-button>
          <el-button type="success" link size="small" @click="handleManageLocations(row)">库位管理</el-button>
          <el-popconfirm title="确定禁用该仓库?" @confirm="handleDeleteWarehouse(row)">
            <template #reference>
              <el-button type="danger" link size="small">禁用</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 16px; display: flex; justify-content: flex-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadWarehouses"
        @current-change="loadWarehouses"
      />
    </div>

    <!-- 仓库对话框 -->
    <el-dialog v-model="warehouseDialogVisible" :title="editingWarehouseId ? '编辑仓库' : '新增仓库'" width="500px" destroy-on-close>
      <el-form :model="warehouseForm" :rules="warehouseRules" ref="warehouseFormRef" label-width="80px" class="dialog-form">
        <el-form-item label="仓库编码" prop="code">
          <el-input v-model="warehouseForm.code" placeholder="请输入仓库编码" />
        </el-form-item>
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="warehouseForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="warehouseForm.manager" placeholder="请输入负责人" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="warehouseForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="warehouseDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleWarehouseSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 库位管理对话框 -->
    <el-dialog v-model="locationDialogVisible" :title="`库位管理 - ${currentWarehouse?.name || ''}`" width="700px" destroy-on-close>
      <div style="margin-bottom: 12px">
        <el-button type="primary" size="small" @click="handleAddLocation">
          <el-icon><Plus /></el-icon> 新增库位
        </el-button>
      </div>
      <el-table :data="locationList" stripe border size="small">
        <el-table-column prop="code" label="库位编码" width="140" />
        <el-table-column prop="zone" label="区" width="80" />
        <el-table-column prop="rack" label="架" width="80" />
        <el-table-column prop="row" label="排" width="80" />
        <el-table-column prop="col" label="位" width="80" />
        <el-table-column prop="remark" label="备注" min-width="120" />
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-popconfirm title="确定禁用?" @confirm="handleDeleteLocation(row)">
              <template #reference>
                <el-button type="danger" link size="small">禁用</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 新增库位 -->
      <el-dialog v-model="locationFormVisible" title="新增库位" width="400px" append-to-body destroy-on-close>
        <el-form :model="locationForm" ref="locationFormRef" label-width="80px" class="dialog-form">
          <el-form-item label="库位编码" prop="code">
            <el-input v-model="locationForm.code" placeholder="如: A-01-01-01" />
          </el-form-item>
          <el-form-item label="区">
            <el-input v-model="locationForm.zone" placeholder="区" />
          </el-form-item>
          <el-form-item label="架">
            <el-input v-model="locationForm.rack" placeholder="架" />
          </el-form-item>
          <el-form-item label="排">
            <el-input v-model="locationForm.row" placeholder="排" />
          </el-form-item>
          <el-form-item label="位">
            <el-input v-model="locationForm.col" placeholder="位" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="locationForm.remark" type="textarea" :rows="2" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="locationFormVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleLocationSubmit">确定</el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getWarehouseList, createWarehouse, updateWarehouse, deleteWarehouse,
  getLocationList, createLocation, deleteLocation,
} from '../../api/warehouse'

// 仓库列表
const warehouseList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')

// 仓库对话框
const warehouseDialogVisible = ref(false)
const editingWarehouseId = ref(null)
const submitting = ref(false)
const warehouseFormRef = ref()
const defaultWarehouseForm = { code: '', name: '', address: '', manager: '', remark: '' }
const warehouseForm = reactive({ ...defaultWarehouseForm })
const warehouseRules = {
  code: [{ required: true, message: '请输入仓库编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }],
}

// 库位对话框
const locationDialogVisible = ref(false)
const locationList = ref([])
const currentWarehouse = ref(null)
const locationFormVisible = ref(false)
const locationFormRef = ref()
const defaultLocationForm = { code: '', zone: '', rack: '', row: '', col: '', remark: '' }
const locationForm = reactive({ ...defaultLocationForm })

onMounted(() => { loadWarehouses() })

async function loadWarehouses() {
  try {
    const res = await getWarehouseList({
      page: page.value, page_size: pageSize.value,
      keyword: searchKeyword.value || undefined,
    })
    warehouseList.value = res.items || []
    total.value = res.total || 0
  } catch (e) { /* ignore */ }
}

function resetSearch() {
  searchKeyword.value = ''
  page.value = 1
  loadWarehouses()
}

function handleAddWarehouse() {
  editingWarehouseId.value = null
  Object.assign(warehouseForm, defaultWarehouseForm)
  warehouseDialogVisible.value = true
}

function handleEditWarehouse(row) {
  editingWarehouseId.value = row.id
  Object.assign(warehouseForm, {
    code: row.code, name: row.name, address: row.address,
    manager: row.manager, remark: row.remark,
  })
  warehouseDialogVisible.value = true
}

async function handleWarehouseSubmit() {
  await warehouseFormRef.value.validate()
  submitting.value = true
  try {
    if (editingWarehouseId.value) {
      await updateWarehouse(editingWarehouseId.value, warehouseForm)
      ElMessage.success('更新成功')
    } else {
      await createWarehouse(warehouseForm)
      ElMessage.success('创建成功')
    }
    warehouseDialogVisible.value = false
    loadWarehouses()
  } catch (e) { /* ignore */ } finally {
    submitting.value = false
  }
}

async function handleDeleteWarehouse(row) {
  try {
    await deleteWarehouse(row.id)
    ElMessage.success('操作成功')
    loadWarehouses()
  } catch (e) { /* ignore */ }
}

// 库位管理
async function handleManageLocations(row) {
  currentWarehouse.value = row
  locationDialogVisible.value = true
  try {
    locationList.value = await getLocationList(row.id)
  } catch (e) { /* ignore */ }
}

function handleAddLocation() {
  Object.assign(locationForm, defaultLocationForm)
  locationFormVisible.value = true
}

async function handleLocationSubmit() {
  submitting.value = true
  try {
    await createLocation({ ...locationForm, warehouse_id: currentWarehouse.value.id })
    ElMessage.success('创建成功')
    locationFormVisible.value = false
    locationList.value = await getLocationList(currentWarehouse.value.id)
  } catch (e) { /* ignore */ } finally {
    submitting.value = false
  }
}

async function handleDeleteLocation(row) {
  try {
    await deleteLocation(row.id)
    ElMessage.success('操作成功')
    locationList.value = await getLocationList(currentWarehouse.value.id)
  } catch (e) { /* ignore */ }
}
</script>
