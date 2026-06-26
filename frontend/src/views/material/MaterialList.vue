<template>
  <div class="page-container">
    <div class="page-header">
      <h3>物料列表</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增物料
      </el-button>
    </div>

    <!-- 搜索 -->
    <div class="search-bar">
      <el-input v-model="searchKeyword" placeholder="搜索编码/名称" clearable style="width: 220px" @keyup.enter="loadData" />
      <el-tree-select
        v-model="searchCategoryId"
        :data="categoryTree"
        placeholder="选择分类"
        clearable
        check-strictly
        style="width: 200px"
      />
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" stripe border style="width: 100%">
      <el-table-column prop="code" label="编码" width="130" />
      <el-table-column prop="name" label="名称" min-width="150" />
      <el-table-column prop="spec" label="规格" width="120" />
      <el-table-column prop="model" label="型号" width="120" />
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="unit" label="单位" width="70" align="center" />
      <el-table-column prop="safety_stock" label="安全库存" width="100" align="center" />
      <el-table-column prop="price" label="参考单价" width="100" align="center" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-popconfirm title="确定禁用该物料?" @confirm="handleDelete(row)">
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
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑物料' : '新增物料'" width="600px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px" class="dialog-form">
        <el-form-item label="物料编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入物料编码" />
        </el-form-item>
        <el-form-item label="物料名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入物料名称" />
        </el-form-item>
        <el-form-item label="规格">
          <el-input v-model="form.spec" placeholder="请输入规格" />
        </el-form-item>
        <el-form-item label="型号">
          <el-input v-model="form.model" placeholder="请输入型号" />
        </el-form-item>
        <el-form-item label="分类">
          <el-tree-select
            v-model="form.category_id"
            :data="categoryTree"
            placeholder="选择分类"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如: 个/箱/米" />
        </el-form-item>
        <el-form-item label="安全库存">
          <el-input-number v-model="form.safety_stock" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最大库存">
          <el-input-number v-model="form.max_stock" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="参考单价">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getMaterialList, createMaterial, updateMaterial, deleteMaterial, getCategoryTree } from '../../api/material'

const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const searchCategoryId = ref(null)
const categoryTree = ref([])

const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref()

const defaultForm = {
  code: '', name: '', spec: '', model: '', category_id: null,
  unit: '个', safety_stock: 0, max_stock: 0, price: 0, remark: '',
}
const form = reactive({ ...defaultForm })
const rules = {
  code: [{ required: true, message: '请输入物料编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入物料名称', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
}

onMounted(() => {
  loadData()
  loadCategoryTree()
})

async function loadData() {
  try {
    const res = await getMaterialList({
      page: page.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value || undefined,
      category_id: searchCategoryId.value || undefined,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) { /* ignore */ }
}

async function loadCategoryTree() {
  try {
    categoryTree.value = buildTree(await getCategoryTree())
  } catch (e) { /* ignore */ }
}

function buildTree(data) {
  return (data || []).map(item => ({
    value: item.id,
    label: item.name,
    children: item.children?.length ? buildTree(item.children) : undefined,
  }))
}

function resetSearch() {
  searchKeyword.value = ''
  searchCategoryId.value = null
  page.value = 1
  loadData()
}

function handleAdd() {
  editingId.value = null
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    code: row.code, name: row.name, spec: row.spec, model: row.model,
    category_id: row.category_id, unit: row.unit, safety_stock: row.safety_stock,
    max_stock: row.max_stock, price: row.price, remark: row.remark,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateMaterial(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createMaterial(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) { /* ignore */ } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await deleteMaterial(row.id)
    ElMessage.success('操作成功')
    loadData()
  } catch (e) { /* ignore */ }
}
</script>
