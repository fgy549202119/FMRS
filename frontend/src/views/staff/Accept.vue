<!--
报修接单页面

该组件用于维修人员查看和接受待接单的工单，包括：
- 待接单工单列表展示
- 查看工单详情
- 接受工单
- 转派工单

作者：范广宇
创建日期：2026年
-->
<template>
  <div class="page">
    <div class="page-header"><h2>报修接单</h2></div>

    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索报修编号/设备名称" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>

      <el-table :data="sortedTableData" stripe v-loading="loading" :row-class-name="urgentRowClass">
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column label="设备名称" min-width="180">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px;">
              <span :class="{ 'urgent-text': row.is_urgent }">{{ row.equipment_name }}</span>
              <el-tag v-if="row.is_urgent" type="danger" effect="dark" size="small">紧急</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="设备类型" width="120">
          <template #default="{ row }">{{ row.equipment_type_name || (isNaN(row.equipment_type) ? row.equipment_type : '-') }}</template>
        </el-table-column>
        <el-table-column label="现场照片" width="100">
          <template #default="{ row }"><el-image v-if="parsePhotos(row.scene_photos).length > 0" :src="parsePhotos(row.scene_photos)[0]" style="width: 60px; height: 60px;" fit="cover" /><span v-else>-</span></template>
        </el-table-column>
        <el-table-column label="设备位置" min-width="200">
          <template #default="{ row }">
            <span>{{ [row.location, row.building, row.floor ? row.floor + '层' : '', row.room].filter(Boolean).join(' · ') || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.is_transferred && row.status === 'WAITING'" type="warning">转让单</el-tag>
            <el-tag v-else :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="success" link @click="handleAccept(row)" v-if="row.status === 'WAITING'">接单</el-button>
            <el-button type="warning" link @click="handleTransfer(row)" v-if="canTransfer(row)">转让</el-button>
            <el-button type="info" link disabled v-if="row.status === 'IN_PROGRESS' && !canTransfer(row)">已超时</el-button>
            <el-button type="success" link @click="handleComplete(row)" v-if="row.status === 'IN_PROGRESS'">完成</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="viewVisible" title="报修详情" width="650px">
      <el-descriptions :column="2" border :label-width="110" v-if="currentItem">
        <el-descriptions-item label="报修编号">{{ currentItem.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="状态"><el-tag :type="getStatusType(currentItem.status)">{{ getStatusText(currentItem.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentItem.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentItem.equipment_type_name || (isNaN(currentItem.equipment_type) ? currentItem.equipment_type : '-') }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ formatDate(currentItem.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="设备位置" :span="2">
          <template v-if="currentItem.location || currentItem.building || currentItem.floor || currentItem.room">
            <el-tag size="small" type="info" v-if="currentItem.location" style="margin-right:4px;">{{ currentItem.location }}</el-tag>
            <el-tag size="small" type="info" v-if="currentItem.building" style="margin-right:4px;">{{ currentItem.building }}</el-tag>
            <el-tag size="small" type="warning" v-if="currentItem.floor" style="margin-right:4px;">{{ currentItem.floor }}层</el-tag>
            <el-tag size="small" type="success" v-if="currentItem.room">{{ currentItem.room }}</el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="详细位置">{{ currentItem.location_detail || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="故障数量">{{ currentItem.fault_count || 1 }}</el-descriptions-item>
        <el-descriptions-item label="现场照片" :span="2">
          <div v-if="parsePhotos(currentItem.scene_photos).length > 0" class="scene-photos">
            <el-image v-for="(photo, idx) in parsePhotos(currentItem.scene_photos)" :key="idx" :src="photo" class="photo-item" fit="cover" :preview-src-list="parsePhotos(currentItem.scene_photos)" :initial-index="idx" preview-teleported />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentItem.description || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <el-dialog v-model="transferVisible" title="转让工单" width="400px">
      <el-alert type="warning" :closable="false" style="margin-bottom:16px;">
        <template #title>确认将此工单转让？转让后工单将回流至待接单池，状态标记为「转让单」</template>
      </el-alert>
      <el-form :model="transferForm" label-width="80px">
        <el-form-item label="目标维修员">
          <el-select v-model="transferForm.staff_id" filterable style="width:100%" placeholder="请选择目标维修员">
            <el-option v-for="s in staffList" :key="s.id" :label="`${s.real_name}(${s.staff_no})`" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="transferVisible = false">取消</el-button><el-button type="primary" @click="submitTransfer" :loading="transferring">确定转让</el-button></template>
    </el-dialog>

    <el-dialog v-model="completeVisible" title="完成维修" width="500px">
      <el-form :model="completeForm" ref="completeFormRef" label-width="100px">
        <el-form-item label="维修照片">
          <el-upload action="#" list-type="picture-card" :auto-upload="false" :limit="3" :on-change="handlePhotoChange" :on-remove="handlePhotoRemove" :file-list="photoFileList"><el-icon><Plus /></el-icon></el-upload>
          <div style="color:#999;font-size:12px;margin-top:4px;">最多上传3张图片</div>
        </el-form-item>
        <el-form-item label="使用备件">
          <el-select v-model="completeForm.spare_parts" multiple placeholder="选择使用的备件（可多选）" style="width:100%;">
            <el-option v-for="item in sparePartList" :key="item.id" :label="`${item.name} (库存:${item.quantity})`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="维修说明"><el-input v-model="completeForm.remark" type="textarea" :rows="4" placeholder="请输入维修说明" /></el-form-item>
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
import { repairApi, staffApi, sparePartApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const viewVisible = ref(false)
const currentItem = ref(null)

const sortedTableData = computed(() => {
  return [...tableData.value].sort((a, b) => {
    if (a.is_urgent && !b.is_urgent) return -1
    if (!a.is_urgent && b.is_urgent) return 1
    return 0
  })
})

const urgentRowClass = ({ row }) => {
  return row.is_urgent ? 'urgent-row' : ''
}

const transferVisible = ref(false); const transferring = ref(false); const staffList = ref([])
const transferForm = ref({ order_id: null, staff_id: null })

const completeVisible = ref(false); const completing = ref(false); const completeFormRef = ref()
const photoFileList = ref([]); let photoBase64List = []
const sparePartList = ref([])
const completeForm = reactive({ order_id: null, remark: '', spare_parts: [] })

const calculatedDuration = computed(() => {
  if (!currentItem.value) return '-'
  const start = currentItem.value.repair_start_time || currentItem.value.accept_time
  if (!start) return '-'
  try { const s = new Date(start).getTime(); const diffMin = Math.round((Date.now() - s) / 60000); return diffMin < 60 ? diffMin + '分钟' : Math.floor(diffMin / 60) + '小时' + (diffMin % 60) + '分' }
  catch { return '-' }
})

onMounted(async () => { await Promise.all([loadData(), loadStaffList(), loadSparePartList()]) })

const loadSparePartList = async () => {
  try { const r = await sparePartApi.list({ page_size: 100 }); sparePartList.value = (r.results || []).filter(s => s.quantity > 0) } catch (e) { console.error(e) }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value, status: 'WAITING' }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await repairApi.orderList(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) { console.error(error) }
  finally { loading.value = false }
}

const loadStaffList = async () => {
  try { const r = await staffApi.list({ page_size: 100 }); staffList.value = r.results || [] } catch (e) { console.error(e) }
}

const handleView = async (row) => {
  try {
    const res = await repairApi.orderGet(row.id)
    currentItem.value = res
  } catch (e) {
    currentItem.value = row
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
  try { await repairApi.orderAccept(row.id, {}); ElMessage.success('接单成功'); loadData() }
  catch (e) { ElMessage.error(e.response?.data?.message || '接单失败') }
}

const canTransfer = (row) => {
  if (row.status !== 'IN_PROGRESS') return false
  if (!row.accept_time) return false
  try { return (Date.now() - new Date(row.accept_time).getTime()) < 180000 }
  catch { return false }
}

const handleTransfer = async (row) => {
  try { await ElMessageBox.confirm('确定要转让此工单吗？转让后工单将回到待接单池。', '确认转让', { type: 'warning' }) }
  catch { return }
  transferForm.value = { order_id: row.id, staff_id: null }
  transferVisible.value = true
}

const submitTransfer = async () => {
  if (!transferForm.value.staff_id) { ElMessage.warning('请选择维修员'); return }
  transferring.value = true
  try {
    await repairApi.orderTransfer(transferForm.value.order_id, { staff_id: transferForm.value.staff_id })
    ElMessage.success('转派成功，工单已回流至待接单池')
    transferVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || '转派失败') }
  finally { transferring.value = false }
}

const handleComplete = (row) => { currentItem.value = row; Object.assign(completeForm, { order_id: row.id, remark: '', spare_parts: [] }); photoFileList.value = []; photoBase64List = []; completeVisible.value = true }

const handlePhotoChange = (file) => {
  photoFileList.value.push(file)
  const reader = new FileReader()
  reader.onload = (e) => { photoBase64List.push(e.target.result) }
  if (file.raw) reader.readAsDataURL(file.raw)
}

const handlePhotoRemove = (file) => {
  const idx = photoFileList.value.findIndex(f => f.uid === file.uid)
  if (idx > -1) { photoFileList.value.splice(idx, 1); photoBase64List.splice(idx, 1) }
}

const submitComplete = async () => {
  completing.value = true
  try {
    const data = { remark: completeForm.remark || '', spare_parts: completeForm.spare_parts || [] }
    if (photoBase64List.length > 0) data['scene_photo'] = photoBase64List[0]
    if (photoBase64List.length > 1) data['scene_photo[]'] = photoBase64List.slice(1)
    await repairApi.orderComplete(completeForm.order_id, data)
    ElMessage.success('维修完成，等待管理员审核')
    completeVisible.value = false
    loadData()
    loadSparePartList()
  } catch (e) { ElMessage.error(e.response?.data?.message || '操作失败') }
  finally { completing.value = false }
}

const getStatusType = (s) => ({ WAITING:'warning', IN_PROGRESS:'primary', PENDING_ADMIN_CLOSE:'info', CLOSED:'success', REJECTED:'danger' })[s] || 'info'
const getStatusText = (s) => ({ WAITING:'待接单', IN_PROGRESS:'处理中', PENDING_ADMIN_CLOSE:'待验收', CLOSED:'已完成', REJECTED:'已取消' })[s] || s
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''
const parsePhotos = (photos) => {
  if (!photos) return []
  if (Array.isArray(photos)) return photos
  if (typeof photos === 'string') {
    if (photos.startsWith('data:')) return [photos]
    try {
      const parsed = JSON.parse(photos)
      return Array.isArray(parsed) ? parsed : [parsed]
    } catch {}
    if (photos.startsWith('http') || photos.startsWith('/media/') || photos.startsWith('/')) {
      return [photos]
    }
  }
  return []
}
</script>

<style scoped lang="scss">
.search-bar { display: flex; align-items: center; margin-bottom: 20px; }
.scene-photos { display: flex; gap: 8px; flex-wrap: wrap; }
.photo-item { width: 150px; height: 110px; border-radius: 4px; overflow: hidden; flex-shrink: 0; }
.urgent-text { color: #f56c6c; font-weight: bold; }
</style>
<style>
.urgent-row td { color: #f56c6c !important; }
</style>
