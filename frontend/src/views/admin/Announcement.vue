<template>
  <div class="page">
    <div class="page-header"><h2>校园公告管理</h2></div>
    
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索公告标题" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button type="primary" @click="handleAdd" style="margin-left: auto;">
          <el-icon><Plus /></el-icon> 发布公告
        </el-button>
      </div>
      
      <el-table :data="tableData" stripe v-loading="loading" style="width:100%;" :cell-style="{padding:'12px 0'}" :header-cell-style="{padding:'12px 0'}">
        <el-table-column prop="id" label="序号" width="70" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="publisher" label="发布人" width="130" />
        <el-table-column prop="publish_time" label="发布时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.publish_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
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
    
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑公告' : '发布公告'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="5" placeholder="请输入公告内容" />
        </el-form-item>
        <el-form-item label="发布人" prop="publisher">
          <el-input v-model="form.publisher" placeholder="请输入发布人" />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            class="image-uploader"
            action="/api/upload/"
            :data="{ type: 'announcement' }"
            :show-file-list="false"
            :on-success="handleImageSuccess"
          >
            <img v-if="form.image" :src="form.image" class="preview-image" />
            <el-icon v-else class="uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="viewVisible" title="公告详情" width="600px">
      <div v-if="currentItem">
        <h3>{{ currentItem.title }}</h3>
        <p class="meta">发布人: {{ currentItem.publisher }} | 发布时间: {{ formatDate(currentItem.publish_time) }}</p>
        <el-divider />
        <div class="content">{{ currentItem.content }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { announcementApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const dialogVisible = ref(false)
const viewVisible = ref(false)
const editId = ref(null)
const currentItem = ref(null)
const formRef = ref()

const form = reactive({
  title: '',
  content: '',
  publisher: '',
  image: ''
})

const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }],
  publisher: [{ required: true, message: '请输入发布人', trigger: 'blur' }]
}

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await announcementApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editId.value = null
  Object.assign(form, { title: '', content: '', publisher: '管理员', image: '' })
  dialogVisible.value = true
}

const handleView = (row) => {
  currentItem.value = row
  viewVisible.value = true
}

const handleEdit = (row) => {
  editId.value = row.id
  Object.assign(form, {
    title: row.title,
    content: row.content,
    publisher: row.publisher,
    image: row.image || ''
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该公告？', '提示', { type: 'warning' })
  try {
    await announcementApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editId.value) {
      await announcementApi.update(editId.value, form)
      ElMessage.success('修改成功')
    } else {
      await announcementApi.create(form)
      ElMessage.success('发布成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const handleImageSuccess = (response) => {
  if (response.code === 200) {
    form.image = response.url
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error(response.error || '图片上传失败')
  }
}
</script>

<style scoped lang="scss">
.meta {
  color: #999;
  font-size: 14px;
  margin: 10px 0;
}
.content {
  line-height: 1.8;
  white-space: pre-wrap;
}
.image-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    &:hover {
      border-color: #409eff;
    }
  }
  .preview-image {
    width: 150px;
    height: 150px;
    display: block;
    object-fit: cover;
  }
  .uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 150px;
    height: 150px;
    line-height: 150px;
    text-align: center;
  }
}
</style>
