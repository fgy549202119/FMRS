<template>
  <div class="page">
    <div class="page-header">
      <h2>设备类型管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon> 新增类型
      </el-button>
    </div>
    
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索类型名称" style="width: 200px; margin-right: 10px;" clearable @keyup.enter="loadData" />
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>
      
      <el-row :gutter="20" v-loading="loading">
        <el-col :span="6" v-for="item in filteredData" :key="item.id">
          <el-card class="type-card" shadow="hover">
            <div class="type-icon" :style="{ background: getTypeColor(item.type_code || 'other') }">
              <el-icon :size="40">
                <component :is="getIconComponent(item.icon)" />
              </el-icon>
            </div>
            <div class="type-info">
              <h4>{{ item.type_name }}</h4>
              <p>{{ item.description || '暂无描述' }}</p>
              <div class="type-stats">
                <el-tag size="small" type="info">设备: {{ item.equipment_count || 0 }}</el-tag>
                <el-tag size="small" type="warning" v-if="item.fault_equipment_count > 0">故障: {{ item.fault_equipment_count || 0 }}</el-tag>
              </div>
            </div>
            <div class="type-actions">
              <el-button type="primary" link @click="handleEdit(item)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(item)">删除</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-if="!loading && filteredData.length === 0" description="暂无设备类型" />
    </el-card>
    
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑类型' : '新增类型'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="类型名称" prop="type_name">
          <el-input v-model="form.type_name" placeholder="请输入类型名称" />
        </el-form-item>
        <el-form-item label="类型编码" prop="type_code">
          <el-input v-model="form.type_code" placeholder="请输入类型编码（英文）" />
        </el-form-item>
        <el-form-item label="图标">
          <div class="icon-selector">
            <div 
              v-for="icon in iconList" 
              :key="icon" 
              :class="['icon-item', { active: form.icon === icon }]"
              @click="form.icon = icon"
            >
              <el-icon :size="24"><component :is="icon" /></el-icon>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="类型描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入类型描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, markRaw } from 'vue'
import { equipmentApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Document, Connection, Lightning,
  House, Warning, Top, Suitcase,
  Reading, View, More, Plus,
  Setting, Bowl, Brush, IceCream, Stamp, Coin, FirstAidKit
} from '@element-plus/icons-vue'
import { EventBus, Events } from '@/utils/eventBus'

const iconList = [
  'Monitor', 'Document', 'Connection', 'Lightning',
  'House', 'Warning', 'Top', 'Suitcase',
  'Reading', 'View', 'More',
  'Setting', 'Bowl', 'Brush', 'IceCream', 'Stamp', 'Coin', 'FirstAidKit'
]

const iconComponents = {
  Monitor: markRaw(Monitor),
  Document: markRaw(Document),
  Connection: markRaw(Connection),
  Lightning: markRaw(Lightning),
  House: markRaw(House),
  Warning: markRaw(Warning),
  Top: markRaw(Top),
  Suitcase: markRaw(Suitcase),
  Reading: markRaw(Reading),
  View: markRaw(View),
  More: markRaw(More),
  Setting: markRaw(Setting),
  Bowl: markRaw(Bowl),
  Brush: markRaw(Brush),
  IceCream: markRaw(IceCream),
  Stamp: markRaw(Stamp),
  Coin: markRaw(Coin),
  FirstAidKit: markRaw(FirstAidKit)
}

const getIconComponent = (icon) => {
  return iconComponents[icon] || Monitor
}

const getTypeColor = (code) => {
  const colors = {
    water_electric: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    door_window: 'linear-gradient(135deg, #fddb92 0%, #d1fdff 100%)',
    multimedia: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    network: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    dorm_furniture: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)',
    security: 'linear-gradient(135deg, #cd9cf2 0%, #f6f3ff 100%)',
    lab: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
    sports: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    canteen: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
    other: 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)'
  }
  return colors[code] || colors.other
}

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const searchKeyword = ref('')
const dialogVisible = ref(false)
const editId = ref(null)
const formRef = ref()

const form = reactive({
  type_name: '',
  type_code: '',
  icon: 'Monitor',
  description: '',
  sort_order: 0
})

const rules = {
  type_name: [{ required: true, message: '请输入类型名称', trigger: 'blur' }]
}

const filteredData = computed(() => {
  if (!searchKeyword.value) return tableData.value
  const keyword = searchKeyword.value.toLowerCase()
  return tableData.value.filter(item => 
    item.type_name?.toLowerCase().includes(keyword) ||
    item.type_code?.toLowerCase().includes(keyword)
  )
})

const faultRate = computed(() => 0)

onMounted(() => {
  loadData()
  
  EventBus.on(Events.DATA_REFRESH, handleDataRefresh)
})

onUnmounted(() => {
  EventBus.off(Events.DATA_REFRESH, handleDataRefresh)
})

const handleDataRefresh = async () => {
  await loadData()
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await equipmentApi.typeList({ page_size: 999 })
    // 开发调试用的 console.log 日志，在浏览器控制台打印接口返回的设备类型数据，方便排查
    // console.log('设备类型数据:', res, '数量:', (res.results || res || []).length)
    tableData.value = res.results || res || []
  } catch (error) {
    console.error('加载设备类型失败:', error)
    ElMessage.error('加载设备类型失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editId.value = null
  form.type_name = ''
  form.type_code = ''
  form.icon = 'Monitor'
  form.description = ''
  form.sort_order = 0
  dialogVisible.value = true
}

const handleEdit = (row) => {
  editId.value = row.id
  form.type_name = row.type_name
  form.type_code = row.type_code || ''
  form.icon = row.icon || 'Monitor'
  form.description = row.description || ''
  form.sort_order = row.sort_order || 0
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该设备类型？', '提示', { type: 'warning' })
  try {
    await equipmentApi.typeDelete(row.id)
    ElMessage.success('删除成功')
    EventBus.emit(Events.EQUIPMENT_TYPE_CHANGED, { action: 'delete', id: row.id })
    loadData()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editId.value) {
      await equipmentApi.typeUpdate(editId.value, form)
      ElMessage.success('修改成功')
      EventBus.emit(Events.EQUIPMENT_TYPE_CHANGED, { action: 'update', id: editId.value, data: form })
    } else {
      await equipmentApi.typeCreate(form)
      ElMessage.success('添加成功')
      EventBus.emit(Events.EQUIPMENT_TYPE_CHANGED, { action: 'create', data: form })
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-bar {
  margin-bottom: 20px;
}

.type-card {
  margin-bottom: 20px;
  text-align: center;
  
  .type-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 15px;
    color: #fff;
  }
  
  .type-info {
    h4 {
      margin: 0 0 10px;
      font-size: 16px;
    }
    
    p {
      margin: 0;
      font-size: 12px;
      color: #666;
      height: 36px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    
    .type-stats {
      margin-top: 10px;
      display: flex;
      gap: 8px;
      justify-content: center;
    }
  }
  
  .type-actions {
    margin-top: 15px;
    border-top: 1px solid #eee;
    padding-top: 10px;
  }
}

.icon-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  
  .icon-item {
    width: 40px;
    height: 40px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      border-color: #409eff;
      color: #409eff;
    }
    
    &.active {
      border-color: #409eff;
      background: #ecf5ff;
      color: #409eff;
    }
  }
}
</style>
