<template>
  <div class="page">
    <div class="page-header"><h2>数据导出</h2></div>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>报修工单导出</span>
            </div>
          </template>
          
          <el-form :model="repairExportForm" label-width="100px">
            <el-form-item label="状态筛选">
              <el-select v-model="repairExportForm.status" placeholder="全部状态" clearable style="width: 100%;">
                <el-option label="待接单" value="WAITING" />
                <el-option label="维修中" value="IN_PROGRESS" />
                <el-option label="待审核" value="PENDING_ADMIN_CLOSE" />
                <el-option label="已完成" value="CLOSED" />
                <el-option label="已取消" value="REJECTED" />
              </el-select>
            </el-form-item>
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="repairExportForm.start_date"
                type="date"
                placeholder="选择开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="repairExportForm.end_date"
                type="date"
                placeholder="选择结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="exportRepairExcel" :loading="exporting.excel">
                <el-icon><Download /></el-icon> 导出Excel
              </el-button>
              <el-button type="success" @click="exportRepairPdf" :loading="exporting.pdf">
                <el-icon><Download /></el-icon> 导出PDF
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>备件库存导出</span>
            </div>
          </template>
          
          <el-form label-width="100px">
            <el-form-item label="导出说明">
              <p style="color: #666; margin: 0;">
                导出所有备件的库存信息，包括备件编号、名称、规格、库存数量、安全库存、单价等。
              </p>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="exportSparePartsExcel" :loading="exporting.spareParts">
                <el-icon><Download /></el-icon> 导出Excel
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>导出说明</span>
        </div>
      </template>
      
      <el-alert title="Excel格式" type="info" :closable="false" style="margin-bottom: 15px;">
        <template #default>
          Excel格式适合数据分析和二次编辑，包含完整的数据表格，支持筛选、排序等操作。
        </template>
      </el-alert>
      
      <el-alert title="PDF格式" type="info" :closable="false">
        <template #default>
          PDF格式适合打印和存档，格式固定，适合生成报表和汇报材料。
        </template>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { exportApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

const repairExportForm = reactive({
  status: '',
  start_date: '',
  end_date: ''
})

const exporting = reactive({
  excel: false,
  pdf: false,
  spareParts: false
})

const downloadFile = (response, filename) => {
  const url = window.URL.createObjectURL(new Blob([response]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

const exportRepairExcel = async () => {
  exporting.excel = true
  try {
    const params = {}
    if (repairExportForm.status) params.status = repairExportForm.status
    if (repairExportForm.start_date) params.start_date = repairExportForm.start_date
    if (repairExportForm.end_date) params.end_date = repairExportForm.end_date
    
    const response = await exportApi.repairOrdersExcel(params)
    downloadFile(response, '报修工单.xlsx')
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.excel = false
  }
}

const exportRepairPdf = async () => {
  exporting.pdf = true
  try {
    const params = {}
    if (repairExportForm.status) params.status = repairExportForm.status
    if (repairExportForm.start_date) params.start_date = repairExportForm.start_date
    if (repairExportForm.end_date) params.end_date = repairExportForm.end_date
    
    const response = await exportApi.repairOrdersPdf(params)
    downloadFile(response, '报修工单.pdf')
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.pdf = false
  }
}

const exportSparePartsExcel = async () => {
  exporting.spareParts = true
  try {
    const response = await exportApi.sparePartsExcel()
    downloadFile(response, '备件库存.xlsx')
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.spareParts = false
  }
}
</script>

<style scoped lang="scss">
.card-header {
  font-weight: 500;
}
</style>
