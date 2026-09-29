<template>
  <div class="page">
    <div class="page-header"><h2>设备巡检</h2></div>
    
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索位置/巡检单号" style="width: 200px; margin-right: 10px;" clearable />
        <el-select v-model="filterEquipment" placeholder="设备" clearable style="width: 180px; margin-right: 10px;" filterable>
          <el-option v-for="item in equipments" :key="item.id" :label="item.equipment_name" :value="item.id" />
        </el-select>
        <el-select v-model="filterResult" placeholder="巡检结果" clearable style="width: 120px; margin-right: 10px;">
          <el-option label="正常" value="normal" />
          <el-option label="异常" value="abnormal" />
        </el-select>
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button type="primary" @click="handleAdd" style="margin-left: auto;">新增巡检</el-button>
      </div>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="inspection_no" label="巡检单号" width="160" />
        <el-table-column prop="equipment_name" label="设备名称" width="150" />
        <el-table-column label="设备类型" width="100">
          <template #default="{ row }">
            {{ row.equipment_type_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="设备位置" min-width="200">
          <template #default="{ row }">
            {{ row.location || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="现场照片" width="90" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.has_photo"
              :src="row._photo_url || ''"
              style="width: 60px; height: 45px; border-radius: 4px; cursor: pointer;"
              fit="cover"
              :preview-src-list="row._photo_url ? [row._photo_url] : []"
              preview-teleported
              lazy
              @click.prevent="loadPhoto(row)"
            >
              <template #error>
                <div class="photo-thumb-placeholder" @click="loadPhoto(row)">
                  <el-icon :size="20"><Picture /></el-icon>
                </div>
              </template>
              <template #placeholder>
                <div class="photo-thumb-loading">
                  <el-icon class="is-loading" :size="16"><Loading /></el-icon>
                </div>
              </template>
            </el-image>
            <el-tag v-else type="info" size="small">无</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inspection_time" label="巡检时间" width="165">
          <template #default="{ row }">
            {{ formatDate(row.inspection_time) }}
          </template>
        </el-table-column>
        <el-table-column label="巡检结果" width="90">
          <template #default="{ row }">
            <el-tag :type="row.result === 'normal' ? 'success' : 'danger'" size="small">
              {{ row.result === 'normal' ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审核状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
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

    <el-dialog v-model="addVisible" title="新增巡检" width="620px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="设备" prop="equipment">
          <el-select v-model="form.equipment" placeholder="请选择设备" style="width: 100%;" filterable @change="handleEquipmentChange">
            <el-option v-for="item in equipments" :key="item.id" :label="item.equipment_name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">位置信息</el-divider>

        <el-form-item label="所在位置" prop="campus">
          <div class="location-selector">
            <el-select v-model="form.campus" placeholder="选择院区" @change="onCampusChange" style="width:120px">
              <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <el-select v-model="form.building" placeholder="选择楼栋" @change="onBuildingChange" style="width:140px" :disabled="!form.campus">
              <el-option v-for="b in buildingList" :key="b.id" :label="b.name" :value="b.id" />
            </el-select>
            <el-select v-model="form.floor" placeholder="选择楼层" @change="onFloorChange" style="width:110px" :disabled="!form.building">
              <el-option v-for="f in floorList" :key="f.id" :label="f.floor_number + '层'" :value="f.id" />
            </el-select>
            <el-select v-model="form.room_id" placeholder="选择房间(可选)" style="width:140px" :disabled="!form.floor" filterable clearable @change="onRoomChange">
              <el-option v-for="r in roomList" :key="r.id" :label="r.name" :value="r.id" />
            </el-select>
          </div>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="详细位置">
              <el-input v-model="form.location_detail" placeholder="具体方位描述" clearable />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">设备序号</el-divider>

        <el-form-item label="设备序号" prop="equipment_id">
          <el-select
            v-model="form.equipment_id"
            placeholder="请先选择设备和位置"
            :disabled="!canLoadSeqList"
            :loading="seqLoading"
            style="width:100%"
          >
            <el-option v-for="item in equipmentSeqList" :key="item.id" :label="'序号: ' + item.sequence_number" :value="item.id" />
          </el-select>
          <div v-if="canLoadSeqList && !seqLoading && equipmentSeqList.length === 0" class="seq-empty-tip">
            该位置不存在此设备，请确认设备或位置
          </div>
        </el-form-item>

        <el-divider content-position="left">巡检信息</el-divider>

        <el-form-item label="巡检数量" prop="inspection_count">
          <el-input-number v-model="form.inspection_count" :min="1" :max="999" style="width: 200px;" />
        </el-form-item>
        <el-form-item label="巡检结果" prop="result">
          <el-radio-group v-model="form.result">
            <el-radio label="normal">正常</el-radio>
            <el-radio label="abnormal">异常</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="现场照片">
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
          <div class="upload-tip">支持jpg/png</div>
        </el-form-item>
        <el-form-item label="巡检记录" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入巡检发现的问题或说明" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交待审核</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="viewVisible" title="巡检详情" width="620px">
      <el-descriptions :column="2" border v-if="currentItem">
        <el-descriptions-item label="巡检单号">{{ currentItem.inspection_no }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentItem.equipment_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentItem.equipment_type_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备序号" v-if="currentItem.equipment_sequence_number">
          <el-tag type="danger" size="small">序号{{ currentItem.equipment_sequence_number }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="院区">{{ currentItem.campus_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="楼栋">{{ currentItem.building_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="楼层">{{ currentItem.floor_display || '-' }}</el-descriptions-item>
        <el-descriptions-item label="房间号">{{ currentItem.room_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="详细位置" :span="2">{{ currentItem.location_detail || '-' }}</el-descriptions-item>
        <el-descriptions-item label="完整位置" :span="2">{{ currentItem.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="巡检结果">
          <el-tag :type="currentItem.result === 'normal' ? 'success' : 'danger'">
            {{ currentItem.result === 'normal' ? '正常' : '异常' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审核状态">
          <el-tag :type="getStatusTagType(currentItem.status)">{{ getStatusText(currentItem.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="现场照片" :span="2">
          <el-image
            v-if="currentItem.scene_photo"
            :src="currentItem.scene_photo"
            style="width: 200px; height: 150px;"
            fit="cover"
            :preview-src-list="[currentItem.scene_photo]"
            preview-teleported
          />
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="巡检记录" :span="2">{{ currentItem.remark || currentItem.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="审核回复" :span="2" v-if="currentItem.review_reply">{{ currentItem.review_reply }}</el-descriptions-item>
        <el-descriptions-item label="巡检人员">{{ currentItem.staff_name }}</el-descriptions-item>
        <el-descriptions-item label="巡检时间">{{ formatDate(currentItem.inspection_time) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { inspectionApi, equipmentApi, locationApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Picture, Loading } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const filterEquipment = ref('')
const filterResult = ref('')
const addVisible = ref(false)
const viewVisible = ref(false)
const currentItem = ref(null)
const submitting = ref(false)
const formRef = ref()
const equipmentTypes = ref([])
const equipments = ref([])

const campusList = ref([])
const buildingList = ref([])
const floorList = ref([])
const roomList = ref([])
const imageFileList = ref([])
let imageBase64 = ''
const equipmentSeqList = ref([])
const seqLoading = ref(false)

const canLoadSeqList = computed(() => {
  return form.equipment && form.floor
})

const form = reactive({
  equipment: null,
  campus: null,
  building: null,
  floor: null,
  room_id: null,
  location_detail: '',
  equipment_id: null,
  scene_photo: '',
  result: 'normal',
  remark: '',
  inspection_count: 1
})

const rules = {
  equipment: [{ required: true, message: '请选择设备', trigger: 'change' }],
  campus: [{ required: true, message: '请选择院区', trigger: 'change' }],
  building: [{ required: true, message: '请选择楼栋', trigger: 'change' }],
  floor: [{ required: true, message: '请选择楼层', trigger: 'change' }],
  equipment_id: [{ required: true, message: '请选择设备序号', trigger: 'change' }],
  result: [{ required: true, message: '请选择巡检结果', trigger: 'change' }]
}

onMounted(async () => {
  await Promise.all([loadEquipmentTypes(), loadEquipments(), loadCampuses(), loadData()])
})

const loadEquipmentTypes = async () => {
  try {
    const res = await equipmentApi.typeList({ page_size: 100 })
    equipmentTypes.value = res.results || []
  } catch (e) { console.error(e) }
}

const loadEquipments = async () => {
  try {
    const res = await equipmentApi.distinctNames()
    equipments.value = res.results || []
  } catch (e) { console.error(e) }
}

const loadCampuses = async () => {
  try {
    const res = await locationApi.campus.list()
    campusList.value = res.results || []
  } catch (e) { console.error(e) }
}

const onCampusChange = async (campusId) => {
  form.building = null
  form.floor = null
  form.room_id = null
  form.equipment_id = null
  buildingList.value = []
  floorList.value = []
  roomList.value = []
  equipmentSeqList.value = []
  if (!campusId) return
  try {
    const res = await locationApi.building.list({ campus: campusId })
    buildingList.value = res.results || []
  } catch (e) { console.error(e) }
}

const onBuildingChange = async (buildingId) => {
  form.floor = null
  form.room_id = null
  form.equipment_id = null
  floorList.value = []
  roomList.value = []
  equipmentSeqList.value = []
  if (!buildingId) return
  try {
    const res = await locationApi.floor.byBuilding(buildingId)
    floorList.value = Array.isArray(res) ? res : (res.results || [])
  } catch (e) { console.error(e) }
}

const onFloorChange = async (floorId) => {
  form.room_id = null
  form.equipment_id = null
  roomList.value = []
  equipmentSeqList.value = []
  if (!floorId) return
  try {
    const res = await locationApi.room.byFloor(floorId)
    roomList.value = res.results || []
  } catch (e) { console.error(e) }
  loadEquipmentSeqList()
}

const onRoomChange = () => {
  form.equipment_id = null
  equipmentSeqList.value = []
  loadEquipmentSeqList()
}

const loadEquipmentSeqList = async () => {
  if (!canLoadSeqList.value) {
    equipmentSeqList.value = []
    return
  }
  const selectedEquipment = equipments.value.find(e => e.id === form.equipment)
  if (!selectedEquipment) {
    equipmentSeqList.value = []
    return
  }
  seqLoading.value = true
  try {
    const params = { equipment_name: selectedEquipment.equipment_name }
    if (form.room_id) params.room_id = form.room_id
    else if (form.floor) params.floor_id = form.floor
    else if (form.building) params.building_id = form.building
    const res = await equipmentApi.byNameAndLocation(params)
    equipmentSeqList.value = res.results || []
    if (equipmentSeqList.value.length === 1) {
      form.equipment_id = equipmentSeqList.value[0].id
    }
  } catch (e) {
    console.error(e)
    equipmentSeqList.value = []
  } finally {
    seqLoading.value = false
  }
}

const handleEquipmentChange = async (equipmentId) => {
  form.equipment_id = null
  equipmentSeqList.value = []
  if (!equipmentId) {
    form.campus = null
    form.building = null
    form.floor = null
    form.room_id = null
    buildingList.value = []
    floorList.value = []
    roomList.value = []
    return
  }
  if (canLoadSeqList.value) {
    loadEquipmentSeqList()
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterEquipment.value) params.equipment = filterEquipment.value
    if (filterResult.value) params.result = filterResult.value
    const res = await inspectionApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  Object.assign(form, {
    equipment: null,
    campus: null,
    building: null,
    floor: null,
    room_id: null,
    location_detail: '',
    equipment_id: null,
    scene_photo: '',
    result: 'normal',
    remark: '',
    inspection_count: 1
  })
  imageFileList.value = []
  imageBase64 = ''
  buildingList.value = []
  floorList.value = []
  roomList.value = []
  equipmentSeqList.value = []
  addVisible.value = true
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

const handleImageChange = (file) => {
  imageFileList.value.push(file)
  const reader = new FileReader()
  reader.onload = (e) => {
    imageBase64 = e.target.result
    form.scene_photo = imageBase64
  }
  reader.readAsDataURL(file.raw)
}

const handleImageRemove = () => {
  imageFileList.value = []
  imageBase64 = ''
  form.scene_photo = ''
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = {
      equipment: form.equipment_id,
      campus: form.campus,
      building: form.building,
      floor: form.floor,
      room_id: form.room_id,
      location_detail: form.location_detail,
      scene_photo: form.scene_photo,
      result: form.result,
      remark: form.remark,
      inspection_count: form.inspection_count || 1,
      status: 'pending'
    }
    await inspectionApi.create(data)
    ElMessage.success('提交成功，等待管理员审核')
    addVisible.value = false
    loadData()
  } catch (error) {
    const msg = error.response?.data?.message || error.response?.data?.equipment?.[0] || error.response?.data?.staff?.[0] || '提交失败'
    ElMessage.error(msg)
  } finally {
    submitting.value = false
  }
}

const getStatusText = (status) => {
  const map = { pending: '待审核', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadPhoto = async (row) => {
  if (row._photo_url) return
  try {
    const res = await inspectionApi.get(row.id)
    const photo = (res.data || res).scene_photo
    if (photo) {
      row._photo_url = photo
    }
  } catch (e) {
    console.error('加载照片失败', e)
  }
}
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
:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
}
:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
}
.location-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}
.seq-empty-tip {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}
.photo-thumb-placeholder {
  width: 60px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  cursor: pointer;
  &:hover { background: #ecf5ff; color: #409eff; }
}
.photo-thumb-loading {
  width: 60px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}
</style>
