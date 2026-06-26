<template>
  <div class="page-container">
    <div class="page-header">
      <h3>角色权限</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增角色
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" stripe border style="width: 100%">
      <el-table-column prop="name" label="角色名称" width="160" />
      <el-table-column prop="code" label="角色编码" width="160" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEditPermission(row)">分配权限</el-button>
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除该角色?" @confirm="handleDelete(row)">
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑角色对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑角色' : '新增角色'" width="450px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="dialog-form">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色编码" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配权限对话框 -->
    <el-dialog v-model="permDialogVisible" title="分配权限" width="550px" destroy-on-close>
      <div v-for="module in permissionModules" :key="module.name" style="margin-bottom: 16px">
        <div style="font-weight: 600; margin-bottom: 8px; color: #303133">{{ module.name }}</div>
        <el-checkbox-group v-model="selectedPermIds">
          <el-checkbox
            v-for="perm in module.permissions"
            :key="perm.id"
            :value="perm.id"
            :label="perm.name"
          />
        </el-checkbox-group>
      </div>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="permSubmitting" @click="handleSavePermission">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getRoleList, createRole, updateRole, deleteRole, assignRolePermissions, getPermissionList } from '../../api/role'

const tableData = ref([])
const dialogVisible = ref(false)
const permDialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const permSubmitting = ref(false)
const formRef = ref()

const defaultForm = { name: '', code: '', description: '' }
const form = reactive({ ...defaultForm })
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

// 权限数据
const allPermissions = ref([])
const selectedPermIds = ref([])
const currentRoleId = ref(null)

const permissionModules = computed(() => {
  const map = {}
  for (const perm of allPermissions.value) {
    if (!map[perm.module]) map[perm.module] = { name: perm.module, permissions: [] }
    map[perm.module].permissions.push(perm)
  }
  return Object.values(map)
})

onMounted(() => {
  loadData()
  loadPermissions()
})

async function loadData() {
  try {
    const res = await getRoleList()
    tableData.value = res.items || res || []
  } catch (e) { /* ignore */ }
}

async function loadPermissions() {
  try {
    allPermissions.value = await getPermissionList()
  } catch (e) { /* ignore */ }
}

function handleAdd() {
  editingId.value = null
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  Object.assign(form, { name: row.name, code: row.code, description: row.description })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateRole(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createRole(form)
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
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* ignore */ }
}

function handleEditPermission(row) {
  currentRoleId.value = row.id
  // 提取当前角色已有的权限 ID
  selectedPermIds.value = (row.permissions || []).map(p => p.id)
  permDialogVisible.value = true
}

async function handleSavePermission() {
  permSubmitting.value = true
  try {
    await assignRolePermissions(currentRoleId.value, selectedPermIds.value)
    ElMessage.success('权限分配成功')
    permDialogVisible.value = false
    loadData()
  } catch (e) { /* ignore */ } finally {
    permSubmitting.value = false
  }
}
</script>
