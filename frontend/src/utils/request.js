import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

function clampPageSize(value) {
  const n = Number(value)
  if (!Number.isFinite(n)) return undefined
  if (n <= 0) return 20
  // 强制禁止超大分页参数（如 1000/10000），后端也会限制，但前端先拦截可明显减少超时
  return Math.min(n, 100)
}

function normalizePaginationParams(params) {
  if (!params || typeof params !== 'object') return params
  const next = { ...params }
  if ('page_size' in next) {
    const clamped = clampPageSize(next.page_size)
    if (clamped !== undefined) next.page_size = clamped
  }
  return next
}

function getCurrentPortal() {
  const path = window.location.pathname
  if (path.startsWith('/admin')) return 'admin'
  if (path.startsWith('/staff')) return 'staff'
  if (path.startsWith('/user')) return 'user'
  return localStorage.getItem('currentPortal') || ''
}

function getTokenByPortal(portal) {
  if (portal === 'user') return localStorage.getItem('userToken') || ''
  if (portal === 'staff') return localStorage.getItem('staffToken') || ''
  if (portal === 'admin') return localStorage.getItem('adminToken') || ''
  return ''
}

function clearAuthByPortal(portal) {
  if (portal === 'user') {
    localStorage.removeItem('userToken')
    localStorage.removeItem('userInfo')
  } else if (portal === 'staff') {
    localStorage.removeItem('staffToken')
    localStorage.removeItem('staffInfo')
  } else if (portal === 'admin') {
    localStorage.removeItem('adminToken')
    localStorage.removeItem('adminInfo')
  }
}

request.interceptors.request.use(
  config => {
    const portal = getCurrentPortal()
    const token = getTokenByPortal(portal)
    if (token) {
      config.headers['Authorization'] = `Token ${token}`
    }
    if (config?.params) {
      config.params = normalizePaginationParams(config.params)
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

function isTimeoutError(error) {
  const msg = String(error?.message || '')
  return error?.code === 'ECONNABORTED' || msg.includes('timeout')
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

request.interceptors.response.use(
  response => {
    return response.data
  },
  async error => {
    const config = error?.config || {}

    // 超时/偶发网络抖动：对 GET 请求做一次重试，避免用户看到空白页
    if (config && config.method === 'get' && isTimeoutError(error)) {
      config.__retryCount = config.__retryCount || 0
      if (config.__retryCount < 1) {
        config.__retryCount += 1
        await sleep(300)
        return request(config)
      }
    }

    if (error.response && error.response.status === 401) {
      const portal = getCurrentPortal()
      clearAuthByPortal(portal)
      window.location.href = '/login'
      return Promise.reject(error)
    }
    ElMessage.error(error.response?.data?.message || error.message || '请求失败')
    return Promise.reject(error)
  }
)

export default request
