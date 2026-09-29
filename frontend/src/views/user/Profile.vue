<template>
  <div class="user-profile">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="profile-card">
          <div class="avatar-section">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="uploadAvatar"
            >
              <el-avatar :src="userInfo.avatar" :size="100" style="background: linear-gradient(135deg, #4f46e5, #6366f1); font-size: 36px;">
                {{ (userInfo.real_name || '用')[0] }}
              </el-avatar>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </el-upload>
            <h3>{{ userInfo.real_name }}</h3>
            <p>{{ getUserType(userInfo.user_type) }}</p>
          </div>
          
          <el-menu :default-active="activeMenu" @select="handleMenuSelect">
            <el-menu-item index="info">
              <el-icon><User /></el-icon>
              <span>基本信息</span>
            </el-menu-item>
            <el-menu-item index="password">
              <el-icon><Lock /></el-icon>
              <span>修改密码</span>
            </el-menu-item>
            <el-menu-item index="delete" style="color: #f56c6c;">
              <el-icon><Delete /></el-icon>
              <span>账号注销</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card v-if="activeMenu === 'info'">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-form :model="infoForm" :rules="infoRules" ref="infoFormRef" label-width="100px">
            <el-form-item label="账号">
              <el-input :value="userInfo.username || userInfo.user_no || '-'" disabled placeholder="账号信息" />
            </el-form-item>
            <el-form-item label="姓名" prop="real_name">
              <el-input v-model="infoForm.real_name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="infoForm.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="联系方式" prop="phone">
              <el-input v-model="infoForm.phone" placeholder="请输入联系方式" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveInfo" :loading="saving">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card v-if="activeMenu === 'password'">
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入原密码" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请确认新密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changing">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card v-if="activeMenu === 'delete'">
          <template #header>
            <span style="color: #f56c6c;">账号注销</span>
          </template>
          <div class="delete-section">
            <el-alert
              title="账号注销须知"
              type="warning"
              :closable="false"
              style="margin-bottom: 20px"
            >
              <div style="font-size: 14px; line-height: 1.5;">
                <p>1. 账号注销后，所有个人数据将被删除，无法恢复</p>
                <p>2. 注销前请确保已完成所有未处理的报修工单</p>
                <p>3. 注销后将无法使用该账号登录系统</p>
              </div>
            </el-alert>
            
            <el-form :model="deleteForm" :rules="deleteRules" ref="deleteFormRef" label-width="100px">
              <el-form-item label="确认密码" prop="password">
                <el-input v-model="deleteForm.password" type="password" placeholder="请输入密码确认身份" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="danger" @click="confirmDelete" :loading="deleting">确认注销</el-button>
                <el-button @click="activeMenu = 'info'">取消</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { userApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, Delete, Camera } from '@element-plus/icons-vue'

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const activeMenu = ref('info')
const userInfo = ref({})
const saving = ref(false)
const changing = ref(false)
const deleting = ref(false)
const infoFormRef = ref()
const passwordFormRef = ref()
const deleteFormRef = ref()

const infoForm = reactive({
  real_name: '',
  gender: 'male',
  phone: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const deleteForm = reactive({
  password: ''
})

const infoRules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系方式', trigger: 'blur' }]
}

const deleteRules = {
  password: [{ required: true, message: '请输入密码确认身份', trigger: 'blur' }]
}

const validateConfirm = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
    { pattern: /[a-z]/, message: '密码必须包含小写字母', trigger: 'blur' },
    { pattern: /[A-Z]/, message: '密码必须包含大写字母', trigger: 'blur' },
    { pattern: /\d/, message: '密码必须包含数字', trigger: 'blur' },
    { pattern: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/, message: '密码必须包含特殊符号', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadUserInfo()
})

const loadUserInfo = async () => {
  try {
    const res = await userApi.profile()
    if (res.code === 200) {
      userInfo.value = res.data
      infoForm.real_name = res.data.real_name
      infoForm.gender = res.data.gender
      infoForm.phone = res.data.phone
    }
  } catch (error) {
    console.error(error)
  }
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const getUserType = (type) => {
  const types = { student: '学生', teacher: '教师', staff: '维修员', admin: '管理员' }
  return types[type] || '用户'
}

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (file.size / 1024 / 1024 > 10) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return true
}

const compressImage = (file) => {
  return new Promise((resolve) => {
    if (file.size / 1024 / 1024 < 0.5) {
      resolve(file)
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const maxSize = 800
        let width = img.width
        let height = img.height
        if (width > maxSize || height > maxSize) {
          if (width > height) {
            height = (height / width) * maxSize
            width = maxSize
          } else {
            width = (width / height) * maxSize
            height = maxSize
          }
        }
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        canvas.toBlob(
          (blob) => {
            resolve(new File([blob], file.name.replace(/\.\w+$/, '.jpg'), { type: 'image/jpeg' }))
          },
          'image/jpeg',
          0.8
        )
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })
}

const uploadAvatar = async (options) => {
  try {
    const compressedFile = await compressImage(options.file)
    const formData = new FormData()
    formData.append('file', compressedFile)
    formData.append('type', 'avatar')
    const response = await fetch('/api/upload/', {
      method: 'POST',
      body: formData
    })
    const result = await response.json()
    if (result.code === 200) {
      await userApi.update(userInfo.value.id, { avatar: result.url })
      userInfo.value.avatar = result.url
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      ElMessage.success('头像上传成功')
    } else {
      ElMessage.error(result.error || '头像上传失败')
    }
  } catch (error) {
    ElMessage.error('头像上传失败')
  }
}

const saveInfo = async () => {
  await infoFormRef.value.validate()
  saving.value = true
  try {
    await userApi.update(userInfo.value.id, infoForm)
    ElMessage.success('保存成功')
    await loadUserInfo()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  await passwordFormRef.value.validate()
  changing.value = true
  try {
    await userApi.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功')
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    ElMessage.error('密码修改失败')
  } finally {
    changing.value = false
  }
}

const confirmDelete = async () => {
  await deleteFormRef.value.validate()
  
  try {
    await ElMessageBox.confirm(
      '确定要注销账号吗？注销后所有数据将被删除，无法恢复。',
      '账号注销确认',
      {
        confirmButtonText: '确认注销',
        cancelButtonText: '取消',
        type: 'danger'
      }
    )
  } catch (error) {
    return
  }
  
  deleting.value = true
  try {
    await userApi.deleteAccount({ password: deleteForm.password })
    ElMessage.success('账号注销成功')
    // 清除本地存储
    localStorage.removeItem('userToken')
    localStorage.removeItem('userInfo')
    // 跳转到登录页面
    window.location.href = '/login'
  } catch (error) {
    ElMessage.error('账号注销失败')
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped lang="scss">
.user-profile {
  .profile-card {
    .avatar-section {
      text-align: center;
      padding: 30px 0;
      
      .avatar-uploader {
        position: relative;
        display: inline-block;
        cursor: pointer;
        
        &:hover .avatar-overlay {
          opacity: 1;
        }
      }
      
      .avatar-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #fff;
        opacity: 0;
        transition: opacity 0.3s;
        
        .el-icon {
          font-size: 24px;
          margin-bottom: 5px;
        }
        
        span {
          font-size: 12px;
        }
      }
      
      h3 {
        margin: 15px 0 5px;
        font-size: 18px;
      }
      
      p {
        color: #666;
        font-size: 14px;
      }
    }
    
    .el-menu {
      border-right: none;
    }
  }
}
</style>
