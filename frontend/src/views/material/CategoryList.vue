<template>
  <div class="page-container">
    <div class="page-header">
      <h3>物料分类</h3>
      <el-button type="primary" @click="handleAdd(null)">
        <el-icon><Plus /></el-icon> 新增分类
      </el-button>
    </div>

    <!-- 树形表格 -->
    <el-table :data="treeData" row-key="id" border default-expand-all stripe>
      <el-table-column prop="name" label="分类名称" min-width="200" />
      <el-table-column prop="code" label="分类编码" width="160" />
      <el-table-column prop="sort_order" label="排序" width="80" align="center" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleAdd(row)">添加子级</el-button>
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-popconfirm title="确定禁用该分类?" @confirm="handleDelete(row)">
            <template #reference>
              <el-button type="danger" link size="small">禁用</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新增分类'" width="450px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="dialog-form">
        <el-form-item label="父分类" v-if="!editingId">
          <el-input :model-value="parentName" disabled placeholder="无（顶级分类）" />
        </el-form-item>
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入分类编码" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" style="width: 100%" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getCategoryTree, createCategory, updateCategory, deleteCategory } from '../../api/material'

const treeData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const parentId = ref(null)
const parentName = ref('')
const submitting = ref(false)
const formRef = ref()

const defaultForm = { name: '', code: '', sort_order: 0 }
const form = reactive({ ...defaultForm })
const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入分类编码', trigger: 'blur' }],
}

onMounted(() => { loadData() })

async function loadData() {
  try {
    treeData.value = await getCategoryTree()
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
  Object.assign(form, { name: row.name, code: row.code, sort_order: row.sort_order })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createCategory({ ...form, parent_id: parentId.value })
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
    await deleteCategory(row.id)
    ElMessage.success('操作成功')
    loadData()
  } catch (e) { /* ignore */ }
}
</script>
