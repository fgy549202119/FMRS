<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h2>维修员注册</h2>
      </div>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="账号" prop="staff_no">
          <el-input v-model="form.staff_no" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="form.confirm_password" type="password" placeholder="请确认密码" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
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
        <el-form-item label="联系方式" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%">注册</el-button>
        </el-form-item>
        <el-form-item>
          <span>已有账号？</span>
          <el-button type="text" @click="$router.push('/login')">直接登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { staffApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const formRef = ref()

const form = reactive({
  staff_no: '',
  password: '',
  confirm_password: '',
  real_name: '',
  gender: 'male',
  avatar: '',
  phone: ''
})

const validatePasswordStrength = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else if (!/[a-z]/.test(value)) {
    callback(new Error('密码必须包含小写字母'))
  } else if (!/[A-Z]/.test(value)) {
    callback(new Error('密码必须包含大写字母'))
  } else if (!/\d/.test(value)) {
    callback(new Error('密码必须包含数字'))
  } else if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(value)) {
    callback(new Error('密码必须包含特殊符号'))
  } else {
    callback()
  }
}

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入联系方式'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('手机号格式不正确'))
  } else {
    callback()
  }
}

const formRules = {
  staff_no: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: validatePasswordStrength, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ validator: validatePhone, trigger: 'blur' }]
}

const handleAvatarSuccess = (response) => {
  form.avatar = response.url
}

const handleRegister = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await staffApi.register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    if (error.response && error.response.data) {
      if (error.response.data.message) {
        ElMessage.error(error.response.data.message)
      } else if (error.response.data.code) {
        ElMessage.error(`注册失败：${error.response.data.code}`)
      } else {
        ElMessage.error('注册失败，请检查输入信息')
      }
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #312e81 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 70% 30%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
    animation: bgFloat 20s ease-in-out infinite;
  }

  @keyframes bgFloat {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-2%, -1%); }
  }

  .register-container {
    width: 520px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 40px 36px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
    position: relative;
    z-index: 1;
    animation: fadeInUp 0.5s ease forwards;

    .register-header {
      text-align: center;
      margin-bottom: 32px;

      h2 {
        font-size: 24px;
        color: #1f2937;
        font-weight: 700;
      }
    }

    :deep(.el-form-item__label) {
      font-weight: 500;
      color: #4b5563;
    }

    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 0 0 1px #e5e7eb inset;

      &:hover {
        box-shadow: 0 0 0 1px #d1d5db inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 2px #6366f1 inset;
      }
    }

    :deep(.el-button--primary) {
      height: 44px;
      font-size: 15px;
      background: linear-gradient(135deg, #4f46e5, #6366f1);
      border: none;
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        background: linear-gradient(135deg, #4338ca, #4f46e5);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
      }
    }

    .avatar-uploader {
      :deep(.el-upload) {
        border: 2px dashed #e5e7eb;
        border-radius: 12px;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;

        &:hover {
          border-color: #6366f1;
          background: #eef2ff;
        }
      }

      .avatar {
        width: 100px;
        height: 100px;
        display: block;
        border-radius: 8px;
      }

      .avatar-uploader-icon {
        font-size: 28px;
        color: #9ca3af;
        width: 100px;
        height: 100px;
        line-height: 100px;
        text-align: center;
      }
    }
  }
}
</style>
