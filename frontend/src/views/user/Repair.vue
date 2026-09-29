<template>
  <div class="repair-container">
    <el-card>
      <template #header><span>设备报修</span></template>

      <el-form ref="formRef" :model="form" :rules="formRules" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择设备" prop="equipment">
              <el-select v-model="form.equipment" filterable placeholder="请选择报修设备" style="width:100%" @change="handleEquipmentChange">
                <el-option v-for="eq in equipments" :key="eq.id" :label="eq.equipment_name" :value="eq.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">位置信息</el-divider>

        <el-form-item label="所在位置" prop="campus_id">
          <div class="location-selector">
            <el-select v-model="form.campus_id" placeholder="选择院区" @change="onCampusChange" style="width:120px">
              <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <el-select v-model="form.building_id" placeholder="选择楼栋" @change="onBuildingChange" style="width:140px" :disabled="!form.campus_id">
              <el-option v-for="b in buildingList" :key="b.id" :label="b.name" :value="b.id" />
            </el-select>
            <el-select v-model="form.floor_id" placeholder="选择楼层" @change="onFloorChange" style="width:110px" :disabled="!form.building_id">
              <el-option v-for="f in floorList" :key="f.id" :label="f.floor_number + '层'" :value="f.id" />
            </el-select>
            <el-select v-model="form.room_id" placeholder="选择房间(可选)" @change="onRoomChange" style="width:140px" :disabled="!form.floor_id" filterable clearable>
              <el-option v-for="r in roomList" :key="r.id" :label="r.name" :value="r.id" />
            </el-select>
          </div>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="详细位置" prop="location_detail">
              <el-input v-model="form.location_detail" placeholder="具体方位描述" clearable />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">设备序号</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备序号" prop="equipment_id">
              <el-select
                v-model="form.equipment_id"
                placeholder="请先选择设备和位置"
                :disabled="!canLoadSeqList"
                :loading="seqLoading"
                style="width:100%"
                @change="handleSeqChange"
              >
                <el-option v-for="item in equipmentSeqList" :key="item.id" :label="'序号: ' + item.sequence_number" :value="item.id" />
              </el-select>
              <div v-if="canLoadSeqList && !seqLoading && equipmentSeqList.length === 0" class="seq-empty-tip">
                该位置不存在此设备，请确认设备或位置
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">故障信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="故障数量" prop="fault_count">
              <el-input-number v-model="form.fault_count" :min="1" :max="99" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="故障描述" prop="description">
              <el-input v-model="form.description" type="textarea" :rows="4" maxlength="500" show-word-limit
                placeholder="请详细描述故障现象、发生时间等信息..." />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="现场照片">
              <el-upload
                action="#"
                list-type="picture-card"
                :auto-upload="false"
                :limit="3"
                accept="image/*"
                :on-change="handlePhotoChange"
                :on-remove="handlePhotoRemove"
                :file-list="photoFileList"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">最多上传3张图片，支持jpg/png</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item class="submit-btn">
          <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting" :disabled="!form.equipment_id">
            提交报修
          </el-button>
          <el-button size="large" @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-dialog v-model="showDuplicateDialog" title="重复报修提示" width="450px">
      <el-alert type="error" :closable="false" style="margin-bottom:15px;">
        <template #title>该位置已有未完成报修，请勿重复提交！</template>
      </el-alert>
      <div v-if="duplicateOrders.length > 0" style="max-height:200px; overflow-y:auto;">
        <div v-for="order in duplicateOrders" :key="order.id" class="duplicate-order-item">
          工单号：{{ order.repair_no }} | 设备：{{ order.equipment_name }} | 提交时间：{{ order.created_at }}
        </div>
      </div>
      <p style="color:#666; font-size:13px; margin-top:10px;">只有"已完成"或"已取消"的工单才允许再次报修。</p>
      <template #footer>
        <el-button type="primary" @click="showDuplicateDialog = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { equipmentApi, repairApi, locationApi } from '@/api'

const formRef = ref()
const submitting = ref(false)
const showDuplicateDialog = ref(false)
const duplicateOrders = ref([])
const photoFileList = ref([])

const equipments = ref([])
const campusList = ref([])
const buildingList = ref([])
const floorList = ref([])
const roomList = ref([])
const equipmentSeqList = ref([])
const seqLoading = ref(false)

const form = reactive({
  equipment: null,
  campus_id: null,
  building_id: null,
  floor_id: null,
  room_id: null,
  location_detail: '',
  equipment_id: null,
  fault_count: 1,
  description: '',
  scene_photos: []
})

const canLoadSeqList = computed(() => {
  return form.equipment && form.floor_id
})

const formRules = {
  equipment: [{ required: true, message: '请选择报修设备', trigger: 'change' }],
  campus_id: [{ required: true, message: '请选择院区', trigger: 'change' }],
  building_id: [{ required: true, message: '请选择楼栋', trigger: 'change' }],
  floor_id: [{ required: true, message: '请选择楼层', trigger: 'change' }],
  equipment_id: [{ required: true, message: '请选择设备序号', trigger: 'change' }],
  description: [{ required: true, message: '请输入故障描述', trigger: 'blur' }]
}

onMounted(async () => {
  await Promise.all([loadEquipment(), loadCampuses()])
})

const loadEquipment = async () => {
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
    const params = {
      equipment_name: selectedEquipment.equipment_name,
    }
    if (form.room_id) params.room_id = form.room_id
    else if (form.floor_id) params.floor_id = form.floor_id
    else if (form.building_id) params.building_id = form.building_id

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

const onCampusChange = async (campusId) => {
  form.building_id = null
  form.floor_id = null
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
  form.floor_id = null
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

const handleEquipmentChange = async (equipmentId) => {
  form.equipment_id = null
  equipmentSeqList.value = []
  if (!equipmentId) {
    form.campus_id = null
    form.building_id = null
    form.floor_id = null
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

const handleSeqChange = () => {}

const handlePhotoChange = (file) => {
  photoFileList.value.push(file)
  const reader = new FileReader()
  reader.onload = (e) => { form.scene_photos.push(e.target.result) }
  if (file.raw) reader.readAsDataURL(file.raw)
}

const handlePhotoRemove = (file) => {
  const idx = photoFileList.value.findIndex(f => f.uid === file.uid)
  if (idx > -1) {
    photoFileList.value.splice(idx, 1)
    form.scene_photos.splice(idx, 1)
  }
}

const resetForm = () => {
  Object.assign(form, {
    equipment: null, campus_id: null, building_id: null, floor_id: null,
    room_id: null, location_detail: '', equipment_id: null, fault_count: 1, description: '', scene_photos: []
  })
  photoFileList.value = []
  buildingList.value = []
  floorList.value = []
  roomList.value = []
  equipmentSeqList.value = []
  formRef.value?.clearValidate()
}

const checkDuplicate = async () => {
  if (!form.equipment_id) return false

  try {
    const equipment = equipments.value.find(e => e.id === form.equipment)
    if (!equipment) return false

    let locationName = ''
    let buildingName = ''
    let floorName = ''
    let roomName = ''

    if (form.campus_id) {
      const campus = campusList.value.find(c => c.id === form.campus_id)
      if (campus) locationName = campus.name
    }
    if (form.building_id) {
      const building = buildingList.value.find(b => b.id === form.building_id)
      if (building) buildingName = building.name
    }
    if (form.floor_id) {
      const floor = floorList.value.find(f => f.id === form.floor_id)
      if (floor) floorName = `${floor.floor_number}层`
    }
    if (form.room_id) {
      const room = roomList.value.find(r => r.id === form.room_id)
      if (room) roomName = room.name
    }

    const res = await repairApi.checkDuplicate({
      equipment_name: equipment.equipment_name,
      location: locationName,
      building: buildingName,
      floor: floorName,
      room: roomName
    })

    if (res.is_duplicate && res.count > 0) {
      showDuplicateDialog.value = true
      return true
    }
  } catch (e) {
    console.warn('查重检查失败:', e)
  }
  return false
}

const handleSubmit = async () => {
  await formRef.value.validate()

  const hasDup = await checkDuplicate()
  if (hasDup) return

  submitting.value = true
  try {
    const data = {
      equipment_id: form.equipment_id,
      campus: form.campus_id,
      building: form.building_id,
      floor: form.floor_id,
      room_id: form.room_id,
      location_detail: form.location_detail,
      fault_count: form.fault_count,
      description: form.description,
      scene_photos: form.scene_photos
    }

    await repairApi.orderCreate(data)
    ElMessage.success('报修成功！')
    resetForm()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || e.message || '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.repair-container {
  padding: 20px;
  max-width: 960px;
  margin: 0 auto;
}
.submit-btn {
  text-align: center;
  margin-top: 30px;
}
.upload-tip {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}
.duplicate-order-item {
  padding: 8px 12px;
  margin-bottom: 6px;
  background: #fef9ef;
  border-left: 3px solid #e6a23c;
  border-radius: 3px;
  font-size: 13px;
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
</style>
