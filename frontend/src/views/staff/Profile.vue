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
              <el-avatar :src="staffInfo.avatar" :size="100" style="background: linear-gradient(135deg, #059669, #10b981); font-size: 36px;">
                {{ (staffInfo.real_name || '维')[0] }}
              </el-avatar>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </el-upload>
            <h3>{{ staffInfo.real_name }}</h3>
            <p>维修员</p>
          </div>
          
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="账号">{{ staffInfo.staff_no }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ staffInfo.gender === 'male' ? '男' : '女' }}</el-descriptions-item>
            <el-descriptions-item label="联系方式">{{ staffInfo.phone }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>基本信息</span>
          </template>
          <el-form :model="infoForm" :rules="infoRules" ref="infoFormRef" label-width="100px">
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
        
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>工单统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">总工单</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value pending">{{ stats.pending }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value processing">{{ stats.processing }}</div>
                <div class="stat-label">处理中</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value completed">{{ stats.completed }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
        
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
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
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { repairApi, staffApi } from '@/api'
import { Camera } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))
const changing = ref(false)
const saving = ref(false)
const passwordFormRef = ref()
const infoFormRef = ref()

const infoForm = reactive({
  real_name: staffInfo.value.real_name || '',
  gender: staffInfo.value.gender || 'male',
  phone: staffInfo.value.phone || ''
})

const infoRules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系方式', trigger: 'blur' }]
}

const stats = ref({ total: 0, pending: 0, processing: 0, completed: 0 })

const passwordForm = reactive({
  new_password: '',
  confirm_password: ''
})

const validateConfirm = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
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
  await loadStats()
  await loadStaffInfo()
})

const loadStaffInfo = async () => {
  try {
    const res = await staffApi.get(staffInfo.value.id)
    const data = res.code ? res.data : res
    if (data) {
      staffInfo.value = data
      infoForm.real_name = data.real_name || ''
      infoForm.gender = data.gender || 'male'
      infoForm.phone = data.phone || ''
      localStorage.setItem('staffInfo', JSON.stringify(data))
    }
  } catch (error) {
    console.error(error)
  }
}

const saveInfo = async () => {
  await infoFormRef.value.validate()
  saving.value = true
  try {
    await staffApi.update(staffInfo.value.id, infoForm)
    ElMessage.success('保存成功')
    await loadStaffInfo()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await repairApi.orderStatistics()
    stats.value = {
      total: res.total || 0,
      pending: res.pending || 0,
      processing: res.accepted || 0,
      completed: res.completed || 0
    }
  } catch (error) {
    console.error(error)
  }
}

const changePassword = async () => {
  await passwordFormRef.value.validate()
  changing.value = true
  try {
    await staffApi.update(staffInfo.value.id, { password: passwordForm.new_password })
    ElMessage.success('密码修改成功')
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '密码修改失败')
  } finally {
    changing.value = false
  }
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
      await staffApi.update(staffInfo.value.id, { avatar: result.url })
      staffInfo.value.avatar = result.url
      localStorage.setItem('staffInfo', JSON.stringify(staffInfo.value))
      ElMessage.success('头像上传成功')
    } else {
      ElMessage.error(result.error || '头像上传失败')
    }
  } catch (error) {
    ElMessage.error('头像上传失败')
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

        .avatar-overlay {
          position: absolute;
          top: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          color: #fff;
          opacity: 0;
          transition: opacity 0.3s;

          .el-icon {
            font-size: 24px;
          }

          span {
            font-size: 12px;
            margin-top: 4px;
          }
        }

        &:hover .avatar-overlay {
          opacity: 1;
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
  }
  
  .stat-item {
    text-align: center;
    padding: 20px;
    
    .stat-value {
      font-size: 32px;
      font-weight: bold;
      color: #409eff;
      
      &.pending { color: #e6a23c; }
      &.processing { color: #409eff; }
      &.completed { color: #67c23a; }
    }
    
    .stat-label {
      color: #666;
      margin-top: 5px;
    }
  }
}
</style>
