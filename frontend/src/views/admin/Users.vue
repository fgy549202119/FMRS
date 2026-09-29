<template>
  <div class="page">
    <div class="page-header"><h2>用户管理</h2></div>
    <el-card>
      <div class="search-bar">
        <el-input v-model="search" placeholder="搜索用户姓名/账号" style="width: 200px;" clearable @clear="loadUsers" @keyup.enter="loadUsers" />
        <el-select v-model="userType" placeholder="用户类型" clearable style="width: 120px; margin-left: 10px;" @change="loadUsers">
          <el-option label="学生" value="student" />
          <el-option label="教师" value="teacher" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-button type="primary" @click="loadUsers" style="margin-left: 10px;">搜索</el-button>
        <el-button type="primary" @click="handleAdd">新增用户</el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedRows.length === 0">批量删除</el-button>
      </div>
      <el-table :data="tableData" stripe @selection-change="handleSelectionChange" v-loading="loading">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="username" label="用户账号" width="120" />
        <el-table-column prop="real_name" label="用户姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="user_type" label="用户类型" width="80">
          <template #default="{ row }">
            <el-tag :type="getUserTypeTag(row.user_type)">{{ getUserTypeText(row.user_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系方式" width="120" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar || defaultAvatar" :size="40" />
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)" :disabled="row.user_type === 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadUsers"
        @current-change="loadUsers"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户账号" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户账号" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input v-model="form.password" type="password" placeholder="请输入密码（留空则不修改）" show-password />
        </el-form-item>
        <el-form-item label="确认密码" v-if="!isEdit" prop="confirm_password">
          <el-input v-model="form.confirm_password" type="password" placeholder="请确认密码" show-password />
        </el-form-item>
        <el-form-item label="用户姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入用户姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="用户类型" prop="user_type">
          <el-select v-model="form.user_type" placeholder="请选择用户类型" style="width: 100%;" :disabled="isEdit && form.user_type === 'admin'">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系方式" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action="/api/upload/"
            :data="{ type: 'avatar' }"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
          >
            <img v-if="form.avatar" :src="form.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
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
import { userApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const search = ref('')
const userType = ref('')
const tableData = ref([])
const selectedRows = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  id: null,
  username: '',
  password: '',
  confirm_password: '',
  real_name: '',
  gender: 'male',
  user_type: 'student',
  phone: '',
  avatar: ''
})

const validatePass = (rule, value, callback) => {
  if (!isEdit.value && !value) {
    callback(new Error('请输入密码'))
  } else if (value && value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else if (value && !/[a-z]/.test(value)) {
    callback(new Error('密码必须包含小写字母'))
  } else if (value && !/[A-Z]/.test(value)) {
    callback(new Error('密码必须包含大写字母'))
  } else if (value && !/\d/.test(value)) {
    callback(new Error('密码必须包含数字'))
  } else if (value && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(value)) {
    callback(new Error('密码必须包含特殊符号'))
  } else {
    callback()
  }
}

const validateConfirmPass = (rule, value, callback) => {
  if (!isEdit.value && value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

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
  username: [{ required: true, message: '请输入用户账号', trigger: 'blur' }],
  password: [{ validator: validatePass, trigger: 'blur' }],
  confirm_password: [{ validator: validateConfirmPass, trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入用户姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  user_type: [{ required: true, message: '请选择用户类型', trigger: 'change' }],
  phone: [{ validator: validatePhone, trigger: 'blur' }]
}

onMounted(() => {
  loadUsers()
})

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (search.value) params.search = search.value
    if (userType.value) params.user_type = userType.value
    
    const res = await userApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const resetForm = () => {
  form.id = null
  form.username = ''
  form.password = ''
  form.confirm_password = ''
  form.real_name = ''
  form.gender = 'male'
  form.user_type = 'student'
  form.phone = ''
  form.avatar = ''
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  isEdit.value = true
  form.id = row.id
  form.username = row.username
  form.real_name = row.real_name
  form.gender = row.gender
  form.user_type = row.user_type
  form.phone = row.phone
  form.avatar = row.avatar
  dialogVisible.value = true
}

const handleAvatarSuccess = (response) => {
  if (response.code === 200) {
    form.avatar = response.url
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error(response.error || '头像上传失败')
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = {
      real_name: form.real_name,
      gender: form.gender,
      user_type: form.user_type,
      phone: form.phone,
      avatar: form.avatar
    }
    
    if (isEdit.value) {
      if (form.password) {
        data.password = form.password
      }
      await userApi.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      data.username = form.username
      data.password = form.password
      data.confirm_password = form.confirm_password
      await userApi.register(data)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadUsers()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  if (row.user_type === 'admin') {
    ElMessage.warning('管理员账号不允许删除')
    return
  }
  await ElMessageBox.confirm('确定删除该用户？', '提示', { type: 'warning' })
  try {
    await userApi.delete(row.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的用户')
    return
  }
  const adminCount = selectedRows.value.filter(r => r.user_type === 'admin').length
  if (adminCount > 0) {
    ElMessage.warning('选中的用户中包含管理员账号，不允许删除')
    return
  }
  await ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 个用户？`, '提示', { type: 'warning' })
  try {
    await userApi.batchDelete(selectedRows.value.map(r => r.id))
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    ElMessage.error('批量删除失败')
  }
}

const getUserTypeTag = (type) => {
  const map = { student: '', teacher: 'success', admin: 'danger' }
  return map[type] || ''
}

const getUserTypeText = (type) => {
  const map = { student: '学生', teacher: '教师', admin: '管理员' }
  return map[type] || type
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
<style scoped lang="scss">
.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}
.avatar-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    &:hover {
      border-color: #409eff;
    }
  }
  .avatar {
    width: 100px;
    height: 100px;
    display: block;
  }
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 100px;
    height: 100px;
    line-height: 100px;
    text-align: center;
  }
}
</style>
