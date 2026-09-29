<template>
  <div class="page">
    <div class="page-header"><h2>维修记录</h2></div>
    
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索报修编号/设备名称" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>
      
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" min-width="120" />
        <el-table-column label="设备类型" width="100">
          <template #default="{ row }">{{ row.equipment_type_name || (isNaN(row.equipment_type) ? row.equipment_type : '-') }}</template>
        </el-table-column>
        <el-table-column label="设备位置" min-width="140">
          <template #default="{ row }">
            <div>{{ [row.location, row.building, row.floor ? row.floor + '层' : '', row.room].filter(Boolean).join(' · ') || '-' }}</div>
            <div v-if="row.location_detail" style="color: #909399; font-size: 12px;">{{ row.location_detail }}</div>
          </template>
        </el-table-column>
        <el-table-column label="维修时长" width="100">
          <template #default="{ row }">
            <span v-if="row.actual_duration">{{ formatDuration(row.actual_duration) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="完成时间" width="160">
          <template #default="{ row }">{{ formatDate(row.complete_time) }}</template>
        </el-table-column>
        <el-table-column label="审核状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getAuditStatusType(row.status)">{{ getAuditStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
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
    
    <el-dialog v-model="viewVisible" title="维修记录详情" width="800px">
      <el-descriptions :column="2" border :label-width="110" v-if="currentItem">
        <el-divider content-position="left">报修信息</el-divider>
        <el-descriptions-item label="报修编号">{{ currentItem.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="工单状态">
          <el-tag :type="getOrderStatusType(currentItem.status)">{{ getOrderStatusText(currentItem.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentItem.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentItem.equipment_type_name || (isNaN(currentItem.equipment_type) ? currentItem.equipment_type : '-') }}</el-descriptions-item>
        <el-descriptions-item label="报修人">{{ currentItem.user_name }}</el-descriptions-item>
        <el-descriptions-item label="报修电话">{{ currentItem.user_phone || '-' }}</el-descriptions-item>
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
          <div v-if="currentItem.scene_photos && currentItem.scene_photos.length > 0" style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-image v-for="(photo, idx) in currentItem.scene_photos" :key="idx" :src="photo" style="width:100px;height:100px;" fit="cover" :preview-src-list="currentItem.scene_photos" :initial-index="idx" preview-teleported />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentItem.description || '无' }}</el-descriptions-item>
        
        <el-divider content-position="left">维修记录</el-divider>
        <el-descriptions-item label="完成时间">{{ formatDate(currentItem.complete_time) }}</el-descriptions-item>
        <el-descriptions-item label="维修时长">
          <span v-if="currentItem.actual_duration">{{ formatDuration(currentItem.actual_duration) }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="审核状态">
          <el-tag :type="getAuditStatusType(currentItem.status)">{{ getAuditStatusText(currentItem.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审核回复">{{ currentItem.review_reply || '-' }}</el-descriptions-item>
        <el-descriptions-item label="维修说明" :span="2">{{ currentItem.remark || '无' }}</el-descriptions-item>
        <el-descriptions-item label="维修照片" :span="2">
          <div v-if="currentItem.repair_photos && currentItem.repair_photos.length > 0" style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-image v-for="(photo, idx) in currentItem.repair_photos" :key="idx" :src="photo" style="width:100px;height:100px;" fit="cover" :preview-src-list="currentItem.repair_photos" :initial-index="idx" preview-teleported />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="使用备件" :span="2">
          <div v-if="currentItem.spare_parts_info && currentItem.spare_parts_info.length > 0">
            <el-tag v-for="part in currentItem.spare_parts_info" :key="part.spare_part_name" size="small" style="margin-right:6px;margin-bottom:4px;">{{ part.spare_part_name }} × {{ part.quantity }}</el-tag>
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { repairApi } from '@/api'
import { ElMessage } from 'element-plus'
import { EventBus, Events } from '@/utils/eventBus'

const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const viewVisible = ref(false)
const currentItem = ref(null)

onMounted(async () => {
  await loadData()
  EventBus.on(Events.RECORD_DELETED, loadData)
  EventBus.on(Events.DATA_REFRESH, loadData)
})

onUnmounted(() => {
  EventBus.off(Events.RECORD_DELETED, loadData)
  EventBus.off(Events.DATA_REFRESH, loadData)
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await repairApi.recordList(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
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

const getAuditStatusType = (status) => ({ PENDING_ADMIN_CLOSE:'warning', CLOSED:'success', IN_PROGRESS:'danger' })[status] || 'info'

const getAuditStatusText = (status) => ({ PENDING_ADMIN_CLOSE:'待审核', CLOSED:'已通过', IN_PROGRESS:'已驳回' })[status] || status

const getOrderStatusType = (status) => ({ WAITING:'warning', IN_PROGRESS:'primary', PENDING_ADMIN_CLOSE:'info', CLOSED:'success', REJECTED:'danger' })[status] || 'info'

const getOrderStatusText = (status) => ({ WAITING:'待接单', IN_PROGRESS:'处理中', PENDING_ADMIN_CLOSE:'待验收', CLOSED:'已完成', REJECTED:'已取消' })[status] || status

const formatDate = (dateStr) => { if (!dateStr) return ''; return new Date(dateStr).toLocaleString('zh-CN') }

const formatDuration = (minutes) => {
  if (!minutes) return '-'
  if (minutes < 60) return `${Math.round(minutes)}分钟`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`
}
</script>

<style scoped lang="scss">
.search-bar { display: flex; align-items: center; margin-bottom: 20px; }
</style>
