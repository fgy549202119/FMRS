<template>
  <div class="page">
    <div class="page-header"><h2>备件库存管理</h2></div>

    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索备件编号/名称" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button type="warning" @click="loadLowStock">库存预警</el-button>
        <el-button type="success" @click="handleExport">导出Excel</el-button>
        <el-button type="primary" @click="handleAdd" style="margin-left: auto;">新增备件</el-button>
      </div>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="part_no" label="备件编号" width="120" />
        <el-table-column prop="name" label="备件名称" width="150"/>
        <el-table-column prop="specification" label="规格型号" />
        <el-table-column prop="supplier" label="供货商" width="140" show-overflow-tooltip />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="quantity" label="库存数量" width="100">
          <template #default="{ row }">
            <el-tag :type="row.quantity <= 0 ? 'danger' : 'success'">{{ row.quantity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">¥{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column prop="storage_location" label="存放位置" width="140" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="success" link @click="handleStockIn(row)">入库</el-button>
            <el-button type="warning" link @click="handleStockOut(row)">出库</el-button>
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

    <el-dialog v-model="formVisible" :title="formTitle" width="550px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="part_no" label="备件编号">
              <el-input v-model="form.part_no" placeholder="请输入备件编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="name" label="备件名称">
              <el-input v-model="form.name" placeholder="请输入备件名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格型号">
              <el-input v-model="form.specification" placeholder="请输入规格型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供货商">
              <el-input v-model="form.supplier" placeholder="请输入供货商" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单位">
              <el-select v-model="form.unit" style="width: 100%;">
                <el-option label="个" value="个" />
                <el-option label="件" value="件" />
                <el-option label="套" value="套" />
                <el-option label="米" value="米" />
                <el-option label="公斤" value="公斤" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="存放位置">
              <el-input v-model="form.storage_location" placeholder="请输入存放位置" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价">
              <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="stockVisible" :title="stockTitle" width="400px">
      <el-form :model="stockForm" :rules="stockRules" ref="stockFormRef" label-width="80px">
        <el-form-item label="备件名称">
          <el-input :value="currentPart?.name" disabled />
        </el-form-item>
        <el-form-item label="当前库存">
          <el-input :value="currentPart?.quantity" disabled />
        </el-form-item>
        <el-form-item prop="quantity" :label="stockType === 'in' ? '入库数量' : '出库数量'">
          <el-input-number v-model="stockForm.quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="关联单号">
          <el-input v-model="stockForm.related_order_no" placeholder="可选" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStock" :loading="stocking">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { sparePartApi, exportApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')

const formVisible = ref(false)
const formTitle = ref('新增备件')
const submitting = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  part_no: '',
  name: '',
  specification: '',
  supplier: '',
  unit: '个',
  storage_location: '',
  unit_price: 0,
  remark: ''
})

const rules = {
  part_no: [{ required: true, message: '请输入备件编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入备件名称', trigger: 'blur' }]
}

const stockVisible = ref(false)
const stockTitle = ref('入库')
const stockType = ref('in')
const stocking = ref(false)
const stockFormRef = ref()
const currentPart = ref(null)
const stockForm = reactive({
  quantity: 1,
  related_order_no: '',
  remark: ''
})

const stockRules = {
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await sparePartApi.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const loadLowStock = async () => {
  loading.value = true
  try {
    const res = await sparePartApi.lowStock()
    tableData.value = res || []
    total.value = tableData.value.length
    ElMessage.warning(`有 ${tableData.value.length} 种备件库存不足`)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleAdd = () => {
  formTitle.value = '新增备件'
  Object.assign(form, { id: null, part_no: '', name: '', specification: '', supplier: '', unit: '个', storage_location: '', unit_price: 0, remark: '' })
  formVisible.value = true
}

const handleEdit = (row) => {
  formTitle.value = '编辑备件'
  Object.assign(form, row)
  formVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (form.id) {
      await sparePartApi.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await sparePartApi.create(form)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || '操作失败') }
  finally { submitting.value = false }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该备件？', '提示', { type: 'warning' })
  try {
    await sparePartApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { ElMessage.error('删除失败') }
}

const handleStockIn = (row) => {
  stockType.value = 'in'
  stockTitle.value = '入库'
  currentPart.value = row
  Object.assign(stockForm, { quantity: 1, related_order_no: '', remark: '' })
  stockVisible.value = true
}

const handleStockOut = (row) => {
  stockType.value = 'out'
  stockTitle.value = '出库'
  currentPart.value = row
  Object.assign(stockForm, { quantity: 1, related_order_no: '', remark: '' })
  stockVisible.value = true
}

const submitStock = async () => {
  await stockFormRef.value.validate()
  stocking.value = true
  try {
    const data = { quantity: stockForm.quantity, related_order_no: stockForm.related_order_no, remark: stockForm.remark, operator: '管理员' }
    if (stockType.value === 'in') {
      await sparePartApi.stockIn(currentPart.value.id, data)
      ElMessage.success('入库成功')
    } else {
      await sparePartApi.stockOut(currentPart.value.id, data)
      ElMessage.success('出库成功')
    }
    stockVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || '操作失败') }
  finally { stocking.value = false }
}

const handleExport = async () => {
  try {
    const response = await exportApi.sparePartsExcel()
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '备件库存.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) { ElMessage.error('导出失败') }
}
</script>

<style scoped lang="scss">
.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
</style>
