<!--
我的工单页面

该组件用于维修人员查看和管理自己的工单，包括：
- 工单列表展示（进行中、待审核、已完成）
- 查看工单详情
- 完成维修任务
- 转派工单

作者：范广宇
创建日期：2026年
-->
<template>
  <div class="page">
    <div class="page-header"><h2>我的工单</h2></div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane name="WAITING">
          <template #label>
            待接单<el-badge v-if="tabCounts.WAITING > 0" :value="tabCounts.WAITING" style="margin-left:4px;" />
          </template>
        </el-tab-pane>
        <el-tab-pane name="IN_PROGRESS">
          <template #label>
            进行中<el-badge v-if="tabCounts.IN_PROGRESS > 0" :value="tabCounts.IN_PROGRESS" style="margin-left:4px;" />
          </template>
        </el-tab-pane>
        <el-tab-pane name="PENDING_ADMIN_CLOSE">
          <template #label>
            待审核<el-badge v-if="tabCounts.PENDING_ADMIN_CLOSE > 0" :value="tabCounts.PENDING_ADMIN_CLOSE" style="margin-left:4px;" />
          </template>
        </el-tab-pane>
        <el-tab-pane name="completed">
          <template #label>
            已完成<el-badge v-if="tabCounts.CLOSED > 0" :value="tabCounts.CLOSED" style="margin-left:4px;" />
          </template>
        </el-tab-pane>
      </el-tabs>
      <el-table :data="tableData" stripe v-loading="loading" style="margin-top: 16px;">
        <el-table-column prop="repair_no" label="报修编号" width="160" />
        <el-table-column prop="equipment_name" label="设备名称" min-width="120" />
        <el-table-column label="位置" min-width="180">
          <template #default="{ row }">{{ [row.location, row.building, row.floor ? row.floor + '层' : '', row.room].filter(Boolean).join(' · ') || '-' }}</template>
        </el-table-column>
        <el-table-column label="报修人" width="100">
          <template #default="{ row }">{{ row.status !== 'WAITING' ? (row.user_name || '-') : '***' }}</template>
        </el-table-column>
        <el-table-column label="联系电话" width="130">
          <template #default="{ row }">{{ row.status !== 'WAITING' ? (row.user_phone || '-') : '***' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.is_transferred && row.status === 'WAITING'" type="warning" size="small">转让单</el-tag>
            <el-tag v-else :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="报修时间" width="165">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button v-if="activeTab === 'WAITING'" type="success" link size="small" @click="handleAccept(row)">接单</el-button>
            <template v-if="activeTab === 'IN_PROGRESS'">
              <el-button type="warning" link size="small" @click="handleTransfer(row)">转派</el-button>
              <el-button type="success" link size="small" @click="handleComplete(row)">完成</el-button>
            </template>
            <template v-else-if="activeTab === 'PENDING_ADMIN_CLOSE'">
              <el-tag v-if="row.status === 'PENDING_ADMIN_CLOSE'" type="warning" size="small">待审核</el-tag>
              <el-tag v-else-if="row.status === 'CLOSED'" type="success" size="small">已通过</el-tag>
              <el-tag v-else-if="row.status === 'IN_PROGRESS'" type="danger" size="small">已驳回</el-tag>
            </template>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <el-dialog v-model="viewVisible" title="工单详情" width="650px">
      <el-descriptions :column="2" border :label-width="110" v-if="currentOrder">
        <el-descriptions-item label="报修编号">{{ currentOrder.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="状态"><el-tag :type="getStatusType(currentOrder.status)">{{ getStatusText(currentOrder.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentOrder.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentOrder.equipment_type_name || (isNaN(currentOrder.equipment_type) ? currentOrder.equipment_type : '-') }}</el-descriptions-item>
        <el-descriptions-item label="报修人">{{ currentOrder.status !== 'WAITING' ? (currentOrder.user_name || '-') : '接单后可见' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentOrder.status !== 'WAITING' ? (currentOrder.user_phone || '-') : '接单后可见' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="设备位置" :span="2">
          <template v-if="currentOrder.location || currentOrder.building || currentOrder.floor || currentOrder.room">
            <el-tag size="small" type="info" v-if="currentOrder.location" style="margin-right:4px;">{{ currentOrder.location }}</el-tag>
            <el-tag size="small" type="info" v-if="currentOrder.building" style="margin-right:4px;">{{ currentOrder.building }}</el-tag>
            <el-tag size="small" type="warning" v-if="currentOrder.floor" style="margin-right:4px;">{{ currentOrder.floor }}层</el-tag>
            <el-tag size="small" type="success" v-if="currentOrder.room">{{ currentOrder.room }}</el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="详细位置">{{ currentOrder.location_detail || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="故障数量">{{ currentOrder.fault_count || 1 }}</el-descriptions-item>
        <el-descriptions-item label="现场照片" :span="2">
          <div v-if="currentOrder.scene_photos && currentOrder.scene_photos.length > 0" class="scene-photos">
            <el-image v-for="(photo, idx) in currentOrder.scene_photos" :key="idx" :src="photo" class="photo-item" fit="cover" :preview-src-list="currentOrder.scene_photos" :initial-index="idx" preview-teleported />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentOrder.description || '无' }}</el-descriptions-item>
        <template v-if="currentOrder.status === 'PENDING_ADMIN_CLOSE' || currentOrder.status === 'CLOSED'">
          <el-descriptions-item label="维修员">{{ currentOrder.staff_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="维修耗时">{{ currentOrder.actual_duration ? formatDuration(currentOrder.actual_duration) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="维修说明" :span="2">{{ currentOrder.remark || '无' }}</el-descriptions-item>
          <el-descriptions-item label="维修照片" :span="2">
              <div v-if="currentOrder.repair_photos && currentOrder.repair_photos.length > 0" class="scene-photos">
                <el-image v-for="(photo, idx) in currentOrder.repair_photos" :key="idx" :src="photo" class="photo-item" fit="cover" :preview-src-list="currentOrder.repair_photos" :initial-index="idx" preview-teleported />
              </div>
              <span v-else>无</span>
            </el-descriptions-item>
          <el-descriptions-item label="使用备件" :span="2">
            <div v-if="currentOrder.spare_parts_info && currentOrder.spare_parts_info.length > 0">
              <el-table :data="currentOrder.spare_parts_info" size="small" style="width:100%;">
                <el-table-column prop="spare_part_name" label="备件名称" />
                <el-table-column prop="quantity" label="使用数量" width="100" />
              </el-table>
            </div>
            <span v-else>无</span>
          </el-descriptions-item>
        </template>
      </el-descriptions>
      <template #footer><el-button @click="viewVisible = false">关闭</el-button></template>
    </el-dialog>

    <el-dialog v-model="completeVisible" title="完成维修" width="580px">
      <el-form ref="completeFormRef" :model="completeForm" :rules="completeRules" label-width="100px">
        <el-form-item label="维修照片">
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
              <div class="el-upload__tip">最多上传5张图片</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="使用备件">
          <el-select v-model="completeForm.selectedSpareIds" multiple placeholder="选择使用的备件（可多选）" style="width:100%;" @change="handleSparePartChange">
            <el-option v-for="item in sparePartList" :key="item.id" :label="`${item.name} (库存:${item.quantity})`" :value="item.id" />
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
          <el-tag type="info" size="large">{{ calculatedDuration }}</el-tag>
          <span style="margin-left:8px;color:#999;">系统自动计算，从接单到提交</span>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="completeVisible = false">取消</el-button><el-button type="primary" @click="submitComplete" :loading="completing">提交完成</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { repairApi, sparePartApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const activeTab = ref('IN_PROGRESS')
const tabCounts = ref({ WAITING: 0, IN_PROGRESS: 0, PENDING_ADMIN_CLOSE: 0, CLOSED: 0 })
const viewVisible = ref(false)
const completeVisible = ref(false)
const completing = ref(false)
const completeFormRef = ref()
const photoFileList = ref([])
const currentOrder = ref(null)

const completeForm = reactive({ order_id: null, remark: '', selectedSpareIds: [], spareQuantities: {}, scene_photos: [] })
const sparePartList = ref([])
const completeRules = {
  remark: [{ required: true, message: '请输入维修说明', trigger: 'blur' }]
}

const getSparePartName = (id) => { const sp = sparePartList.value.find(s => s.id === id); return sp ? sp.name : '' }
const getSparePartStock = (id) => { const sp = sparePartList.value.find(s => s.id === id); return sp ? sp.quantity : 0 }
const handleSparePartChange = (val) => {
  if (!val || !val.length) return
  val.forEach(id => { if (!completeForm.spareQuantities[id]) completeForm.spareQuantities[id] = 1 })
  Object.keys(completeForm.spareQuantities).forEach(k => { if (!val.includes(parseInt(k))) delete completeForm.spareQuantities[k] })
}

const calculatedDuration = computed(() => {
  if (!currentOrder.value) return '-'
  const start = currentOrder.value.repair_start_time || currentOrder.value.accept_time
  if (!start) return '-'
  try {
    const s = new Date(start).getTime()
    const diffMin = Math.round((Date.now() - s) / 60000)
    return diffMin < 60 ? diffMin + '分钟' : Math.floor(diffMin / 60) + '小时' + (diffMin % 60) + '分'
  } catch { return '-' }
})

onMounted(async () => {
  await waitForStaffInfo()
  loadData()
  loadSparePartList()
})

const waitForStaffInfo = () => {
  return new Promise((resolve) => {
    const check = () => {
      try {
        const info = JSON.parse(localStorage.getItem('staffInfo') || '{}')
        if (info?.id) {
          staffInfo.value = info
          resolve()
        } else {
          setTimeout(check, 50)
        }
      } catch (e) {
        setTimeout(check, 50)
      }
    }
    check()
  })
}

const loadSparePartList = async () => {
  try { const r = await sparePartApi.list({ page_size: 100 }); sparePartList.value = (r.results || []).filter(s => s.quantity > 0) } catch (e) { console.error(e) }
}

const handleTabChange = () => { currentPage.value = 1; loadData() }

const getStatusType = (s) => ({ WAITING:'warning', IN_PROGRESS:'primary', PENDING_ADMIN_CLOSE:'info', CLOSED:'success', REJECTED:'danger' })[s] || 'info'

const getStatusText = (s) => ({ WAITING:'待接单', IN_PROGRESS:'处理中', PENDING_ADMIN_CLOSE:'待验收', CLOSED:'已完成', REJECTED:'已取消' })[s] || s

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''

const formatDuration = (minutes) => {
  if (!minutes) return '-'
  if (minutes < 60) return minutes + '分钟'
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  return m > 0 ? h + '小时' + m + '分' : h + '小时'
}

const parsePhotos = (photoStr) => {
  if (!photoStr) return []
  if (Array.isArray(photoStr)) return photoStr
  if (typeof photoStr === 'string' && photoStr.startsWith('[')) { try { return JSON.parse(photoStr) } catch (e) {} }
  if (typeof photoStr === 'string' && (photoStr.startsWith('data:') || photoStr.startsWith('http'))) return [photoStr]
  return [photoStr]
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (activeTab.value !== 'completed') params.status = activeTab.value
    else params.status = 'CLOSED'

    const [res, statRes] = await Promise.all([
      repairApi.orderList(params),
      repairApi.orderStatistics().catch(() => null)
    ])
    tableData.value = res.results || []
    total.value = res.count || 0

    if (statRes) {
      tabCounts.value = {
        WAITING: statRes.pending || 0,
        IN_PROGRESS: statRes.accepted || 0,
        PENDING_ADMIN_CLOSE: statRes.repairing || 0,
        CLOSED: statRes.completed || 0
      }
    }
  } catch (error) { console.error(error) }
  finally { loading.value = false }
}

const handleView = async (row) => {
  try {
    const res = await repairApi.orderGet(row.id)
    currentOrder.value = res
  } catch (e) {
    currentOrder.value = row
  }
  viewVisible.value = true
}

const handleAccept = async (row) => {
  const info = JSON.parse(localStorage.getItem('staffInfo') || '{}')
  if (!info.is_online) {
    ElMessageBox.alert('当前账号未上线，暂无法接单，请先完成上线操作后再尝试。', '无法接单', {
      confirmButtonText: '我知道了',
      type: 'warning',
    })
    return
  }
  try {
    await repairApi.orderAccept(row.id, {})
    ElMessage.success('接单成功'); activeTab.value = 'IN_PROGRESS'; currentPage.value = 1; loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || '接单失败') }
}

const handleTransfer = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定转让此工单？转让后工单将回流至【报修接单】公共列表，并标记为「转让单」。',
      '确认转让',
      { confirmButtonText: '确定转让', cancelButtonText: '取消', type: 'warning' }
    )
  } catch { return }
  try {
    await repairApi.orderTransfer(row.id, {})
    ElMessage.success('转让成功，工单已回流至待接单池')
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || '转让失败') }
}

const handleComplete = (row) => {
  currentOrder.value = row
  Object.assign(completeForm, { order_id: row.id, remark: '', selectedSpareIds: [], spareQuantities: {}, scene_photos: [] })
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
    await repairApi.orderComplete(completeForm.order_id, {
      scene_photos: completeForm.scene_photos,
      spare_parts: spare_parts,
      remark: completeForm.remark
    })
    ElMessage.success('维修完成，等待管理员审核')
    completeVisible.value = false
    activeTab.value = 'PENDING_ADMIN_CLOSE'; currentPage.value = 1; loadData()
    loadSparePartList()
  } catch (e) { ElMessage.error(e.response?.data?.message || '操作失败') }
  finally { completing.value = false }
}
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; font-size: 22px; color: #303133; }
.scene-photos { display: flex; gap: 8px; flex-wrap: wrap; }
.photo-item { width: 150px; height: 110px; border-radius: 4px; overflow: hidden; flex-shrink: 0; }
</style>
