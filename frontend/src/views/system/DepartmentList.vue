<template>
  <div class="page-container">
    <div class="page-header">
      <h3>部门管理</h3>
      <el-button type="primary" @click="handleAdd(null)">
        <el-icon><Plus /></el-icon> 新增部门
      </el-button>
    </div>

    <!-- 树形表格 -->
    <el-table :data="treeData" row-key="id" border default-expand-all stripe>
      <el-table-column prop="name" label="部门名称" min-width="200" />
      <el-table-column prop="code" label="部门编码" width="160" />
      <el-table-column prop="manager" label="负责人" width="100" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleAdd(row)">添加子级</el-button>
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-popconfirm title="确定禁用该部门?" @confirm="handleDelete(row)">
            <template #reference>
              <el-button type="danger" link size="small">禁用</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑部门' : '新增部门'" width="450px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="dialog-form">
        <el-form-item label="父部门" v-if="!editingId">
          <el-input :model-value="parentName" disabled placeholder="无（顶级部门）" />
        </el-form-item>
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入部门编码" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.manager" placeholder="请输入负责人" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="备注" />
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
import { getDepartmentTree, createDepartment, updateDepartment, deleteDepartment } from '../../api/department'

const treeData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const parentId = ref(null)
const parentName = ref('')
const submitting = ref(false)
const formRef = ref()

const defaultForm = { name: '', code: '', manager: '', remark: '' }
const form = reactive({ ...defaultForm })
const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }],
}

onMounted(() => loadData())

async function loadData() {
  try {
    const res = await getDepartmentTree()
    treeData.value = res || []
  } catch (e) { /* ignore */ }
}

function handleAdd(row) {
  editingId.value = null
  parentId.value = row?.id || null
  parentName.value = row?.name || ''
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  parentId.value = row.parent_id
  parentName.value = ''
  Object.assign(form, { name: row.name, code: row.code, manager: row.manager, remark: row.remark })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateDepartment(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createDepartment({ ...form, parent_id: parentId.value })
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
    await deleteDepartment(row.id)
    ElMessage.success('操作成功')
    loadData()
  } catch (e) { /* ignore */ }
}
</script>
