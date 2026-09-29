<template>
  <div class="page">
    <div class="page-header"><h2>留言管理</h2></div>

    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索留言标题或内容" style="width: 220px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>

      <el-table :data="tableData" stripe v-loading="loading" style="width:100%;" :cell-style="{padding:'12px 0'}" :header-cell-style="{padding:'12px 0'}">
        <el-table-column prop="id" label="序号" width="70" />
        <el-table-column prop="user_name" label="留言用户" width="120" />
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="content" label="内容" min-width="260" show-overflow-tooltip />
        <el-table-column prop="created_at" label="留言时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
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

    <el-dialog v-model="viewVisible" title="留言详情" width="560px">
      <div v-if="currentItem" class="message-detail">
        <div class="detail-item">
          <span class="detail-label">留言用户：</span>
          <span>{{ currentItem.user_name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">标题：</span>
          <span>{{ currentItem.title }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">内容：</span>
          <span class="detail-content">{{ currentItem.content }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">留言时间：</span>
          <span>{{ formatDate(currentItem.created_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { messageBoardApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const viewVisible = ref(false)
const currentItem = ref(null)

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await messageBoardApi.adminList(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleView = (row) => {
  currentItem.value = row
  viewVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该留言？删除后不可恢复', '提示', { type: 'warning' })
    await messageBoardApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
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
  margin-bottom: 16px;
}

.message-detail {
  .detail-item {
    margin: 14px 0;
    font-size: 14px;
    color: #333;

    .detail-label {
      font-weight: 500;
      color: #666;
    }

    .detail-content {
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}
</style>
