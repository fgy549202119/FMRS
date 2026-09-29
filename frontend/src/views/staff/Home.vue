<!--
维修人员工作台

该组件是维修人员的工作台首页，包括：
- 工单统计信息（待接单、进行中、待审核、已完成）
- 进行中工单列表
- 工单快捷操作

作者：范广宇
创建日期：2026年
-->
<template>
  <div class="staff-home">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待接单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon><Tools /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.repairing }}</div>
            <div class="stat-label">维修中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending_review }}</div>
            <div class="stat-label">待审核</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>当前进行中的工单</span>
              <div class="header-actions">
                <el-button 
                  :type="isOnline ? 'danger' : 'success'" 
                  @click="toggleOnlineStatus"
                  style="margin-right: 15px;"
                >
                  {{ isOnline ? '离线' : '上线' }}
                </el-button>
                <el-button type="primary" link @click="$router.push('/staff/my-orders')">查看我的工单</el-button>
              </div>
            </div>
          </template>
          
          <div v-if="currentOrder" class="current-order">
            <div class="order-info">
              <div class="order-header">
                <span class="order-no">{{ currentOrder.repair_no }}</span>
                <el-tag :type="getStatusType(currentOrder.status)" size="large">{{ getStatusText(currentOrder.status) }}</el-tag>
              </div>
              
              <el-descriptions :column="2" border style="margin-top: 15px;">
                <el-descriptions-item label="设备名称">{{ currentOrder.equipment_name }}</el-descriptions-item>
                <el-descriptions-item label="设备类型">{{ currentOrder.equipment_type_name || (isNaN(currentOrder.equipment_type) ? currentOrder.equipment_type : '-') }}</el-descriptions-item>
                <el-descriptions-item label="设备位置" :span="2">
                  <span>{{ [currentOrder.location, currentOrder.building, currentOrder.floor ? currentOrder.floor + '层' : '', currentOrder.room].filter(Boolean).join(' · ') || '-' }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="报修人">{{ currentOrder.user_name }}</el-descriptions-item>
                <el-descriptions-item label="联系电话">{{ currentOrder.user_phone || '未填写' }}</el-descriptions-item>
                <el-descriptions-item label="故障描述" :span="2">
                  <div class="fault-description">{{ currentOrder.description || '无' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="报修时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="getStatusType(currentOrder.status)" size="small">
                    {{ getStatusText(currentOrder.status) }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
              
              <div v-if="currentOrder.scene_photos && currentOrder.scene_photos.length > 0" class="scene-photos">
                <div class="photos-label">现场照片：</div>
                <div class="photos-grid">
                  <el-image 
                    v-for="(photo, index) in currentOrder.scene_photos" 
                    :key="index"
                    :src="photo" 
                    :preview-src-list="currentOrder.scene_photos"
                    :initial-index="index"
                    class="photo-item"
                    fit="cover"
                    preview-teleported
                  />
                </div>
              </div>
            </div>
            
            <div class="timer-section" v-if="currentOrder.status === 'IN_PROGRESS'">
              <div class="timer-display">
                <div class="timer-label">维修计时</div>
                <div class="timer-value">{{ formattedTime }}</div>
                <div class="timer-start">开始时间: {{ formatDate(currentOrder.repair_start_time) }}</div>
              </div>
              <div class="timer-actions">
                <el-button type="warning" size="large" @click="handleTransfer">转派</el-button>
                <el-button type="success" size="large" @click="handleComplete" :loading="completing">完成维修</el-button>
              </div>
            </div>
          </div>
          
          <el-empty v-else description="暂无进行中的工单" />
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待处理工单</span>
              <el-badge :value="pendingOrders.length" type="warning" />
            </div>
          </template>
          
          <div class="pending-list">
            <div 
              v-for="order in pendingOrders" 
              :key="order.id" 
              class="pending-item"
              @click="showOrderDetail(order)"
            >
              <div class="pending-info">
                <div class="pending-header">
                  <span class="pending-no">{{ order.repair_no }}</span>
                </div>
                <div class="pending-equipment">
                  <el-icon><Monitor /></el-icon> {{ order.equipment_name }}
                </div>
                <div class="pending-location">
                  <el-icon><Location /></el-icon> {{ [order.location, order.building, order.floor ? order.floor + '层' : '', order.room].filter(Boolean).join(' · ') || '-' }}
                </div>
                <div class="pending-desc">{{ order.description || '无故障描述' }}</div>
              </div>
              <el-button type="primary" size="small" @click.stop="handleAccept(order)">接单</el-button>
            </div>
            
            <el-empty v-if="pendingOrders.length === 0" description="暂无待处理工单" :image-size="60" />
          </div>
        </el-card>
        
        <el-card style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>今日统计</span>
            </div>
          </template>
          
          <div class="today-stats">
            <div class="today-item">
              <span class="today-label">完成工单</span>
              <span class="today-value">{{ todayStats.completed }}</span>
            </div>
            <div class="today-item">
              <span class="today-label">维修时长</span>
              <span class="today-value">{{ todayStats.duration > 0 ? formatDuration(todayStats.duration) : '暂无' }}</span>
            </div>
            <div class="today-item">
              <span class="today-label">平均评分</span>
              <span class="today-value">{{ todayStats.rating > 0 ? todayStats.rating + '分' : '暂无评分' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-dialog v-model="orderDetailVisible" title="工单详情" width="600px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="报修编号">{{ selectedOrder.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ selectedOrder.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ selectedOrder.equipment_type_name || (isNaN(selectedOrder.equipment_type) ? selectedOrder.equipment_type : '-') }}</el-descriptions-item>
        <el-descriptions-item label="设备位置" :span="2">{{ [selectedOrder.location, selectedOrder.building, selectedOrder.floor ? selectedOrder.floor + '层' : '', selectedOrder.room].filter(Boolean).join(' · ') || '-' }}</el-descriptions-item>
        <el-descriptions-item label="报修人">接单后可见</el-descriptions-item>
        <el-descriptions-item label="联系电话">接单后可见</el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ selectedOrder.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间" :span="2">{{ formatDate(selectedOrder.created_at) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="orderDetailVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAccept(selectedOrder)">接单</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="completeVisible" title="完成维修" width="600px">
      <el-form :model="completeForm" :rules="completeRules" ref="completeFormRef" label-width="100px">
        <el-form-item label="现场照片">
          <el-upload
            class="photo-uploader"
            action="/api/upload/"
            :data="{ type: 'repair' }"
            list-type="picture-card"
            :file-list="photoFileList"
            :on-success="handlePhotoSuccess"
            :on-remove="handlePhotoRemove"
            :limit="5"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">最多上传5张现场照片</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="使用备件">
          <el-select v-model="completeForm.selectedSpareIds" multiple placeholder="选择使用的备件" style="width: 100%;" @change="handleSparePartChange">
            <el-option v-for="item in sparePartList" :key="item.id" :label="`${item.name} (库存: ${item.quantity})`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="completeForm.selectedSpareIds && completeForm.selectedSpareIds.length > 0" label="使用数量">
          <div style="width:100%;">
            <div v-for="spId in completeForm.selectedSpareIds" :key="spId" style="display:flex;align-items:center;margin-bottom:8px;gap:8px;">
              <span style="min-width:160px;">{{ getSparePartName(spId) }}</span>
              <el-input-number v-model="completeForm.spareQuantities[spId]" :min="1" :max="getSparePartStock(spId)" size="small" controls-position="right" />
              <span style="color:#909399;font-size:12px;">库存: {{ getSparePartStock(spId) }}</span>
            </div>
          </div>
        </el-form-item>
        <el-form-item prop="remark" label="维修说明">
          <el-input v-model="completeForm.remark" type="textarea" :rows="4" placeholder="请详细描述维修过程和结果" />
        </el-form-item>
        <el-form-item label="维修耗时">
          <el-input :value="formattedTime" disabled />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="completeVisible = false">取消</el-button>
        <el-button type="primary" @click="submitComplete" :loading="completing">提交完成</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="transferVisible" title="转让工单" width="400px">
      <el-alert type="warning" :closable="false" style="margin-bottom:16px;">
        <template #title>确定转让此工单？转让后工单将回流至【报修接单】公共列表，并标记为「转让单」</template>
      </el-alert>
      <template #footer>
        <el-button @click="transferVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTransfer" :loading="transferring">确认转让</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { repairApi, staffApi, sparePartApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Tools, Document, CircleCheck, Plus, Location, Monitor } from '@element-plus/icons-vue'

const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))
const stats = ref({ pending: 0, repairing: 0, pending_review: 0, completed: 0 })
const pendingOrders = ref([])
const currentOrder = ref(null)
const todayStats = ref({ completed: 0, duration: 0, rating: 5.0 })
const isOnline = ref(staffInfo.value.is_online !== false)

const orderDetailVisible = ref(false)
const selectedOrder = ref(null)

const completeVisible = ref(false)
const completing = ref(false)
const completeFormRef = ref()
const completeForm = reactive({
  scene_photos: [],
  selectedSpareIds: [],
  spareQuantities: {},
  remark: ''
})
const photoFileList = ref([])
const sparePartList = ref([])

const completeRules = {
  remark: [{ required: true, message: '请输入维修说明', trigger: 'blur' }]
}

const transferVisible = ref(false)
const transferring = ref(false)
const staffList = ref([])

const timerSeconds = ref(0)
let timerInterval = null

const formattedTime = computed(() => {
  const hours = Math.floor(timerSeconds.value / 3600)
  const minutes = Math.floor((timerSeconds.value % 3600) / 60)
  const seconds = timerSeconds.value % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

onMounted(async () => {
  await loadStaffList()
  await loadSparePartList()
  await loadData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopTimer()
  stopAutoRefresh()
})

let refreshInterval = null

const startAutoRefresh = () => {
  refreshInterval = setInterval(() => {
    loadData(false)
  }, 30000)
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
}

const loadStaffList = async () => {
  try {
    const res = await staffApi.list({ page_size: 100 })
    staffList.value = (res.results || []).filter(s => s.id !== staffInfo.value.id)
  } catch (error) {
    console.error(error)
  }
}

const loadSparePartList = async () => {
  try {
    const res = await sparePartApi.list({ page_size: 100 })
    sparePartList.value = (res.results || []).filter(s => s.quantity > 0)
  } catch (error) {
    console.error(error)
  }
}

const loadData = async (showLoading = true) => {
  try {
    const [orderRes, allOrdersRes, statsRes] = await Promise.all([
      repairApi.orderList({ page_size: 20 }),
      repairApi.orderList({ status: 'WAITING', page_size: 10 }),
      repairApi.orderStatistics().catch(e => { console.error('获取统计数据失败:', e); return null })
    ])

    const orders = orderRes.results || []
    pendingOrders.value = allOrdersRes.results || []

    if (statsRes) {
      stats.value = {
        pending: statsRes.pending || 0,
        repairing: statsRes.accepted || 0,
        pending_review: statsRes.repairing || 0,
        completed: statsRes.completed || 0
      }
      todayStats.value = {
        completed: statsRes.today_completed || 0,
        duration: statsRes.today_duration || 0,
        rating: statsRes.today_avg_rating || 0
      }
    } else {
      stats.value = {
        pending: pendingOrders.value.length,
        repairing: orders.filter(o => o.status === 'IN_PROGRESS').length,
        pending_review: orders.filter(o => o.status === 'PENDING_ADMIN_CLOSE').length,
        completed: orders.filter(o => o.status === 'CLOSED').length
      }
    }

    const inProgress = orders.find(o => o.status === 'IN_PROGRESS')
    if (inProgress) {
      currentOrder.value = inProgress
      if (inProgress.repair_start_time) {
        const startTime = new Date(inProgress.repair_start_time).getTime()
        timerSeconds.value = Math.floor((Date.now() - startTime) / 1000)
        startTimer()
      }
    } else {
      currentOrder.value = null
      stopTimer()
    }
  } catch (error) {
    console.error(error)
  }
}

const startTimer = () => {
  stopTimer()
  timerInterval = setInterval(() => {
    timerSeconds.value++
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const showOrderDetail = (order) => {
  selectedOrder.value = order
  orderDetailVisible.value = true
}

const handleAccept = async (order) => {
  if (!isOnline.value) {
    ElMessageBox.alert('当前账号未上线，暂无法接单，请先完成上线操作后再尝试。', '无法接单', {
      confirmButtonText: '我知道了',
      type: 'warning',
    })
    return
  }
  try {
    await ElMessageBox.confirm('确定接单吗？接单后请及时处理', '提示', { type: 'info' })
    await repairApi.orderAccept(order.id, {})
    ElMessage.success('接单成功')
    orderDetailVisible.value = false
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      const msg = error.response?.data?.message || error.message || '未知错误'
      if (msg.includes('已被其他维修员接单')) {
        await ElMessageBox.alert(msg, '接单失败', { type: 'warning', confirmButtonText: '我知道了' })
        await loadData()
      } else {
        ElMessage.error('接单失败: ' + msg)
      }
    }
  }
}

const handleTransfer = () => {
  transferVisible.value = true
}

const submitTransfer = async () => {
  if (!currentOrder.value) return
  transferring.value = true
  try {
    await repairApi.orderTransfer(currentOrder.value.id, {})
    ElMessage.success('转让成功，工单已回流至接单池')
    transferVisible.value = false
    currentOrder.value = null
    stopTimer()
    await loadData()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '转让失败')
  } finally {
    transferring.value = false
  }
}

const getSparePartName = (id) => { const sp = sparePartList.value.find(s => s.id === id); return sp ? sp.name : '' }
const getSparePartStock = (id) => { const sp = sparePartList.value.find(s => s.id === id); return sp ? sp.quantity : 0 }
const handleSparePartChange = (val) => {
  if (!val || !val.length) return
  val.forEach(id => { if (!completeForm.spareQuantities[id]) completeForm.spareQuantities[id] = 1 })
  Object.keys(completeForm.spareQuantities).forEach(k => { if (!val.includes(parseInt(k))) delete completeForm.spareQuantities[k] })
}

const handleComplete = () => {
  completeForm.scene_photos = []
  completeForm.selectedSpareIds = []
  completeForm.spareQuantities = {}
  completeForm.remark = ''
  photoFileList.value = []
  completeVisible.value = true
}

const handlePhotoSuccess = (response, file, fileList) => {
  if (response.url) {
    completeForm.scene_photos.push(response.url)
    ElMessage.success('图片上传成功')
  }
}

const handlePhotoRemove = (file, fileList) => {
  const url = file.response?.url || file.url
  const index = completeForm.scene_photos.indexOf(url)
  if (index > -1) {
    completeForm.scene_photos.splice(index, 1)
  }
}

const submitComplete = async () => {
  if (completeForm.selectedSpareIds && completeForm.selectedSpareIds.length > 0) {
    for (const spId of completeForm.selectedSpareIds) {
      const qty = completeForm.spareQuantities[spId]
      const stock = getSparePartStock(spId)
      if (!qty || qty < 1) { ElMessage.error('使用数量不能小于1'); return }
      if (qty > stock) { ElMessage.error(`备件「${getSparePartName(spId)}」使用数量(${qty})超过库存(${stock})，请调整`); return }
    }
  }
  await completeFormRef.value.validate()
  completing.value = true
  
  try {
    const spare_parts = (completeForm.selectedSpareIds || []).map(id => ({ id, quantity: completeForm.spareQuantities[id] || 1 }))
    await repairApi.orderComplete(currentOrder.value.id, {
      scene_photos: completeForm.scene_photos,
      spare_parts: spare_parts,
      remark: completeForm.remark
    })
    
    ElMessage.success('维修完成，等待审核')
    stopTimer()
    completeVisible.value = false
    currentOrder.value = null
    await loadData()
    await loadSparePartList()
    
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    completing.value = false
  }
}

const getStatusType = (status) => {
  const map = { WAITING: 'warning', IN_PROGRESS: 'primary', PENDING_ADMIN_CLOSE: 'info', CLOSED: 'success', REJECTED: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { WAITING: '待接单', IN_PROGRESS: '处理中', PENDING_ADMIN_CLOSE: '待验收', CLOSED: '已完成', REJECTED: '已取消' }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDuration = (minutes) => {
  if (!minutes) return '0分钟'
  if (minutes < 60) return `${Math.round(minutes)}分钟`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`
}

const toggleOnlineStatus = async () => {
  const newStatus = !isOnline.value
  try {
    await staffApi.update(staffInfo.value.id, {
      is_online: newStatus,
      status: newStatus ? 'online' : 'offline'
    })
    isOnline.value = newStatus
    staffInfo.value.is_online = newStatus
    staffInfo.value.status = newStatus ? 'online' : 'offline'
    localStorage.setItem('staffInfo', JSON.stringify(staffInfo.value))
    ElMessage.success(newStatus ? '已上线，可以接收新工单' : '已离线，将不会接收新工单')
  } catch (error) {
    ElMessage.error('状态更新失败: ' + (error.response?.data?.message || '未知错误'))
  }
}
</script>

<style scoped lang="scss">
.staff-home {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #fff;
    font-size: 28px;
  }
  
  .stat-info {
    margin-left: 20px;
    
    .stat-value {
      font-size: 28px;
      font-weight: bold;
    }
    
    .stat-label {
      color: #666;
      margin-top: 5px;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .header-actions {
    display: flex;
    align-items: center;
  }
}

.current-order {
  .order-info {
    .order-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .order-no {
        font-size: 18px;
        font-weight: bold;
      }
    }
    
    .fault-description {
      max-height: 60px;
      overflow-y: auto;
    }
    
    .scene-photos {
      margin-top: 15px;
      
      .photos-label {
        margin-bottom: 10px;
        color: #666;
      }

      .photos-grid {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }

      .photo-item {
        width: 100px;
        height: 100px;
        border-radius: 4px;
        overflow: hidden;
        flex-shrink: 0;
      }
    }
  }
  
  .timer-section {
    margin-top: 20px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    color: white;
    text-align: center;
    
    .timer-display {
      .timer-label {
        font-size: 14px;
        opacity: 0.9;
      }
      
      .timer-value {
        font-size: 48px;
        font-weight: bold;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
      }
      
      .timer-start {
        font-size: 12px;
        opacity: 0.8;
      }
    }
    
    .timer-actions {
      margin-top: 20px;
      display: flex;
      justify-content: center;
      gap: 15px;
    }
  }
  
  .order-actions {
    margin-top: 20px;
    text-align: center;
    display: flex;
    justify-content: center;
    gap: 15px;
  }
}

.pending-list {
  .pending-item {
    padding: 12px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background 0.3s;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    &:hover {
      background: #f9f9f9;
    }
    
    .pending-info {
      flex: 1;
      
      .pending-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 5px;
        
        .pending-no {
          font-weight: 500;
        }
      }
      
      .pending-equipment, .pending-location {
        font-size: 13px;
        color: #666;
        margin: 3px 0;
        display: flex;
        align-items: flex-start;
        gap: 5px;
        word-break: break-all;
      }
      
      .pending-desc {
        font-size: 12px;
        color: #999;
        margin-top: 5px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 200px;
      }
    }
  }
}

.today-stats {
  .today-item {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .today-label {
      color: #666;
    }
    
    .today-value {
      font-weight: 500;
    }
  }
}

.photo-uploader {
  :deep(.el-upload--picture-card) {
    width: 100px;
    height: 100px;
  }
  :deep(.el-upload-list--picture-card .el-upload-list__item) {
    width: 100px;
    height: 100px;
  }
}
</style>
