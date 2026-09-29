<template>
  <div class="page">
    <div class="page-header"><h2>设备巡检管理</h2></div>
    
    <el-card>
      <div class="search-bar">
        <el-select v-model="filterStatus" placeholder="审核状态" clearable style="width: 120px; margin-right: 10px;">
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-input v-model="searchKeyword" placeholder="搜索巡检单号" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedRows.length === 0" style="margin-left: auto;">批量删除</el-button>
      </div>
      
      <el-table :data="tableData" stripe v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="inspection_no" label="巡检单号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" width="120">
          <template #default="{ row }">
            {{ row.equipment_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="equipment_type_name" label="设备类型" width="120">
          <template #default="{ row }">
            {{ row.equipment_type_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="inspection_count" label="巡检数量" width="90" align="center" />
        <el-table-column prop="location" label="设备位置">
          <template #default="{ row }">
            {{ row.location || '-' }}
            <el-tag type="danger" size="small" v-if="row.equipment_sequence_number" style="margin-left:4px;">序号{{ row.equipment_sequence_number }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="staff_name" label="巡检人员" width="100" />
        <el-table-column prop="inspection_time" label="巡检时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.inspection_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="审核状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="success" link @click="handleReview(row)" v-if="row.status === 'pending'">审核</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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
    
    <el-dialog v-model="viewVisible" title="巡检详情" width="600px">
      <el-descriptions :column="2" border v-if="currentItem">
        <el-descriptions-item label="巡检单号">{{ currentItem.inspection_no }}</el-descriptions-item>
        <el-descriptions-item label="审核状态">
          <el-tag :type="getStatusType(currentItem.status)">{{ getStatusText(currentItem.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentItem.equipment_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentItem.equipment_type_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备序号" v-if="currentItem.equipment_sequence_number">
          <el-tag type="danger" size="small">序号{{ currentItem.equipment_sequence_number }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="设备位置">{{ currentItem.location }}</el-descriptions-item>
        <el-descriptions-item label="巡检人员">{{ currentItem.staff_name }}</el-descriptions-item>
        <el-descriptions-item label="巡检时间">{{ formatDate(currentItem.inspection_time) }}</el-descriptions-item>
        <el-descriptions-item label="巡检描述" :span="2">{{ currentItem.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="现场照片" :span="2">
          <template v-if="currentItem.scene_photo">
            <el-image v-if="Array.isArray(currentItem.scene_photo)" :src="currentItem.scene_photo[0]" style="width: 200px; height: 150px;" fit="cover" :preview-src-list="currentItem.scene_photo" />
            <el-image v-else :src="currentItem.scene_photo" style="width: 200px; height: 150px;" fit="cover" :preview-src-list="[currentItem.scene_photo]" />
          </template>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="审核回复" :span="2">{{ currentItem.review_reply || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    
    <el-dialog v-model="reviewVisible" title="审核巡检记录" width="500px">
      <el-form :model="reviewForm" ref="reviewFormRef" label-width="80px">
        <el-form-item label="审核结果" prop="review_status">
          <el-radio-group v-model="reviewForm.review_status">
            <el-radio label="approved">通过</el-radio>
            <el-radio label="rejected">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核回复">
          <el-input v-model="reviewForm.review_reply" type="textarea" :rows="3" placeholder="请输入审核回复" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { inspectionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const filterStatus = ref('')
const viewVisible = ref(false)
const reviewVisible = ref(false)
const currentItem = ref(null)
const reviewFormRef = ref()
const selectedRows = ref([])

const reviewForm = reactive({
  review_status: 'approved',
  review_reply: ''
})

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await inspectionApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleView = async (row) => {
  try {
    const res = await inspectionApi.get(row.id)
    currentItem.value = res.data || res
  } catch (e) {
    currentItem.value = row
  }
  viewVisible.value = true
}

const handleReview = (row) => {
  currentItem.value = row
  reviewForm.review_status = 'approved'
  reviewForm.review_reply = ''
  reviewVisible.value = true
}

const submitReview = async () => {
  submitting.value = true
  try {
    await inspectionApi.review(currentItem.value.id, reviewForm)
    ElMessage.success('审核成功')
    reviewVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('审核失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该巡检记录？', '提示', { type: 'warning' })
    await inspectionApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的巡检记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 条巡检记录？此操作不可恢复！`, '警告', { type: 'warning' })
    for (const row of selectedRows.value) {
      await inspectionApi.delete(row.id)
    }
    ElMessage.success('批量删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const getStatusType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { pending: '待审核', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
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
}
</style>
