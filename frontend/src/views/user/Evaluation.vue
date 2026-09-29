<template>
  <div class="page">
    <div class="page-header"><h2>服务评价</h2></div>
    
    <el-card v-if="pendingOrders.length > 0">
      <template #header>
        <span>待评价工单</span>
      </template>
      <el-table :data="pendingOrders" stripe>
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column prop="staff_name" label="维修员" width="100" />
        <el-table-column prop="complete_time" label="完成时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.complete_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openEvaluation(row)">评价</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>已评价记录</span>
      </template>
      <el-table :data="evaluatedOrders" stripe>
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column prop="staff_name" label="维修员" width="100" />
        <el-table-column label="评分" width="200">
          <template #default="{ row }">
            <div v-if="row.evaluation" class="rating-display">
              <el-rate v-model="row.evaluation.rating" disabled />
              <span class="rating-text">{{ row.evaluation.rating }}分</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="evaluation.created_at" label="评价时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.evaluation?.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewEvaluation(row)">查看</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteEval(row)" v-if="row.evaluation">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="evaluationVisible" title="服务评价" width="500px">
      <div class="evaluation-form">
        <div class="order-info">
          <p><strong>报修编号：</strong>{{ currentOrder?.repair_no }}</p>
          <p><strong>维修员：</strong>{{ currentOrder?.staff_name }}</p>
          <p><strong>设备名称：</strong>{{ currentOrder?.equipment_name }}</p>
        </div>
        
        <el-divider />
        
        <div class="rating-section">
          <div class="rating-item">
            <span class="rating-label">维修质量</span>
            <el-rate v-model="evaluationForm.quality_rating" show-text :texts="ratingTexts" />
          </div>
          
          <div class="rating-item">
            <span class="rating-label">响应速度</span>
            <el-rate v-model="evaluationForm.speed_rating" show-text :texts="ratingTexts" />
          </div>
          
          <div class="rating-item">
            <span class="rating-label">服务态度</span>
            <el-rate v-model="evaluationForm.attitude_rating" show-text :texts="ratingTexts" />
          </div>
        </div>
        
        <el-divider />
        
        <div class="overall-rating">
          <span class="rating-label">综合评分</span>
          <el-rate v-model="overallRating" disabled show-score text-color="#ff9900" />
        </div>
        
        <el-input
          v-model="evaluationForm.content"
          type="textarea"
          :rows="4"
          placeholder="请输入评价内容（选填）"
          style="margin-top: 15px;"
        />
      </div>
      <template #footer>
        <el-button @click="evaluationVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEvaluation" :loading="submitting">提交评价</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="detailVisible" title="评价详情" width="500px">
      <div v-if="currentEvaluation" class="evaluation-detail">
        <div class="order-info">
          <p><strong>报修编号：</strong>{{ currentEvaluation.repair_no }}</p>
          <p><strong>维修人员：</strong>{{ currentEvaluation.staff_name }}</p>
        </div>
        
        <el-divider />
        
        <div class="rating-section">
          <div class="rating-item">
            <span class="rating-label">维修质量</span>
            <el-rate v-model="currentEvaluation.quality_rating" disabled />
          </div>
          
          <div class="rating-item">
            <span class="rating-label">响应速度</span>
            <el-rate v-model="currentEvaluation.speed_rating" disabled />
          </div>
          
          <div class="rating-item">
            <span class="rating-label">服务态度</span>
            <el-rate v-model="currentEvaluation.attitude_rating" disabled />
          </div>
        </div>
        
        <el-divider />
        
        <div class="overall-rating">
          <span class="rating-label">综合评分</span>
          <el-rate v-model="currentEvaluation.rating" disabled show-score text-color="#ff9900" />
        </div>
        
        <div class="content-section" v-if="currentEvaluation.content">
          <el-divider />
          <p><strong>评价内容：</strong></p>
          <p>{{ currentEvaluation.content }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { repairApi, evaluationApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

const pendingOrders = ref([])
const evaluatedOrders = ref([])
const evaluationVisible = ref(false)
const detailVisible = ref(false)
const currentOrder = ref(null)
const currentEvaluation = ref(null)
const submitting = ref(false)

const ratingTexts = ['很差', '较差', '一般', '较好', '很好']

const evaluationForm = reactive({
  quality_rating: 5,
  speed_rating: 5,
  attitude_rating: 5,
  content: ''
})

const overallRating = computed(() => {
  return Math.round((evaluationForm.quality_rating + evaluationForm.speed_rating + evaluationForm.attitude_rating) / 3)
})

onMounted(() => {
  loadData()
})

const loadData = async () => {
  try {
    const [pendingRes, evalRes, completedRes] = await Promise.all([
      repairApi.pendingEvaluation({ page_size: 100 }),
      evaluationApi.list({ page_size: 100 }),
      repairApi.orderList({ page_size: 200, status: 'CLOSED' })
    ])
    
    pendingOrders.value = pendingRes.results || []
    
    const evaluations = evalRes.results || []
    const reEvalOrders = evaluations.filter(e => e.is_hidden && e.appeal_status === 'approved').map(e => e.order_id)
    
    const completedOrders = completedRes.results || []
    
    const evaluatedIds = new Set(evaluations.filter(e => !e.is_hidden).map(e => e.order_id).filter(Boolean))
    
    evaluatedOrders.value = completedOrders.filter(o => evaluatedIds.has(o.id)).map(o => {
      const eval_ = evaluations.find(e => e.order_id === o.id && !e.is_hidden)
      return { ...o, evaluation: eval_ }
    })

    const reEvalIds = new Set(reEvalOrders)
    const reEvalCompleted = completedOrders.filter(o => reEvalIds.has(o.id))
    for (const o of reEvalCompleted) {
      if (!pendingOrders.value.find(p => p.id === o.id)) {
        pendingOrders.value.push(o)
      }
    }
  } catch (error) {
    console.error(error)
  }
}

const openEvaluation = (order) => {
  currentOrder.value = order
  evaluationForm.quality_rating = 5
  evaluationForm.speed_rating = 5
  evaluationForm.attitude_rating = 5
  evaluationForm.content = ''
  evaluationVisible.value = true
}

const submitEvaluation = async () => {
  submitting.value = true
  try {
    await evaluationApi.create({
      repair_order: currentOrder.value.id,
      quality_rating: evaluationForm.quality_rating,
      speed_rating: evaluationForm.speed_rating,
      attitude_rating: evaluationForm.attitude_rating,
      content: evaluationForm.content
    })
    ElMessage.success('评价成功')
    evaluationVisible.value = false
    loadData()
  } catch (error) { ElMessage.error(error.response?.data?.message || error.message || '评价失败，请稍后重试') } finally {
    submitting.value = false
  }
}

const viewEvaluation = (order) => {
  currentEvaluation.value = order.evaluation
  detailVisible.value = true
}

const handleDeleteEval = async (row) => {
  if (!row.evaluation) return
  try {
    await ElMessageBox.confirm('确定删除该评价？删除后不可恢复', '提示', { type: 'warning' })
    await evaluationApi.delete(row.evaluation.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped lang="scss">
.evaluation-form, .evaluation-detail {
  .order-info {
    p {
      margin: 8px 0;
      color: #666;
    }
  }
  
  .rating-section {
    .rating-item {
      display: flex;
      align-items: center;
      margin: 15px 0;
      
      .rating-label {
        width: 80px;
        font-weight: 500;
      }
    }
  }
  
  .overall-rating {
    display: flex;
    align-items: center;
    
    .rating-label {
      width: 80px;
      font-weight: 500;
    }
  }
  
  .content-section {
    p {
      margin: 5px 0;
    }
  }
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 10px;
  
  .rating-text {
    color: #ff9900;
    font-weight: 500;
  }
}
</style>
