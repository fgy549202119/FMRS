<template>
  <div class="page">
    <div class="page-header"><h2>公共设备管理</h2></div>

    <el-card>
      <div class="search-bar">
        <el-select v-model="filterType" placeholder="设备类型" clearable style="width: 150px; margin-right: 10px;">
          <el-option v-for="item in types" :key="item.id" :label="item.type_name" :value="item.id" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="设备状态" clearable style="width: 120px; margin-right: 10px;">
          <el-option label="正常" value="正常" />
          <el-option label="故障" value="故障" />
        </el-select>
        <el-input v-model="searchKeyword" placeholder="搜索序号/设备名称" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
        <div style="margin-left: auto; display: flex; gap: 8px;">
          <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增设备</el-button>
          <el-button type="danger" :disabled="selectedIds.length === 0" @click="handleBatchDelete">
            <el-icon><Delete /></el-icon> 批量删除 ({{ selectedIds.length }})
          </el-button>
        </div>
      </div>

      <el-table :data="tableData" stripe v-loading="loading" style="width:100%;" :cell-style="{padding:'12px 0'}" :header-cell-style="{padding:'12px 0'}" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="45" />
        <el-table-column prop="sequence_number" label="序号" width="70" align="center" />
        <el-table-column label="图片" width="70">
          <template #default="{ row }">
            <el-image v-if="row.equipment_image" :src="row.equipment_image" fit="cover" style="width:36px;height:36px;border-radius:4px;" :preview-src-list="[row.equipment_image]" preview-teleported />
            <span v-else style="color:#ccc;font-size:12px;">无</span>
          </template>
        </el-table-column>
        <el-table-column prop="equipment_name" label="设备名称" width="110" show-overflow-tooltip />
        <el-table-column prop="equipment_type" label="设备类型" width="110">
          <template #default="{ row }">
            {{ row.equipment_type_detail?.type_name || row.equipment_type_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="所在位置" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.location_info?.full_location || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="specification" label="规格" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="75">
          <template #default="{ row }">
            <el-tag :type="row.status === '正常' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑设备' : '新增设备'" width="620px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="设备图片">
          <el-upload
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :limit="1"
            accept="image/*"
            :on-change="handleImageChange"
            :on-remove="handleImageRemove"
            :file-list="imageFileList"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">建议尺寸 300x300，支持 jpg/png</div>
        </el-form-item>
        <el-form-item label="设备名称" prop="equipment_name">
          <el-input v-model="form.equipment_name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型" prop="equipment_type">
          <el-select v-model="form.equipment_type" placeholder="请选择设备类型" style="width: 100%;">
            <el-option v-for="item in types" :key="item.id" :label="item.type_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所在位置">
          <div class="location-selector">
            <el-select v-model="form._campus" placeholder="选择院区" clearable style="width: 120px;" @change="onFormCampusChange">
              <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <el-select v-model="form.building" placeholder="选择楼栋" clearable style="width: 130px;" :disabled="!form._campus" @change="onFormBuildingChange">
              <el-option v-for="b in formBuildingList" :key="b.id" :label="b.name" :value="b.id" />
            </el-select>
            <el-select v-model="form.floor" placeholder="选择楼层" clearable style="width: 100px;" :disabled="!form.building" @change="onFormFloorChange">
              <el-option v-for="f in formFloorList" :key="f.id" :label="f.floor_number + '层'" :value="f.id" />
            </el-select>
            <el-select v-model="form.room" placeholder="选择房间(可选)" clearable style="width: 130px;" :disabled="!form.floor">
              <el-option label="无" :value="null" />
              <el-option v-for="r in formRoomList" :key="r.id" :label="r.name" :value="r.id" />
            </el-select>
          </div>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备规格">
              <el-input v-model="form.specification" placeholder="请输入设备规格" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供货商">
              <el-input v-model="form.supplier" placeholder="请输入供货商" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewVisible" title="设备详情" width="680px">
      <div v-if="currentItem" class="equipment-detail">
        <div class="detail-header">
          <div v-if="currentItem.equipment_image" class="detail-image">
            <el-image :src="currentItem.equipment_image" fit="cover" :preview-src-list="[currentItem.equipment_image]" preview-teleported />
          </div>
          <div class="detail-title">
            <h3>{{ currentItem.equipment_name }}</h3>
            <span class="equipment-no">序号: {{ currentItem.sequence_number }} | 编号: {{ currentItem.equipment_no }}</span>
          </div>
        </div>
        <div class="detail-content">
          <el-descriptions :column="2" border class="detail-descriptions">
            <el-descriptions-item label="设备类型" :span="1">
              {{ currentItem.equipment_type_detail?.type_name || currentItem.equipment_type_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="所在位置" :span="1">
              {{ currentItem.location_info?.full_location || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="设备规格" :span="1">{{ currentItem.specification || '-' }}</el-descriptions-item>
            <el-descriptions-item label="供货商" :span="1">{{ currentItem.supplier || '-' }}</el-descriptions-item>
            <el-descriptions-item label="设备状态" :span="1">
              <el-tag :type="currentItem.status === '正常' ? 'success' : 'danger'">{{ currentItem.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="发布时间" :span="2">{{ formatDate(currentItem.publish_time) }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { equipmentApi, locationApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const types = ref([])
const campusList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const filterType = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const viewVisible = ref(false)
const editId = ref(null)
const currentItem = ref(null)
const formRef = ref()
const imageFileList = ref([])
const selectedIds = ref([])

const formBuildingList = ref([])
const formFloorList = ref([])
const formRoomList = ref([])

const form = reactive({
  equipment_name: '',
  equipment_type: null,
  specification: '',
  supplier: '',
  status: '正常',
  is_reportable: true,
  equipment_image: '',
  _campus: null,
  building: null,
  floor: null,
  room: null
})

const rules = {
  equipment_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  equipment_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }]
}

onMounted(async () => {
  await Promise.all([loadTypes(), loadData(), loadCampuses()])
})

const loadTypes = async () => {
  try {
    const res = await equipmentApi.typeList({ page_size: 200 })
    types.value = res.results || []
  } catch (e) { console.error(e) }
}

const loadCampuses = async () => {
  try {
    const res = await locationApi.campus.list()
    campusList.value = res.results || []
  } catch (e) { console.error(e) }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterType.value) params.equipment_type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await equipmentApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleSelectionChange = (rows) => {
  selectedIds.value = rows.map(r => r.id)
}

const onFormCampusChange = async () => {
  form.building = null; form.floor = null; form.room = null
  formFloorList.value = []; formRoomList.value = []
  if (form._campus) {
    try {
      const res = await locationApi.building.list({ campus: form._campus })
      formBuildingList.value = res.results || []
    } catch (e) { console.error(e) }
  } else { formBuildingList.value = [] }
}

const onFormBuildingChange = async () => {
  form.floor = null; form.room = null; formRoomList.value = []
  if (form.building) {
    try {
      const res = await locationApi.floor.list({ building: form.building })
      formFloorList.value = Array.isArray(res) ? res : (res.results || [])
    } catch (e) { console.error(e) }
  } else { formFloorList.value = [] }
}

const onFormFloorChange = async () => {
  form.room = null
  if (form.floor) {
    try {
      const res = await locationApi.room.byFloor(form.floor)
      formRoomList.value = res.results || []
    } catch (e) { console.error(e) }
  } else { formRoomList.value = [] }
}

const handleAdd = () => {
  editId.value = null
  Object.assign(form, {
    equipment_name: '', equipment_type: null, specification: '', supplier: '',
    status: '正常', is_reportable: true, equipment_image: '',
    _campus: null, building: null, floor: null, room: null
  })
  formBuildingList.value = []; formFloorList.value = []; formRoomList.value = []
  imageFileList.value = []
  dialogVisible.value = true
}

const handleView = (row) => {
  currentItem.value = row
  viewVisible.value = true
}

const handleEdit = async (row) => {
  editId.value = row.id
  Object.assign(form, {
    equipment_name: row.equipment_name,
    equipment_type: row.equipment_type_detail?.id || row.equipment_type,
    specification: row.specification || '',
    supplier: row.supplier || '',
    status: row.status || '正常',
    is_reportable: row.is_reportable !== false,
    equipment_image: row.equipment_image || '',
    _campus: null, building: null, floor: null,
    room: row.room || null
  })
  imageFileList.value = row.equipment_image ? [{ name: '图片', url: row.equipment_image }] : []

  if (row.location_info) {
    form._campus = row.location_info.campus_id || null
    if (form._campus) {
      try { const res = await locationApi.building.list({ campus: form._campus }); formBuildingList.value = res.results || [] } catch (e) { console.error(e) }
    }
    form.building = row.location_info.building_id || null
    if (form.building) {
      try { const res = await locationApi.floor.list({ building: form.building }); formFloorList.value = Array.isArray(res) ? res : (res.results || []) } catch (e) { console.error(e) }
    }
    form.floor = row.location_info.floor_id || null
    if (form.floor) {
      try { const res = await locationApi.room.byFloor(form.floor); formRoomList.value = res.results || [] } catch (e) { console.error(e) }
    }
  } else {
    formBuildingList.value = []; formFloorList.value = []; formRoomList.value = []
  }
  dialogVisible.value = true
}

const handleImageChange = (file) => {
  imageFileList.value = [file]
  const reader = new FileReader()
  reader.onload = (e) => { form.equipment_image = e.target.result }
  if (file.raw) reader.readAsDataURL(file.raw)
  else form.equipment_image = file.url || ''
}

const handleImageRemove = () => {
  imageFileList.value = []; form.equipment_image = ''
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该设备？', '提示', { type: 'warning' })
  try { await equipmentApi.delete(row.id); ElMessage.success('删除成功'); loadData() }
  catch (e) { ElMessage.error('删除失败') }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const submitData = { ...form }
    delete submitData._campus
    if (editId.value) {
      await equipmentApi.update(editId.value, submitData)
      ElMessage.success('修改成功')
    } else {
      await equipmentApi.create(submitData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || '操作失败') }
  finally { submitting.value = false }
}

const handleBatchDelete = async () => {
  await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 台设备？`, '批量删除', { type: 'warning' })
  try {
    const res = await equipmentApi.batchDelete(selectedIds.value)
    ElMessage.success(res.message || '批量删除成功')
    selectedIds.value = []
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || '批量删除失败') }
}

const formatDate = (dateStr) => dateStr ? new Date(dateStr).toLocaleString('zh-CN') : ''
</script>

<style scoped lang="scss">
.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 8px;
}
.upload-tip {
  color: #999;
  font-size: 12px;
  margin-top: 4px;
}
.location-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  width: 100%;
}
.equipment-detail {
  .detail-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #ebeef5;
  }
  .detail-image {
    width: 120px;
    height: 120px;
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  .detail-title {
    flex: 1;
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 0 0 8px 0;
      color: #1f2329;
    }
    .equipment-no {
      font-size: 13px;
      color: #8f959e;
    }
  }
  .detail-content {
    .detail-descriptions {
      :deep(.el-descriptions__label) {
        color: #646a73;
        font-weight: 500;
        min-width: 80px;
        text-align: left;
      }
      :deep(.el-descriptions__content) {
        color: #1f2329;
      }
    }
  }
}
</style>
