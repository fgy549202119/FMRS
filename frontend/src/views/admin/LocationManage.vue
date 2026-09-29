<template>
  <div class="location-manage">
    <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
      <el-tab-pane label="院区管理" name="campus">
        <div class="tab-header">
          <el-button type="primary" @click="handleAdd('campus')">
            <el-icon><Plus /></el-icon> 新增院区
          </el-button>
        </div>
        <el-table :data="campusList" border stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="院区名称" width="150" show-overflow-tooltip />
          <el-table-column prop="code" label="编码" width="100" />
          <el-table-column prop="description" label="描述"  />
          <el-table-column prop="sort_order" label="排序" width="70" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit('campus', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('campus', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="楼栋管理" name="building">
        <div class="tab-header">
          <el-select v-model="buildingFilter.campus" placeholder="筛选院区" clearable style="width: 180px; margin-right: 10px;" @change="loadBuildings">
            <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-button type="primary" @click="handleAdd('building')">
            <el-icon><Plus /></el-icon> 新增楼栋
          </el-button>
        </div>
        <el-table :data="buildingList" border stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="楼栋名称" />
          <el-table-column prop="code" label="编码" width="120" />
          <el-table-column prop="campus_name" label="所属院区" width="140" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit('building', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('building', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="楼层管理" name="floor">
        <div class="tab-header">
          <el-select v-model="floorFilter.campus" placeholder="选择院区" clearable style="width: 160px; margin-right: 8px;" @change="onFloorCampusChange">
            <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-select v-model="floorFilter.building" placeholder="选择楼栋" clearable style="width: 200px; margin-right: 10px;" @change="loadFloors" :disabled="!floorFilter.campus">
            <el-option v-for="b in filteredBuildingsForFloor" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
          <el-button type="success" @click="showBatchFloorDialog = true" style="margin-right: 10px;">
            <el-icon><Plus /></el-icon> 批量添加
          </el-button>
          <el-button type="primary" @click="handleAdd('floor')">
            <el-icon><Plus /></el-icon> 新增楼层
          </el-button>
        </div>
        <el-table :data="floorList" border stripe v-loading="floorLoading">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="floor_number" label="楼层号" width="90" />
          <el-table-column label="所属位置" min-width="200">
            <template #default="{ row }">
              {{ row.campus_name || '' }} - {{ row.building_name || '' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="handleDelete('floor', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="房间管理" name="room">
        <div class="tab-header">
          <el-select v-model="roomFilter.campus" placeholder="选择院区" clearable style="width: 150px; margin-right: 8px;" @change="onRoomCampusChange">
            <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-select v-model="roomFilter.building" placeholder="选择楼栋" clearable style="width: 180px; margin-right: 8px;" @change="onRoomBuildingChange" :disabled="!roomFilter.campus">
            <el-option v-for="b in roomBuildingList" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
          <el-select v-model="roomFilter.floor" placeholder="选择楼层" clearable style="width: 120px; margin-right: 10px;" @change="loadRooms" :disabled="!roomFilter.building">
            <el-option v-for="f in roomFloorList" :key="f.id" :label="f.floor_number + '层'" :value="f.id" />
          </el-select>
          <el-button type="success" @click="showBatchRoomDialog = true" style="margin-right: 10px;">
            <el-icon><Plus /></el-icon> 批量添加
          </el-button>
          <el-button type="primary" @click="handleAdd('room')">
            <el-icon><Plus /></el-icon> 新增房间
          </el-button>
        </div>
        <el-table :data="roomList" border stripe v-loading="roomLoading">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="房间名称" width="160" />
          <el-table-column prop="campus_name" label="院区" width="100" />
          <el-table-column prop="building_name" label="楼栋" width="140" />
          <el-table-column prop="floor_name" label="楼层" width="80" />
          <el-table-column prop="sort" label="排序" width="70" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit('room', row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete('room', row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @closed="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="110px">
        <template v-if="editType === 'campus'">
          <el-form-item label="院区名称" prop="name"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="编码" prop="code"><el-input v-model="form.code" /></el-form-item>
          <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
          <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        </template>

        <template v-if="editType === 'building'">
          <el-form-item label="所属院区" prop="campus">
            <el-select v-model="form.campus" style="width: 100%">
              <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="楼栋名称" prop="name"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="编码" prop="code"><el-input v-model="form.code" /></el-form-item>
        </template>

        <template v-if="editType === 'floor'">
          <el-form-item label="所属院区" prop="_campus">
            <el-select v-model="form._campus" style="width: 100%" @change="onFormCampusChange">
              <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属楼栋" prop="building">
            <el-select v-model="form.building" style="width: 100%" filterable :disabled="!form._campus">
              <el-option v-for="b in formBuildingList" :key="b.id" :label="b.campus_name + '-' + b.name" :value="b.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="楼层号" prop="floor_number"><el-input-number v-model="form.floor_number" :min="-5" :max="100" /></el-form-item>
        </template>

        <template v-if="editType === 'room'">
          <el-form-item label="所属院区" prop="_campus">
            <el-select v-model="form._campus" style="width: 100%" @change="onRoomFormCampusChange">
              <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属楼栋" prop="_building">
            <el-select v-model="form._building" style="width: 100%" filterable :disabled="!form._campus" @change="onRoomFormBuildingChange">
              <el-option v-for="b in roomFormBuildingList" :key="b.id" :label="b.name" :value="b.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属楼层" prop="floor">
            <el-select v-model="form.floor" style="width: 100%" :disabled="!form._building">
              <el-option v-for="f in roomFormFloorList" :key="f.id" :label="f.floor_number + '层'" :value="f.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="房间名称" prop="name"><el-input v-model="form.name" placeholder="如：101、会议室、实验室A" /></el-form-item>
          <el-form-item label="排序号"><el-input-number v-model="form.sort" :min="0" /></el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchFloorDialog" title="批量添加楼层" width="450px">
      <el-form :model="batchForm" :rules="batchRules" ref="batchFormRef" label-width="100px">
        <el-form-item label="所属院区" prop="campus">
          <el-select v-model="batchForm.campus" style="width: 100%" @change="onBatchCampusChange">
            <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属楼栋" prop="building">
          <el-select v-model="batchForm.building" style="width: 100%" filterable :disabled="!batchForm.campus">
            <el-option v-for="b in batchBuildingList" :key="b.id" :label="b.campus_name + '-' + b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="起始楼层" prop="start_floor">
          <el-input-number v-model="batchForm.start_floor" :min="-5" :max="100" />
        </el-form-item>
        <el-form-item label="结束楼层" prop="end_floor">
          <el-input-number v-model="batchForm.end_floor" :min="-5" :max="100" />
        </el-form-item>
        <el-alert type="info" :closable="false" style="margin-top: 10px;">
          <template #title>输入 1 到 6 将一次性创建 1~6 层，已存在的自动跳过。</template>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="showBatchFloorDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchCreateFloors" :loading="batchCreating">批量创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchRoomDialog" title="批量添加房间" width="500px">
      <el-form :model="batchRoomForm" :rules="batchRoomRules" ref="batchRoomFormRef" label-width="100px">
        <el-form-item label="所属院区" prop="campus">
          <el-select v-model="batchRoomForm.campus" style="width: 100%" @change="onBatchRoomCampusChange">
            <el-option v-for="c in campusList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属楼栋" prop="building">
          <el-select v-model="batchRoomForm.building" style="width: 100%" filterable :disabled="!batchRoomForm.campus" @change="onBatchRoomBuildingChange">
            <el-option v-for="b in batchRoomBuildingList" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属楼层" prop="floor">
          <el-select v-model="batchRoomForm.floor" style="width: 100%" :disabled="!batchRoomForm.building">
            <el-option v-for="f in batchRoomFloorList" :key="f.id" :label="f.floor_number + '层'" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="命名方式">
          <el-radio-group v-model="batchRoomForm.nameMode">
            <el-radio label="number">纯数字（如 101, 102）</el-radio>
            <el-radio label="prefix">前缀+数字（如 A101）</el-radio>
            <el-radio label="custom">自定义</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="名称前缀" v-if="batchRoomForm.nameMode === 'prefix' || batchRoomForm.nameMode === 'custom'">
          <el-input v-model="batchRoomForm.name_prefix" placeholder="如 A、B、东" style="width: 150px;" />
        </el-form-item>
        <el-form-item label="名称后缀" v-if="batchRoomForm.nameMode === 'custom'">
          <el-input v-model="batchRoomForm.name_suffix" placeholder="如 室" style="width: 150px;" />
        </el-form-item>
        <el-form-item label="起始号" prop="start_num">
          <el-input-number v-model="batchRoomForm.start_num" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="结束号" prop="end_num">
          <el-input-number v-model="batchRoomForm.end_num" :min="0" :max="9999" />
        </el-form-item>
        <el-alert type="info" :closable="false" style="margin-top: 10px;">
          <template #title>
            <span v-if="batchRoomForm.nameMode === 'number'">
              预览：{{ batchRoomForm.start_num }} ~ {{ batchRoomForm.end_num }}，共 {{ Math.max(0, batchRoomForm.end_num - batchRoomForm.start_num + 1) }} 个房间
            </span>
            <span v-else-if="batchRoomForm.nameMode === 'prefix'">
              预览：{{ batchRoomForm.name_prefix || 'X' }}{{ batchRoomForm.start_num }} ~ {{ batchRoomForm.name_prefix || 'X' }}{{ batchRoomForm.end_num }}，共 {{ Math.max(0, batchRoomForm.end_num - batchRoomForm.start_num + 1) }} 个房间
            </span>
            <span v-else>
              预览：{{ batchRoomForm.name_prefix || '' }}{{ batchRoomForm.start_num }}{{ batchRoomForm.name_suffix || '' }} ~ {{ batchRoomForm.name_prefix || '' }}{{ batchRoomForm.end_num }}{{ batchRoomForm.name_suffix || '' }}，共 {{ Math.max(0, batchRoomForm.end_num - batchRoomForm.start_num + 1) }} 个房间
            </span>
          </template>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="showBatchRoomDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchCreateRooms" :loading="batchRoomCreating">批量创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { locationApi } from '@/api'

const activeTab = ref('campus')
const dialogVisible = ref(false)
const showBatchFloorDialog = ref(false)
const showBatchRoomDialog = ref(false)
const batchCreating = ref(false)
const batchRoomCreating = ref(false)
const floorLoading = ref(false)
const roomLoading = ref(false)
const editType = ref('')
const editId = ref(null)
const formRef = ref()
const batchFormRef = ref()
const batchRoomFormRef = ref()

const campusList = ref([])
const buildingList = ref([])
const allBuildingList = ref([])
const allFloorList = ref([])
const floorList = ref([])
const roomList = ref([])

const buildingFilter = reactive({ campus: null })
const floorFilter = reactive({ campus: null, building: null })
const roomFilter = reactive({ campus: null, building: null, floor: null })

const roomBuildingList = ref([])
const roomFloorList = ref([])
const roomFormBuildingList = ref([])
const roomFormFloorList = ref([])

const form = reactive({
  name: '', code: '', description: '', sort_order: 0,
  campus: null,
  _campus: null,
  _building: null,
  building: null, floor_number: 1,
  floor: null, sort: 0
})

const formBuildingList = ref([])

const batchForm = reactive({
  campus: null, building: null,
  start_floor: 1, end_floor: 6
})
const batchBuildingList = ref([])

const batchRoomForm = reactive({
  campus: null, building: null, floor: null,
  nameMode: 'number',
  name_prefix: '', name_suffix: '',
  start_num: 101, end_num: 120
})
const batchRoomBuildingList = ref([])
const batchRoomFloorList = ref([])

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  campus: [{ required: true, message: '请选择院区', trigger: 'change' }],
  _campus: [{ required: true, message: '请选择院区', trigger: 'change' }],
  _building: [{ required: true, message: '请选择楼栋', trigger: 'change' }],
  building: [{ required: true, message: '请选择楼栋', trigger: 'change' }],
  floor: [{ required: true, message: '请选择楼层', trigger: 'change' }]
}

const batchRules = {
  campus: [{ required: true, message: '请选择院区', trigger: 'change' }],
  building: [{ required: true, message: '请选择楼栋', trigger: 'change' }],
  start_floor: [{ required: true, message: '请输入起始楼层', trigger: 'blur' }],
  end_floor: [{ required: true, message: '请输入结束楼层', trigger: 'blur' }]
}

const batchRoomRules = {
  campus: [{ required: true, message: '请选择院区', trigger: 'change' }],
  building: [{ required: true, message: '请选择楼栋', trigger: 'change' }],
  floor: [{ required: true, message: '请选择楼层', trigger: 'change' }],
  start_num: [{ required: true, message: '请输入起始号', trigger: 'blur' }],
  end_num: [{ required: true, message: '请输入结束号', trigger: 'blur' }]
}

const apiMap = {
  campus: locationApi.campus,
  building: locationApi.building,
  floor: locationApi.floor,
  room: locationApi.room
}

const dialogTitle = computed(() => {
  const titles = { campus: '院区', building: '楼栋', floor: '楼层', room: '房间' }
  return (editId.value ? '编辑' : '新增') + (titles[editType.value] || '')
})

const filteredBuildingsForFloor = computed(() => {
  if (!floorFilter.campus) return allBuildingList.value
  const target = String(floorFilter.campus).trim()
  if (!target) return allBuildingList.value
  return allBuildingList.value.filter(b => String(b.campus ?? b.campus_id ?? '').trim() === target)
})

onMounted(() => {
  loadCampuses()
  loadAllForSelect()
})

const handleTabChange = (tab) => {
  if (tab === 'room') loadRooms()
}

const loadCampuses = async () => {
  try {
    const res = await locationApi.campus.list()
    campusList.value = res.results || []
  } catch (e) { console.error(e) }
}

const loadBuildings = async () => {
  try {
    const params = {}
    if (buildingFilter.campus) params.campus = buildingFilter.campus
    const res = await locationApi.building.list(params)
    buildingList.value = res.results || []
  } catch (e) { console.error(e) }
}

const loadFloors = async () => {
  floorLoading.value = true
  try {
    const params = {}
    if (floorFilter.building) params.building = floorFilter.building
    else if (floorFilter.campus) params.campus = floorFilter.campus
    const res = await locationApi.floor.list(params)
    floorList.value = Array.isArray(res) ? res : (res.results || [])
  } catch (e) { console.error(e) }
  finally { floorLoading.value = false }
}

const loadRooms = async () => {
  roomLoading.value = true
  try {
    const params = {}
    if (roomFilter.floor) params.floor_id = roomFilter.floor
    else if (roomFilter.building) params.building_id = roomFilter.building
    else if (roomFilter.campus) params.campus_id = roomFilter.campus
    const res = await locationApi.room.list(params)
    roomList.value = res.results || []
  } catch (e) { console.error(e) }
  finally { roomLoading.value = false }
}

const loadAllForSelect = async () => {
  try {
    const [bRes, fRes] = await Promise.all([
      locationApi.building.listAll(),
      locationApi.floor.listAll()
    ])
    allBuildingList.value = Array.isArray(bRes) ? bRes : (bRes.data || [])
    allFloorList.value = Array.isArray(fRes) ? fRes : (fRes.data || [])
  } catch (e) { console.error(e) }
}

const resetForm = () => {
  Object.assign(form, {
    name: '', code: '', description: '', sort_order: 0,
    campus: null, _campus: null, _building: null,
    building: null, floor_number: 1,
    floor: null, sort: 0
  })
  formBuildingList.value = []
  roomFormBuildingList.value = []
  roomFormFloorList.value = []
}

const getSubmitData = () => {
  const data = {}
  if (editType.value === 'campus') {
    data.name = form.name
    data.code = form.code
    data.description = form.description
    data.sort_order = form.sort_order
  } else if (editType.value === 'building') {
    data.campus = form.campus
    data.name = form.name
    data.code = form.code
  } else if (editType.value === 'floor') {
    data.building = form.building
    data.floor_number = form.floor_number
  } else if (editType.value === 'room') {
    data.floor = form.floor
    data.name = form.name
    data.sort = form.sort
  }
  return data
}

const handleAdd = (type) => {
  editType.value = type
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = async (type, row) => {
  editType.value = type
  editId.value = row.id
  resetForm()
  Object.assign(form, { ...row })
  if (type === 'floor') {
    form._campus = row.campus || null
    form.building = row.building || null
    if (form._campus) await loadFormBuildings(form._campus)
  } else if (type === 'room') {
    form._campus = row.campus_name ? campusList.value.find(c => c.name === row.campus_name)?.id : null
    form._building = null
    form.floor = row.floor || null
    if (form._campus) {
      await loadRoomFormBuildings(form._campus)
      const bItem = roomFormBuildingList.value.find(b => b.name === row.building_name)
      if (bItem) {
        form._building = bItem.id
        await loadRoomFormFloors(bItem.id)
      }
    }
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  const api = apiMap[editType.value]
  const data = getSubmitData()

  try {
    if (editId.value) {
      await api.update(editId.value, data)
      ElMessage.success('更新成功')
    } else {
      await api.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    refreshAfterSubmit(editType.value)
  } catch (e) {
    const msg = e.response?.data?.message
      || e.response?.data?.code?.[0]
      || e.response?.data?.non_field_errors?.[0]
      || e.message
    ElMessage.error(msg || '提交失败，请检查输入')
  }
}

const refreshAfterSubmit = (type) => {
  if (type === 'campus') { loadCampuses(); loadAllForSelect() }
  else if (type === 'building') { loadBuildings(); loadAllForSelect() }
  else if (type === 'floor') { loadFloors(); loadAllForSelect() }
  else if (type === 'room') { loadRooms() }
}

const handleDelete = async (type, id) => {
  await ElMessageBox.confirm('确定要删除吗？关联数据可能受影响。', '提示', { type: 'warning' })
  await apiMap[type].delete(id)
  ElMessage.success('删除成功')
  refreshAfterSubmit(type)
}

const onFloorCampusChange = () => {
  floorFilter.building = null
  floorList.value = []
}

const onRoomCampusChange = async () => {
  roomFilter.building = null
  roomFilter.floor = null
  roomFloorList.value = []
  roomList.value = []
  if (roomFilter.campus) {
    try {
      const res = await locationApi.building.list({ campus: roomFilter.campus })
      roomBuildingList.value = res.results || []
    } catch (e) { console.error(e) }
  } else {
    roomBuildingList.value = []
  }
}

const onRoomBuildingChange = async () => {
  roomFilter.floor = null
  roomList.value = []
  if (roomFilter.building) {
    try {
      const res = await locationApi.floor.list({ building: roomFilter.building })
      roomFloorList.value = Array.isArray(res) ? res : (res.results || [])
    } catch (e) { console.error(e) }
  } else {
    roomFloorList.value = []
  }
}

const onFormCampusChange = async () => {
  form.building = null
  if (form._campus) await loadFormBuildings(form._campus)
}

const loadFormBuildings = async (campusId) => {
  try {
    const res = await locationApi.building.list({ campus: campusId })
    formBuildingList.value = res.results || []
  } catch (e) { console.error(e) }
}

const onRoomFormCampusChange = async () => {
  form._building = null
  form.floor = null
  roomFormFloorList.value = []
  if (form._campus) {
    await loadRoomFormBuildings(form._campus)
  } else {
    roomFormBuildingList.value = []
  }
}

const loadRoomFormBuildings = async (campusId) => {
  try {
    const res = await locationApi.building.list({ campus: campusId })
    roomFormBuildingList.value = res.results || []
  } catch (e) { console.error(e) }
}

const onRoomFormBuildingChange = async () => {
  form.floor = null
  if (form._building) {
    await loadRoomFormFloors(form._building)
  } else {
    roomFormFloorList.value = []
  }
}

const loadRoomFormFloors = async (buildingId) => {
  try {
    const res = await locationApi.floor.list({ building: buildingId })
    roomFormFloorList.value = Array.isArray(res) ? res : (res.results || [])
  } catch (e) { console.error(e) }
}

const onBatchCampusChange = async () => {
  batchForm.building = null
  if (batchForm.campus) {
    const res = await locationApi.building.list({ campus: batchForm.campus })
    batchBuildingList.value = res.results || []
  } else {
    batchBuildingList.value = []
  }
}

const handleBatchCreateFloors = async () => {
  await batchFormRef.value.validate()
  batchCreating.value = true
  try {
    const res = await locationApi.floor.batchCreate(batchForm)
    ElMessage.success(res.message || '批量创建完成')
    showBatchFloorDialog.value = false
    Object.assign(batchForm, { campus: null, building: null, start_floor: 1, end_floor: 6 })
    loadFloors()
    loadAllForSelect()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '批量创建失败')
  } finally {
    batchCreating.value = false
  }
}

const onBatchRoomCampusChange = async () => {
  batchRoomForm.building = null
  batchRoomForm.floor = null
  batchRoomFloorList.value = []
  if (batchRoomForm.campus) {
    try {
      const res = await locationApi.building.list({ campus: batchRoomForm.campus })
      batchRoomBuildingList.value = res.results || []
    } catch (e) { console.error(e) }
  } else {
    batchRoomBuildingList.value = []
  }
}

const onBatchRoomBuildingChange = async () => {
  batchRoomForm.floor = null
  if (batchRoomForm.building) {
    try {
      const res = await locationApi.floor.list({ building: batchRoomForm.building })
      batchRoomFloorList.value = Array.isArray(res) ? res : (res.results || [])
    } catch (e) { console.error(e) }
  } else {
    batchRoomFloorList.value = []
  }
}

const handleBatchCreateRooms = async () => {
  await batchRoomFormRef.value.validate()
  batchRoomCreating.value = true
  try {
    const data = {
      floor: batchRoomForm.floor,
      start_num: batchRoomForm.start_num,
      end_num: batchRoomForm.end_num,
      name_prefix: batchRoomForm.nameMode === 'number' ? '' : batchRoomForm.name_prefix,
      name_suffix: batchRoomForm.nameMode === 'custom' ? batchRoomForm.name_suffix : ''
    }
    const res = await locationApi.room.batchCreate(data)
    ElMessage.success(res.message || '批量创建完成')
    showBatchRoomDialog.value = false
    Object.assign(batchRoomForm, {
      campus: null, building: null, floor: null,
      nameMode: 'number', name_prefix: '', name_suffix: '',
      start_num: 101, end_num: 120
    })
    batchRoomBuildingList.value = []
    batchRoomFloorList.value = []
    loadRooms()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '批量创建失败')
  } finally {
    batchRoomCreating.value = false
  }
}
</script>

<style scoped lang="scss">
.location-manage {
  .tab-header {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  :deep(.el-tabs__header) {
    background: #fff;
  }
}
</style>
