<template>
  <div class="page">
    <div class="page-header"><h2>维修知识库</h2></div>
    
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索标题/关键词" style="width: 250px; margin-right: 10px;" clearable />
        <el-select v-model="filterEquipmentType" placeholder="设备类型筛选" clearable style="width: 150px; margin-right: 10px;">
          <el-option v-for="t in equipmentTypes" :key="t.id" :label="t.type_name" :value="t.id" />
        </el-select>
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>
      
      <el-row :gutter="20">
        <el-col :span="8" v-for="item in tableData" :key="item.id">
          <el-card class="knowledge-card" shadow="hover" @click="handleView(item)">
            <div class="knowledge-header">
              <el-tag type="primary" size="small">{{ item.equipment_type_name || '未分类' }}</el-tag>
              <span class="view-count"><el-icon><View /></el-icon> {{ item.view_count }}</span>
            </div>
            <h3 class="knowledge-title">{{ item.title }}</h3>
            <p class="knowledge-desc">{{ truncateText(item.problem_description, 100) }}</p>
            <div class="knowledge-footer">
              <span class="author">{{ item.author }}</span>
              <span class="time">{{ formatDate(item.created_at) }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-if="tableData.length === 0" description="暂无知识库内容" />
      
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>
    
    <el-dialog v-model="viewVisible" :title="currentItem?.title" width="700px">
      <div v-if="currentItem">
        <div class="detail-header">
          <el-tag type="primary">{{ currentItem.equipment_type_name || '未分类' }}</el-tag>
          <span class="view-count"><el-icon><View /></el-icon> {{ currentItem.view_count }} 次浏览</span>
        </div>
        
        <el-divider content-position="left">问题描述</el-divider>
        <p class="detail-content">{{ currentItem.problem_description }}</p>
        
        <el-divider content-position="left">解决方案</el-divider>
        <p class="detail-content">{{ currentItem.solution }}</p>
        
        <div v-if="currentItem.images && currentItem.images.length > 0" style="margin-top: 20px;">
          <el-divider content-position="left">相关图片</el-divider>
          <el-image
            v-for="(img, index) in currentItem.images"
            :key="index"
            :src="img"
            :preview-src-list="currentItem.images"
            style="width: 200px; height: 150px; margin-right: 10px;"
            fit="cover"
          />
        </div>
        
        <div class="detail-footer">
          <el-button type="success" @click="handleUseful(currentItem)" v-if="!currentItem.is_useful">
            <el-icon><CircleCheck /></el-icon> 有帮助 ({{ currentItem.useful_count }})
          </el-button>
          <el-button type="info" disabled v-else>
            <el-icon><CircleCheck /></el-icon> 已点赞 ({{ currentItem.useful_count }})
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { knowledgeApi, equipmentApi } from '@/api'
import { ElMessage } from 'element-plus'
import { View, CircleCheck } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)
const searchKeyword = ref('')
const filterEquipmentType = ref('')
const equipmentTypes = ref([])

const viewVisible = ref(false)
const currentItem = ref(null)

onMounted(async () => {
  await loadEquipmentTypes()
  loadData()
})

const loadEquipmentTypes = async () => {
  try {
    const res = await equipmentApi.typeList({ page_size: 100 })
    equipmentTypes.value = res.results || []
  } catch (error) {
    console.error(error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterEquipmentType.value) params.equipment_type = filterEquipmentType.value
    
    const res = await knowledgeApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleView = async (item) => {
  currentItem.value = item
  viewVisible.value = true
  try {
    await knowledgeApi.view(item.id)
    item.view_count++
  } catch (error) {
    console.error(error)
  }
}

const handleUseful = async (item) => {
  try {
    await knowledgeApi.useful(item.id)
    item.useful_count++
    item.is_useful = true
    ElMessage.success('感谢您的反馈')
  } catch (error) {
    console.error(error)
  }
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped lang="scss">
.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.knowledge-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
  
  &:hover {
    transform: translateY(-3px);
  }
  
  .knowledge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    
    .view-count {
      font-size: 12px;
      color: #999;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }
  
  .knowledge-title {
    font-size: 16px;
    margin: 0 0 10px 0;
    color: #333;
  }
  
  .knowledge-desc {
    font-size: 13px;
    color: #666;
    line-height: 1.5;
    margin: 0 0 10px 0;
  }
  
  .knowledge-footer {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #999;
  }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  
  .view-count {
    font-size: 13px;
    color: #999;
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}

.detail-footer {
  margin-top: 20px;
  text-align: center;
}
</style>
