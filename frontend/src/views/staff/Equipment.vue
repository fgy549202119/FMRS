<template>
  <div class="page">
    <div class="page-header"><h2>公共设备</h2></div>

    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索设备名称" style="width: 200px; margin-right: 10px;" clearable @keyup.enter="loadData" />
        <el-select v-model="filterType" placeholder="设备类型" clearable style="width: 150px; margin-right: 10px;">
          <el-option v-for="item in equipmentTypes" :key="item.id" :label="item.type_name" :value="item.id" />
        </el-select>
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>

      <el-row :gutter="20" v-loading="loading">
        <el-col :span="6" v-for="item in tableData" :key="item.id">
          <el-card class="equipment-card" shadow="hover" @click="handleView(item)">
            <div class="equipment-image">
              <el-image :src="item.equipment_image" fit="cover" style="width: 100%; height: 150px;">
                <template #error>
                  <div class="image-placeholder"><el-icon><Monitor /></el-icon><span>暂无图片</span></div>
                </template>
              </el-image>
              <el-tag :type="getStatusType(item.status)" class="status-tag">{{ item.status }}</el-tag>
            </div>
            <div class="equipment-info">
              <h4>{{ item.equipment_name }}</h4>
              <p><el-icon><Box /></el-icon> {{ item.equipment_type_detail?.type_name || item.equipment_type_name || '未分类' }}</p>
              <p v-if="item.location_info?.full_location && item.location_info.full_location !== '-'"><el-icon><Location /></el-icon> {{ item.location_info.full_location }}</p>
              <p><el-icon><Document /></el-icon> {{ item.specification || '-' }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && tableData.length === 0" description="暂无设备数据" />

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <el-dialog v-model="viewVisible" title="设备详情" width="780px">
      <div v-if="currentItem" class="equipment-detail">
        <div class="detail-header">
          <div v-if="currentItem.equipment_image" class="detail-image">
            <el-image :src="currentItem.equipment_image" fit="cover" :preview-src-list="[currentItem.equipment_image]" preview-teleported />
          </div>
          <div class="detail-title">
            <h3>{{ currentItem.equipment_name }}</h3>
            <span class="equipment-no">{{ currentItem.equipment_no }}</span>
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
            <el-descriptions-item label="设备序号" :span="1">{{ currentItem.sequence_number }}</el-descriptions-item>
            <el-descriptions-item label="设备状态" :span="1">
              <el-tag :type="getStatusType(currentItem.status)">{{ currentItem.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="发布时间" :span="2">{{ formatDate(currentItem.publish_time) }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { equipmentApi } from '@/api'
import { Monitor, Box, Document, Location } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const searchKeyword = ref('')
const filterType = ref('')
const equipmentTypes = ref([])
const viewVisible = ref(false)
const currentItem = ref(null)

onMounted(async () => {
  await Promise.all([loadEquipmentTypes(), loadData()])
})

const loadEquipmentTypes = async () => {
  try {
    const res = await equipmentApi.typeOptions()
    equipmentTypes.value = Array.isArray(res) ? res : (res.data || [])
  } catch (e) { console.error(e) }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await equipmentApi.distinctNames(params)
    let results = res.results || []
    if (filterType.value) {
      results = results.filter(e => e.equipment_type === filterType.value)
    }
    const totalItems = results.length
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    tableData.value = results.slice(start, end)
    total.value = totalItems
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleView = (row) => { currentItem.value = row; viewVisible.value = true }

const getStatusType = (s) => { if (s === '正常') return 'success'; if (s === '故障') return 'danger'; if (String(s).includes('故障')) return 'warning'; return 'info' }

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped lang="scss">
.search-bar { display: flex; align-items: center; margin-bottom: 20px; }

.equipment-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
  &:hover { transform: translateY(-5px); }
  .equipment-image {
    position: relative;
    .status-tag { position: absolute; top: 10px; right: 10px; }
    .image-placeholder {
      width: 100%; height: 150px;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      gap: 8px; background: #f5f7fa; color: #909399; font-size: 40px;
      span { font-size: 13px; }
    }
  }
  .equipment-info {
    padding: 10px 0;
    h4 { margin: 0 0 10px; font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    p { margin: 5px 0; font-size: 12px; color: #666; display: flex; align-items: center; gap: 5px; }
  }
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
