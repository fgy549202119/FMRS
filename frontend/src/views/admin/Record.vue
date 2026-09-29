<template>
  <div class="page">
    <div class="page-header"><h2>维修记录管理</h2></div>

    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索报修编号/设备名称" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>

      <el-table :data="tableData" stripe v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column label="设备类型" width="120">
          <template #default="{ row }">{{ row.equipment_type_name || row.equipment_type || '-' }}</template>
        </el-table-column>
        <el-table-column label="设备位置" min-width="160">
          <template #default="{ row }">
            <span>{{ [row.location, row.building, row.floor, row.room].filter(Boolean).join(' ') || '-' }}</span>
            <span v-if="row.location_detail" style="color:#909399;font-size:12px;">（{{ row.location_detail }}）</span>
          </template>
        </el-table-column>
        <el-table-column label="使用备件" min-width="150">
          <template #default="{ row }">
            <span v-if="row.spare_parts_info && row.spare_parts_info.length > 0">
              <el-tag size="small" v-for="(sp, idx) in row.spare_parts_info" :key="idx" style="margin-right:4px; margin-bottom:2px;">
                {{ sp.spare_part_name }}×{{ sp.quantity }}
              </el-tag>
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="staff_name" label="维修员" width="100" />
        <el-table-column label="维修时长" width="100">
          <template #default="{ row }">{{ formatDuration(row.actual_duration) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="报修时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="viewVisible" title="维修记录详情" width="750px">
      <el-descriptions :column="2" border :label-width="110" v-if="currentRecord">
        <el-descriptions-item label="报修编号">{{ currentRecord.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="状态"><el-tag :type="getStatusType(currentRecord.status)">{{ getStatusText(currentRecord.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentRecord.equipment_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentRecord.equipment_type_name || currentRecord.equipment_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="报修人">{{ currentRecord.user_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="报修电话">{{ currentRecord.user_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ formatDate(currentRecord.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="报修位置" :span="2">
          <template v-if="currentRecord.location || currentRecord.building || currentRecord.floor || currentRecord.room">
            <el-tag size="small" type="info" v-if="currentRecord.location" style="margin-right:4px;">{{ currentRecord.location }}</el-tag>
            <el-tag size="small" type="info" v-if="currentRecord.building" style="margin-right:4px;">{{ currentRecord.building }}</el-tag>
            <el-tag size="small" type="warning" v-if="currentRecord.floor" style="margin-right:4px;">{{ currentRecord.floor }}层</el-tag>
            <el-tag size="small" type="success" v-if="currentRecord.room">{{ currentRecord.room }}</el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="详细位置">{{ currentRecord.location_detail || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="故障数量">{{ currentRecord.fault_count || 1 }}</el-descriptions-item>
        <el-descriptions-item label="现场照片" :span="2">
          <div v-if="currentRecord.scene_photos && currentRecord.scene_photos.length > 0" style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-image v-for="(photo, idx) in currentRecord.scene_photos" :key="idx" :src="photo" style="width:150px;height:110px;" fit="cover" :preview-src-list="currentRecord.scene_photos" />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentRecord.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="维修人">{{ currentRecord.staff_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="维修人电话">{{ currentRecord.staff_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="维修时间">{{ formatDate(currentRecord.complete_time || currentRecord.repair_end_time) }}</el-descriptions-item>
        <el-descriptions-item label="维修时长">{{ currentRecord.actual_duration ? formatDuration(currentRecord.actual_duration) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="维修说明" :span="2">{{ currentRecord.remark || '无' }}</el-descriptions-item>
        <el-descriptions-item label="维修照片" :span="2">
          <div v-if="currentRecord.repair_photos && currentRecord.repair_photos.length > 0" style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-image v-for="(photo, idx) in currentRecord.repair_photos" :key="idx" :src="photo" style="width:150px;height:110px;" fit="cover" :preview-src-list="currentRecord.repair_photos" />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="审核回复" :span="2"><span v-if="currentRecord.review_reply">{{ currentRecord.review_reply }}</span><span v-else>-</span></el-descriptions-item>
        <el-descriptions-item label="使用备件" :span="2">
          <template v-if="currentRecord.spare_parts_info && currentRecord.spare_parts_info.length > 0">
            <div v-for="(sp, idx) in currentRecord.spare_parts_info" :key="idx" style="margin-bottom:4px;">
              <el-tag size="small" type="info">{{ sp.spare_part_name }}</el-tag>
              <span style="margin-left:4px; color:#606266;">× {{ sp.quantity }}</span>
            </div>
          </template>
          <span v-else>无</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { repairApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const viewVisible = ref(false)
const currentItem = ref(null)
const selectedRows = ref([])

onMounted(() => loadData())

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value, status: 'CLOSED' }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await repairApi.recordList(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleSelectionChange = (rows) => { selectedRows.value = rows }

const currentRecord = ref(null)

const handleView = async (row) => {
  try {
    const res = await repairApi.orderGet(row.id)
    currentRecord.value = res
  } catch (e) {
    currentRecord.value = row
  }
  viewVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该维修记录？', '提示', { type: 'warning' })
  try {
    await repairApi.recordDelete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''
const formatDuration = (m) => { if (!m) return '-'; return m < 60 ? `${Math.round(m)}分钟` : `${Math.floor(m/60)}小时${Math.round(m%60)}分钟` }
const parsePhotos = (photoStr) => {
  if (!photoStr) return []
  if (Array.isArray(photoStr)) return photoStr
  if (typeof photoStr === 'string' && photoStr.startsWith('[')) { try { return JSON.parse(photoStr) } catch (e) {} }
  if (typeof photoStr === 'string' && (photoStr.startsWith('data:') || photoStr.startsWith('http'))) return [photoStr]
  return [photoStr]
}
</script>

<style scoped lang="scss">
.search-bar { display: flex; align-items: center; margin-bottom: 20px; }
</style>
