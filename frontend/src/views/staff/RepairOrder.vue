<template>
  <div class="page">
    <div class="page-header"><h2>我的工单</h2></div>

    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索报修编号/设备名称" style="width: 200px; margin-right: 10px;" clearable />
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px; margin-right: 10px;">
          <el-option label="处理中" value="IN_PROGRESS" />
          <el-option label="待审核" value="PENDING_ADMIN_CLOSE" />
          <el-option label="已完成" value="CLOSED" />
        </el-select>
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column label="设备类型" width="120">
          <template #default="{ row }">{{ row.equipment_type_name || row.equipment_type || '-' }}</template>
        </el-table-column>
        <el-table-column label="设备位置" min-width="140">
          <template #default="{ row }">{{ [row.location, row.building, row.floor].filter(Boolean).join(' ') || '-' }}<el-tag size="small" type="danger" v-if="row.equipment_sequence_number" style="margin-left:4px;">序号{{ row.equipment_sequence_number }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="user_name" label="报修人" width="90" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }"><el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
            <el-button type="warning" link @click="handleTransfer(row)" v-if="canTransfer(row)">转派</el-button>
            <el-button type="primary" link @click="handleComplete(row)" v-if="row.status === 'IN_PROGRESS'">完成</el-button>
            <el-button type="info" link @click="handleReviewStatus(row)" v-if="row.status === 'PENDING_ADMIN_CLOSE'">审核</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="viewVisible" title="工单详情" width="600px">
      <el-descriptions :column="2" border v-if="currentItem">
        <el-descriptions-item label="编号">{{ currentItem.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="状态"><el-tag :type="getStatusType(currentItem.status)">{{ getStatusText(currentItem.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="设备">{{ currentItem.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentItem.equipment_type_name || (isNaN(currentItem.equipment_type) ? currentItem.equipment_type : '-') }}</el-descriptions-item>
        <el-descriptions-item label="位置" :span="2">{{ [currentItem.location, currentItem.building, currentItem.floor].filter(Boolean).join(' ') }}<el-tag size="small" type="danger" v-if="currentItem.equipment_sequence_number" style="margin-left:4px;">序号{{ currentItem.equipment_sequence_number }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="报修人">{{ currentItem.user_name }}</el-descriptions-item>
        <el-descriptions-item label="维修员">{{ currentItem.staff_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentItem.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="照片" :span="2">
          <div v-if="currentItem.scene_photos && currentItem.scene_photos.length > 0" style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-image v-for="(photo, idx) in currentItem.scene_photos" :key="idx" :src="photo" style="width:180px;height:130px" fit="cover" :preview-src-list="currentItem.scene_photos" :initial-index="idx" preview-teleported />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer><el-button @click="viewVisible=false">关闭</el-button></template>
    </el-dialog>

    <el-dialog v-model="transferVisible" title="转派工单" width="400px">
      <el-form :model="transferForm" label-width="80px">
        <el-form-item label="目标维修员">
          <el-select v-model="transferForm.staff_id" filterable style="width:100%"><el-option v-for="s in staffList" :key="s.id" :label="`${s.real_name}(${s.staff_no})`" :value="s.id" /></el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="transferVisible=false">取消</el-button><el-button type="primary" @click="submitTransfer" :loading="transferring">确认</el-button></template>
    </el-dialog>

    <el-dialog v-model="completeVisible" title="完成维修" width="500px">
      <el-form :model="completeForm" ref="completeRef" :rules="{ remark:[{required:true,message:'请输入说明'}] }" label-width="100px">
        <el-form-item label="维修照片"><el-upload action="#" list-type="picture-card" :auto-upload="false" :limit="3" :on-change="(f)=>{photoFiles.push(f);completeForm.photo=f.url||''}" :on-remove="()=>{photoFiles=[];completeForm.photo=''}" :file-list="photoFiles"><el-icon><Plus /></el-icon></el-upload></el-form-item>
        <el-form-item label="维修说明" prop="remark"><el-input v-model="completeForm.remark" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="维修耗时"><el-tag>{{ calcDuration }}</el-tag><span style="color:#999;margin-left:8px;">自动计算</span></el-form-item>
      </el-form>
      <template #footer><el-button @click="completeVisible=false">取消</el-button><el-button type="primary" @click="submitComplete" :loading="completing">提交</el-button></template>
    </el-dialog>

    <el-dialog v-model="reviewVisible" title="审核状态" width="450px">
      <el-descriptions :column="1" border v-if="reviewRecord">
        <el-descriptions-item label="状态"><el-tag :type="reviewRecord.review_status==='approved'?'success':reviewRecord.review_status==='rejected'?'danger':'warning'">{{ {pending:'待审核', approved:'已通过', rejected:'已驳回'}[reviewRecord.review_status] }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="说明">{{ reviewRecord.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="回复">{{ reviewRecord.review_reply || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer><el-button @click="reviewVisible=false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { repairApi, staffApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const filterStatus = ref('')
const viewVisible = ref(false)
const currentItem = ref(null)

const transferVisible = ref(false); const transferring = ref(false); const staffList = ref([])
const transferForm = reactive({ order_id: null, staff_id: null })

const completeVisible = ref(false); const completing = ref(false); const completeRef = ref()
const photoFiles = ref([])
const completeForm = reactive({ order_id: null, photo: '', remark: '' })
const calcDuration = computed(() => {
  if (!currentItem.value) return '-'
  const s = currentItem.value.repair_start_time || currentItem.value.accept_time
  if (!s) return '-'
  try { const d = Math.round((Date.now() - new Date(s).getTime()) / 60000); return d<60?d+'分钟':Math.floor(d/60)+'小时'+(d%60)+'分' }
  catch { return '-' }
})

const reviewVisible = ref(false); const reviewRecord = ref(null)

onMounted(() => { loadData(); loadStaffList() })

const loadData = async () => {
  loading.value = true
  try {
    const p = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) p.search = searchKeyword.value
    if (filterStatus.value) p.status = filterStatus.value
    else p.status = 'IN_PROGRESS'
    if (staffInfo.value?.id) p.staff_id = staffInfo.value.id
    const r = await repairApi.orderList(p); tableData.value = r.results || []; total.value = r.count || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}
const loadStaffList = async () => { try { const r = await staffApi.list({ page_size:100 }); staffList.value = r.results || [] } catch(e){} }

const handleView = async (row) => {
  try {
    const res = await repairApi.orderGet(row.id)
    currentItem.value = res
  } catch (e) {
    currentItem.value = row
  }
  viewVisible.value = true
}

const canTransfer = (row) => {
  if (row.status !== 'IN_PROGRESS') return false
  if (!row.accept_time) return false
  try { return (Date.now() - new Date(row.accept_time).getTime()) < 180000 }
  catch { return false }
}

const handleTransfer = (row) => { Object.assign(transferForm, { order_id: row.id, staff_id: null }); transferVisible.value = true }
const submitTransfer = async () => {
  if (!transferForm.staff_id) { ElMessage.warning('请选择'); return }
  transferring.value = true
  try { await repairApi.orderTransfer(transferForm.order_id, { staff_id: transferForm.staff_id }); ElMessage.success('转派成功'); transferVisible.value = false; loadData() }
  catch (e) { ElMessage.error(e.response?.data?.message || '失败') }
  finally { transferring.value = false }
}
const handleComplete = (row) => { currentItem.value = row; Object.assign(completeForm, { order_id: row.id, photo: '', remark: '' }); photoFiles.value = []; completeVisible.value = true }
const submitComplete = async () => {
  await completeRef.value.validate()
  completing.value = true
  try { await repairApi.orderComplete(completeForm.order_id, { scene_photo: completeForm.photo, remark: completeForm.remark }); ElMessage.success('提交成功'); completeVisible.value = false; loadData() }
  catch (e) { ElMessage.error(e.response?.data?.message || '失败') }
  finally { completing.value = false }
}
const handleReviewStatus = async (row) => {
  try { const r = await repairApi.recordList({ repair_no: row.repair_no }); if (r.results?.length) { reviewRecord.value = r.results[0]; reviewVisible.value = true } else ElMessage.warning('无记录') }
  catch (e) { ElMessage.error('获取失败') }
}

const getStatusType = (s) => ({ WAITING:'warning', IN_PROGRESS:'primary', PENDING_ADMIN_CLOSE:'info', CLOSED:'success', REJECTED:'danger' })[s] || 'info'
const getStatusText = (s) => ({ WAITING:'待接单', IN_PROGRESS:'处理中', PENDING_ADMIN_CLOSE:'待验收', CLOSED:'已完成', REJECTED:'已取消' })[s] || s
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''
</script>

<style scoped lang="scss">
.search-bar { display:flex; align-items:center; margin-bottom:20px; }
</style>
