<template>
  <div class="page">
    <div class="page-header"><h2>维修员管理</h2></div>
    
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索姓名或账号" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button type="primary" @click="handleAdd" style="margin-left: auto;">
          <el-icon><Plus /></el-icon> 新增维修员
        </el-button>
      </div>
      
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="staff_no" label="账号" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="70">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系方式" width="130" />
        <el-table-column label="工作状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_order_count" label="当前工单数" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.current_order_count || 0" :max="99" />
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="账号" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button :type="row.status === 'online' ? 'warning' : 'success'" link size="small" @click="handleToggleStatus(row)">{{ row.status === 'online' ? '设为离线' : '设为在岗' }}</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
      />
    </el-card>
    
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑维修员' : '新增维修人员'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="账号" prop="staff_no">
          <el-input v-model="form.staff_no" placeholder="请输入手机号作为账号" :disabled="!!editId" />
        </el-form-item>
        <el-form-item label="密码" :prop="editId ? '' : 'password'">
          <el-input v-model="form.password" type="password" :placeholder="editId ? '不修改请留空' : '请输入密码'" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="联系方式" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系方式" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { staffApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const dialogVisible = ref(false)
const editId = ref(null)
const formRef = ref()

const form = reactive({
  staff_no: '',
  password: '',
  real_name: '',
  gender: 'male',
  phone: ''
})

const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入联系方式'))
  } else if (!/^1\d{10}$/.test(value)) {
    callback(new Error('手机号格式不正确'))
  } else {
    callback()
  }
}

const rules = {
  staff_no: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
    { pattern: /[a-z]/, message: '密码必须包含小写字母', trigger: 'blur' },
    { pattern: /[A-Z]/, message: '密码必须包含大写字母', trigger: 'blur' },
    { pattern: /\d/, message: '密码必须包含数字', trigger: 'blur' },
    { pattern: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/, message: '密码必须包含特殊符号', trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ validator: validatePhone, trigger: 'blur' }]
}

const statusText = (status) => ({ online: '在岗', offline: '离线', leave: '调休' }[status] || status)
const statusTagType = (status) => ({ online: 'success', offline: 'info', leave: 'warning' }[status] || 'info')

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await staffApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editId.value = null
  Object.assign(form, { staff_no: '', password: '', real_name: '', gender: 'male', phone: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  editId.value = row.id
  Object.assign(form, {
    staff_no: row.staff_no,
    password: '',
    real_name: row.real_name,
    gender: row.gender,
    phone: row.phone
  })
  dialogVisible.value = true
}

const handleToggleStatus = async (row) => {
  const newStatus = row.status === 'online' ? 'offline' : 'online'
  try {
    await staffApi.setStatus({ staff_id: row.id, status: newStatus })
    ElMessage.success(`已设置为${statusText(newStatus)}`)
    loadData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该维修员？', '提示', { type: 'warning' })
  try {
    await staffApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = { ...form }
    if (editId.value && !data.password) delete data.password
    if (editId.value) {
      await staffApi.update(editId.value, data)
      ElMessage.success('修改成功')
    } else {
      await staffApi.register(data)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.page { padding: 20px; }
.search-bar { display: flex; align-items: center; margin-bottom: 16px; }
</style>
