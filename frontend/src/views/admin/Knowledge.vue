<template>
  <div class="page">
    <div class="page-header">
      <h2>维修知识库管理</h2>
      <el-button type="primary" @click="handleAdd">新增知识</el-button>
    </div>
    
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索标题/关键词" style="width: 250px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>
      
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="equipment_type_name" label="设备类型" width="150" />
        <el-table-column prop="equipment_type" label="设备类型ID" width="100" v-if="false" />
        <el-table-column prop="author" label="作者" width="100" />
        <el-table-column prop="view_count" label="浏览次数" width="120" />
        <el-table-column prop="useful_count" label="有用次数" width="120" />
        <el-table-column prop="is_published" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'">
              {{ row.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
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
    
    <el-dialog v-model="formVisible" :title="formTitle" width="700px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item prop="title" label="标题">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="form.equipment_type" placeholder="请选择设备类型" style="width: 100%;" filterable>
            <el-option v-for="item in equipmentTypes" :key="item.id" :label="item.type_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item prop="problem_description" label="问题描述">
          <el-input v-model="form.problem_description" type="textarea" :rows="4" placeholder="请详细描述故障现象" />
        </el-form-item>
        <el-form-item prop="solution" label="解决方案">
          <el-input v-model="form.solution" type="textarea" :rows="6" placeholder="请详细描述解决方案和步骤" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="form.keywords" placeholder="多个关键词用逗号分隔" />
        </el-form-item>
        <el-form-item label="是否发布">
          <el-switch v-model="form.is_published" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { knowledgeApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const equipmentTypes = ref([])

const formVisible = ref(false)
const formTitle = ref('新增知识')
const submitting = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  title: '',
  equipment_type: null,
  problem_description: '',
  solution: '',
  keywords: '',
  is_published: true
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  problem_description: [{ required: true, message: '请输入问题描述', trigger: 'blur' }],
  solution: [{ required: true, message: '请输入解决方案', trigger: 'blur' }]
}

onMounted(async () => {
  await loadEquipmentTypes()
  loadData()
})

const loadEquipmentTypes = async () => {
  try {
    const { equipmentApi } = await import('@/api')
    const res = await equipmentApi.typeList({ page_size: 100 })
    equipmentTypes.value = res.results || []
  } catch (error) {
    console.error('加载设备类型失败:', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    
    const res = await knowledgeApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  formTitle.value = '新增知识'
  Object.assign(form, {
    id: null,
    title: '',
    equipment_type: null,
    problem_description: '',
    solution: '',
    keywords: '',
    is_published: true
  })
  formVisible.value = true
}

const handleEdit = (row) => {
  formTitle.value = '编辑知识'
  Object.assign(form, {
    id: row.id,
    title: row.title,
    equipment_type: row.equipment_type || null,
    problem_description: row.problem_description,
    solution: row.solution,
    keywords: row.keywords,
    is_published: row.is_published
  })
  formVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    const submitData = { ...form, author: '管理员' }
    if (submitData.keywords === null || submitData.keywords === undefined) {
      submitData.keywords = ''
    }
    if (form.id) {
      await knowledgeApi.update(form.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await knowledgeApi.create(submitData)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该知识？', '提示', { type: 'warning' })
  try {
    await knowledgeApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}



const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
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
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
</style>
