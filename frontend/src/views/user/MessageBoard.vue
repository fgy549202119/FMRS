<template>
  <div class="page">
    <div class="page-header">
      <h2>留言板</h2>
      <el-button type="primary" @click="showAddDialog">新增留言</el-button>
    </div>

    <el-card>
      <el-table :data="messages" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="content" label="内容" min-width="280" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewMessage(row)">查看</el-button>
            <el-button type="danger" link size="small" @click="deleteMessage(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadMessages"
        />
      </div>
    </el-card>

    <el-dialog v-model="addDialogVisible" title="新增留言" width="520px" @close="resetForm">
      <el-form :model="messageForm" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="messageForm.title" placeholder="请输入留言标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="messageForm.content" type="textarea" :rows="5" placeholder="请输入留言内容" maxlength="1000" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createMessage" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="留言详情" width="520px">
      <div v-if="currentMessage" class="message-detail">
        <div class="detail-item">
          <span class="detail-label">标题：</span>
          <span>{{ currentMessage.title }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">内容：</span>
          <span class="detail-content">{{ currentMessage.content }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">创建时间：</span>
          <span>{{ formatDate(currentMessage.created_at) }}</span>
        </div>
        <div class="detail-item" v-if="currentMessage.updated_at && currentMessage.updated_at !== currentMessage.created_at">
          <span class="detail-label">更新时间：</span>
          <span>{{ formatDate(currentMessage.updated_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { messageBoardApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const messages = ref([])
const loading = ref(false)
const submitting = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const addDialogVisible = ref(false)
const detailVisible = ref(false)
const currentMessage = ref(null)
const formRef = ref(null)

const messageForm = reactive({
  title: '',
  content: ''
})

const formRules = {
  title: [{ required: true, message: '请输入留言标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入留言内容', trigger: 'blur' }]
}

onMounted(() => {
  loadMessages()
})

const loadMessages = async () => {
  loading.value = true
  try {
    const res = await messageBoardApi.list({
      page: currentPage.value,
      page_size: pageSize.value
    })
    messages.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  addDialogVisible.value = true
}

const resetForm = () => {
  messageForm.title = ''
  messageForm.content = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const createMessage = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    await messageBoardApi.create({
      title: messageForm.title,
      content: messageForm.content
    })
    ElMessage.success('留言成功')
    addDialogVisible.value = false
    currentPage.value = 1
    loadMessages()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '留言失败')
  } finally {
    submitting.value = false
  }
}

const viewMessage = (row) => {
  currentMessage.value = row
  detailVisible.value = true
}

const deleteMessage = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该留言？删除后不可恢复', '提示', { type: 'warning' })
    await messageBoardApi.delete(row.id)
    ElMessage.success('删除成功')
    loadMessages()
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
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    margin: 0;
  }
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.message-detail {
  .detail-item {
    margin: 12px 0;
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
