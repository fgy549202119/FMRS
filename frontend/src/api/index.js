/**
 * API接口定义文件
 * 
 * 该文件集中定义了前端与后端交互的所有API接口。
 * 采用模块化组织，按业务功能分组，便于维护和调用。
 * 
 * 模块结构：
 * - userApi：用户管理相关接口
 * - staffApi：维修人员相关接口
 * - adminApi：管理员相关接口
 * - equipmentApi：设备管理相关接口
 * - repairApi：报修管理相关接口
 * - evaluationApi：评价管理相关接口
 * - appealApi：评价申诉相关接口
 * - announcementApi：公告管理相关接口
 * - inspectionApi：巡检管理相关接口
 * - sparePartApi：备件管理相关接口
 * - knowledgeApi：知识库相关接口
 * - repairLogApi：维修日志相关接口
 * - exportApi：数据导出相关接口
 * - locationApi：位置管理相关接口
 * - statsApi：统计数据相关接口
 * 
 * 使用方式：
 * import { userApi, repairApi } from '@/api'
 * const res = await userApi.login({ username, password })
 * 
 * 作者：FMRS开发团队
 * 创建日期：2024年
 */

// 导入封装好的请求工具
import request from '@/utils/request'

/**
 * 用户管理API
 * 
 * 提供普通用户的登录、注册、信息管理等功能。
 */
export const userApi = {
  /**
   * 用户登录
   * @param {Object} data - 登录数据 { username, password }
   * @returns {Promise} 登录结果
   */
  login: (data) => request.post('/user/users/login/', data),
  
  /**
   * 用户登出
   * @returns {Promise} 登出结果
   */
  logout: () => request.post('/user/users/logout/'),
  
  /**
   * 用户注册
   * @param {Object} data - 注册数据
   * @returns {Promise} 注册结果
   */
  register: (data) => request.post('/user/users/', data),
  
  /**
   * 获取当前用户信息
   * @returns {Promise} 用户信息
   */
  profile: () => request.get('/user/users/profile/'),
  
  /**
   * 修改密码
   * @param {Object} data - { old_password, new_password }
   * @returns {Promise} 修改结果
   */
  changePassword: (data) => request.post('/user/users/change_password/', data),
  
  /**
   * 获取用户列表（管理员使用）
   * @param {Object} params - 查询参数
   * @returns {Promise} 用户列表
   */
  list: (params) => request.get('/user/users/', { params }),
  
  /**
   * 获取单个用户详情
   * @param {number} id - 用户ID
   * @returns {Promise} 用户详情
   */
  get: (id) => request.get(`/user/users/${id}/`),
  
  /**
   * 更新用户信息
   * @param {number} id - 用户ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  update: (id, data) => request.patch(`/user/users/${id}/`, data),
  
  /**
   * 删除用户
   * @param {number} id - 用户ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/user/users/${id}/`),
  
  /**
   * 账号注销
   * @param {Object} data - { password }
   * @returns {Promise} 注销结果
   */
  deleteAccount: (data) => request.post('/user/users/delete_account/', data),
  
  /**
   * 批量删除用户
   * @param {Array} ids - 用户ID数组
   * @returns {Promise} 删除结果
   */
  batchDelete: (ids) => request.post('/user/users/batch_delete/', { ids })
}

/**
 * 维修人员API
 * 
 * 提供维修人员的登录、状态管理等功能。
 */
export const staffApi = {
  /**
   * 维修人员登录
   * @param {Object} data - { staff_no, password }
   * @returns {Promise} 登录结果
   */
  login: (data) => request.post('/user/staff/login/', data),
  
  logout: () => request.post('/user/staff/logout/'),
  
  /**
   * 创建维修人员
   * @param {Object} data - 维修人员数据
   * @returns {Promise} 创建结果
   */
  register: (data) => request.post('/user/staff/', data),
  
  /**
   * 获取维修人员列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 维修人员列表
   */
  list: (params) => request.get('/user/staff/', { params }),
  
  /**
   * 获取单个维修人员详情
   * @param {number} id - 维修人员ID
   * @returns {Promise} 维修人员详情
   */
  get: (id) => request.get(`/user/staff/${id}/`),
  
  /**
   * 更新维修人员信息
   * @param {number} id - 维修人员ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  update: (id, data) => request.patch(`/user/staff/${id}/`, data),
  
  /**
   * 删除维修人员
   * @param {number} id - 维修人员ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/user/staff/${id}/`),
  
  /**
   * 设置维修人员状态
   * @param {Object} data - { staff_id, status }
   * @returns {Promise} 设置结果
   */
  setStatus: (data) => request.post('/repair/staff-online/set_status/', data),
  
  /**
   * 发送心跳（保持在线状态）
   * @param {Object} data - { staff_id }
   * @returns {Promise} 心跳结果
   */
  heartbeat: (data) => request.post('/repair/staff-online/heartbeat/', data),
  
  /**
   * 维修人员登出
   * @returns {Promise} 登出结果
   */
  onlineLogout: () => request.post('/repair/staff-online/logout/')
}

/**
 * 管理员API
 * 
 * 提供管理员的登录功能。
 */
export const adminApi = {
  login: (data) => request.post('/user/admin/login/', data),
  logout: () => request.post('/user/admin/logout/'),
  profile: (id) => request.get(`/user/admin/${id}/`),
  update: (id, data) => request.patch(`/user/admin/${id}/`, data),
  changePassword: (id, data) => request.patch(`/user/admin/${id}/`, data)
}

/**
 * 设备管理API
 * 
 * 提供设备类型和设备的管理功能。
 */
export const equipmentApi = {
  // ========== 设备类型相关 ==========
  
  /**
   * 获取设备类型列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 设备类型列表
   */
  typeList: (params) => request.get('/equipment/types/', { params }),
  
  /**
   * 创建设备类型
   * @param {Object} data - 设备类型数据
   * @returns {Promise} 创建结果
   */
  typeCreate: (data) => request.post('/equipment/types/', data),
  
  /**
   * 更新设备类型
   * @param {number} id - 设备类型ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  typeUpdate: (id, data) => request.put(`/equipment/types/${id}/`, data),
  
  /**
   * 删除设备类型
   * @param {number} id - 设备类型ID
   * @returns {Promise} 删除结果
   */
  typeDelete: (id) => request.delete(`/equipment/types/${id}/`),
  
  /**
   * 获取设备类型统计
   * @returns {Promise} 统计数据
   */
  typeStatistics: () => request.get('/equipment/types/statistics/'),
  
  /**
   * 获取启用的设备类型选项
   * @returns {Promise} 设备类型选项列表
   */
  typeOptions: () => request.get('/equipment/types/options/'),

  // ========== 设备相关 ==========
  
  /**
   * 获取设备列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 设备列表
   */
  list: (params) => request.get('/equipment/list/', { params }),
  distinctNames: (params) => request.get('/equipment/list/distinct_names/', { params }),
  byNameAndLocation: (params) => request.get('/equipment/list/by_name_and_location/', { params }),
  
  /**
   * 获取单个设备详情
   * @param {number} id - 设备ID
   * @returns {Promise} 设备详情
   */
  get: (id) => request.get(`/equipment/list/${id}/`),
  
  /**
   * 创建设备
   * @param {Object} data - 设备数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/equipment/list/', data),
  
  /**
   * 更新设备
   * @param {number} id - 设备ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  update: (id, data) => request.put(`/equipment/list/${id}/`, data),
  
  /**
   * 删除设备
   * @param {number} id - 设备ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/equipment/list/${id}/`),
  
  /**
   * 标记设备故障
   * @param {number} id - 设备ID
   * @param {Object} data - 故障信息
   * @returns {Promise} 标记结果
   */
  markFaulty: (id, data) => request.post(`/equipment/list/${id}/mark_faulty/`, data),
  
  /**
   * 标记设备正常
   * @param {number} id - 设备ID
   * @returns {Promise} 标记结果
   */
  markNormal: (id) => request.post(`/equipment/list/${id}/mark_normal/`),

  batchCreate: (data) => request.post('/equipment/list/batch_create/', data),
  batchDelete: (ids) => request.post('/equipment/list/batch_delete/', { ids }),
}

/**
 * 报修管理API
 * 
 * 提供报修工单的管理功能。
 */
export const repairApi = {
  /**
   * 获取工单列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 工单列表
   */
  orderList: (params) => request.get('/repair/orders/', { params }),
  
  /**
   * 获取单个工单详情
   * @param {number} id - 工单ID
   * @returns {Promise} 工单详情
   */
  orderGet: (id) => request.get(`/repair/orders/${id}/`),
  
  /**
   * 创建报修工单
   * @param {Object} data - 工单数据
   * @returns {Promise} 创建结果
   */
  orderCreate: (data) => request.post('/repair/orders/', data),
  
  /**
   * 接单
   * @param {number} id - 工单ID
   * @param {Object} data - 接单数据
   * @returns {Promise} 接单结果
   */
  orderAccept: (id, data) => request.post(`/repair/orders/${id}/accept/`, data),
  
  /**
   * 开始维修
   * @param {number} id - 工单ID
   * @returns {Promise} 操作结果
   */
  orderStartRepair: (id) => request.post(`/repair/orders/${id}/start_repair/`),
  
  /**
   * 转派工单
   * @param {number} id - 工单ID
   * @param {Object} data - 转派数据
   * @returns {Promise} 转派结果
   */
  orderTransfer: (id, data) => request.post(`/repair/orders/${id}/transfer/`, data),
  
  /**
   * 提交完成
   * @param {number} id - 工单ID
   * @param {Object} data - 完成数据
   * @returns {Promise} 提交结果
   */
  orderComplete: (id, data) => request.post(`/repair/orders/${id}/complete/`, data),
  
  /**
   * 审核工单
   * @param {number} id - 工单ID
   * @param {Object} data - 审核数据
   * @returns {Promise} 审核结果
   */
  orderReview: (id, data) => request.post(`/repair/orders/${id}/review/`, data),
  
  /**
   * 取消工单
   * @param {number} id - 工单ID
   * @returns {Promise} 取消结果
   */
  orderCancel: (id) => request.post(`/repair/orders/${id}/cancel/`),
  
  /**
   * 删除工单
   * @param {number} id - 工单ID
   * @returns {Promise} 删除结果
   */
  orderDelete: (id) => request.delete(`/repair/orders/${id}/`),
  
  /**
   * 获取工单统计
   * @returns {Promise} 统计数据
   */
  orderStatistics: (params) => request.get('/repair/orders/statistics/', { params }),
  
  /**
   * 获取待评价工单
   * @param {Object} params - 查询参数
   * @returns {Promise} 待评价工单列表
   */
  pendingEvaluation: (params) => request.get('/repair/orders/pending_evaluation/', { params }),
  
  /**
   * 检查重复报修
   * @param {Object} data - 检查数据
   * @returns {Promise} 检查结果
   */
  checkDuplicate: (data) => request.post('/repair/orders/check_duplicate/', data),

  /**
   * 获取维修记录列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 维修记录列表
   */
  recordList: (params) => request.get('/repair/records/', { params }),
  
  /**
   * 删除维修记录
   * @param {number} id - 记录ID
   * @returns {Promise} 删除结果
   */
  recordDelete: (id) => request.delete(`/repair/records/${id}/`),
  
  /**
   * 审核维修记录
   * @param {number} id - 记录ID
   * @param {Object} data - 审核数据
   * @returns {Promise} 审核结果
   */
  recordReview: (id, data) => request.post(`/repair/records/${id}/review/`, data),
  
  /**
   * 获取在线维修人员列表
   * @returns {Promise} 在线维修人员列表
   */
  onlineStaffList: () => request.get('/repair/orders/online-staff-list/')
}

/**
 * 评价管理API
 * 
 * 提供评价的管理和统计功能。
 */
export const evaluationApi = {
  /**
   * 获取评价列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 评价列表
   */
  list: (params) => request.get('/repair/evaluations/', { params }),
  
  /**
   * 创建评价
   * @param {Object} data - 评价数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/repair/evaluations/', data),
  
  /**
   * 获取单个评价详情
   * @param {number} id - 评价ID
   * @returns {Promise} 评价详情
   */
  get: (id) => request.get(`/repair/evaluations/${id}/`),
  
  /**
   * 更新评价
   * @param {number} id - 评价ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  update: (id, data) => request.put(`/repair/evaluations/${id}/`, data),
  
  /**
   * 删除评价
   * @param {number} id - 评价ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/repair/evaluations/${id}/`),
  
  /**
   * 获取评价统计
   * @param {Object} params - 查询参数
   * @returns {Promise} 统计数据
   */
  statistics: (params) => request.get('/repair/evaluations/statistics/', { params }),
  
  /**
   * 检查工单是否已评价
   * @param {string} orderIds - 工单ID列表（逗号分隔）
   * @returns {Promise} 已评价工单ID列表
   */
  checkEvaluated: (orderIds) => request.get('/repair/evaluations/check_evaluated/', { params: { order_ids: orderIds } }),
  
  /**
   * 获取维修人员评分排名
   * @returns {Promise} 排名列表
   */
  staffRanking: () => request.get('/repair/evaluations/staff_ranking/'),
  
  /**
   * 获取月度评价趋势
   * @returns {Promise} 趋势数据
   */
  monthlyTrend: () => request.get('/repair/evaluations/monthly_trend/'),
  
  /**
   * 获取评价维度分析
   * @returns {Promise} 维度分析数据
   */
  dimensionAnalysis: () => request.get('/repair/evaluations/dimension_analysis/'),
  
  /**
   * 获取差评列表
   * @returns {Promise} 差评列表
   */
  badReviews: () => request.get('/repair/evaluations/bad_reviews/'),
  
  /**
   * 隐藏评价
   * @param {number} id - 评价ID
   * @param {Object} data - 隐藏原因
   * @returns {Promise} 隐藏结果
   */
  hide: (id, data) => request.post(`/repair/evaluations/${id}/hide/`, data),
  
  /**
   * 显示评价
   * @param {number} id - 评价ID
   * @returns {Promise} 显示结果
   */
  show: (id) => request.post(`/repair/evaluations/${id}/show/`),
  
  /**
   * 管理员审核评价
   * @param {number} id - 评价ID
   * @param {Object} data - 审核数据
   * @returns {Promise} 审核结果
   */
  adminReview: (id, data) => request.post(`/repair/evaluations/${id}/admin_review/`, data)
}

/**
 * 评价申诉API
 * 
 * 提供评价申诉的管理功能。
 */
export const appealApi = {
  /**
   * 获取申诉列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 申诉列表
   */
  list: (params) => request.get('/repair/appeals/', { params }),
  
  /**
   * 创建申诉
   * @param {Object} data - 申诉数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/repair/appeals/', data),
  
  /**
   * 获取申诉详情
   * @param {number} id - 申诉ID
   * @returns {Promise} 申诉详情
   */
  get: (id) => request.get(`/repair/appeals/${id}/`),
  
  /**
   * 通过申诉
   * @param {number} id - 申诉ID
   * @param {Object} data - 处理数据
   * @returns {Promise} 处理结果
   */
  approve: (id, data) => request.post(`/repair/appeals/${id}/approve/`, data),
  
  /**
   * 驳回申诉
   * @param {number} id - 申诉ID
   * @param {Object} data - 处理数据
   * @returns {Promise} 处理结果
   */
  reject: (id, data) => request.post(`/repair/appeals/${id}/reject/`, data)
}

/**
 * 公告管理API
 * 
 * 提供公告的增删改查功能。
 */
export const announcementApi = {
  /**
   * 获取公告列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 公告列表
   */
  list: (params) => request.get('/announcement/list/', { params }),
  
  /**
   * 获取公告详情
   * @param {number} id - 公告ID
   * @returns {Promise} 公告详情
   */
  get: (id) => request.get(`/announcement/list/${id}/`),
  
  /**
   * 创建公告
   * @param {Object} data - 公告数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/announcement/list/', data),
  
  /**
   * 更新公告
   * @param {number} id - 公告ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  update: (id, data) => request.put(`/announcement/list/${id}/`, data),
  
  /**
   * 删除公告
   * @param {number} id - 公告ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/announcement/list/${id}/`)
}

/**
 * 巡检管理API
 * 
 * 提供巡检单的管理功能。
 */
export const inspectionApi = {
  /**
   * 获取巡检单列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 巡检单列表
   */
  list: (params) => request.get('/inspection/list/', { params }),
  
  /**
   * 获取巡检单详情
   * @param {number} id - 巡检单ID
   * @returns {Promise} 巡检单详情
   */
  get: (id) => request.get(`/inspection/list/${id}/`),
  
  /**
   * 创建巡检单
   * @param {Object} data - 巡检单数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/inspection/list/', data),
  
  /**
   * 审核巡检单
   * @param {number} id - 巡检单ID
   * @param {Object} data - 审核数据
   * @returns {Promise} 审核结果
   */
  review: (id, data) => request.post(`/inspection/list/${id}/review/`, data),
  
  /**
   * 删除巡检单
   * @param {number} id - 巡检单ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/inspection/list/${id}/`)
}

/**
 * 备件管理API
 * 
 * 提供备件的库存管理功能。
 */
export const sparePartApi = {
  /**
   * 获取备件列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 备件列表
   */
  list: (params) => request.get('/common/spare-parts/', { params }),
  
  /**
   * 获取备件详情
   * @param {number} id - 备件ID
   * @returns {Promise} 备件详情
   */
  get: (id) => request.get(`/common/spare-parts/${id}/`),
  
  /**
   * 创建备件
   * @param {Object} data - 备件数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/common/spare-parts/', data),
  
  /**
   * 更新备件
   * @param {number} id - 备件ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  update: (id, data) => request.put(`/common/spare-parts/${id}/`, data),
  
  /**
   * 删除备件
   * @param {number} id - 备件ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/common/spare-parts/${id}/`),
  
  /**
   * 获取库存不足的备件列表
   * @returns {Promise} 库存不足备件列表
   */
  lowStock: () => request.get('/common/spare-parts/low_stock/'),
  
  /**
   * 备件入库
   * @param {number} id - 备件ID
   * @param {Object} data - 入库数据
   * @returns {Promise} 入库结果
   */
  stockIn: (id, data) => request.post(`/common/spare-parts/${id}/stock_in/`, data),
  
  /**
   * 备件出库
   * @param {number} id - 备件ID
   * @param {Object} data - 出库数据
   * @returns {Promise} 出库结果
   */
  stockOut: (id, data) => request.post(`/common/spare-parts/${id}/stock_out/`, data),
  
  /**
   * 获取备件记录
   * @param {Object} params - 查询参数
   * @returns {Promise} 备件记录列表
   */
  records: (params) => request.get('/common/spare-part-records/', { params })
}

/**
 * 知识库API
 * 
 * 提供维修知识库的管理功能。
 */
export const knowledgeApi = {
  /**
   * 获取知识库列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 知识库列表
   */
  list: (params) => request.get('/common/knowledge/', { params }),
  
  /**
   * 获取知识库详情
   * @param {number} id - 知识ID
   * @returns {Promise} 知识详情
   */
  get: (id) => request.get(`/common/knowledge/${id}/`),
  
  /**
   * 创建知识条目
   * @param {Object} data - 知识数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/common/knowledge/', data),
  
  /**
   * 更新知识条目
   * @param {number} id - 知识ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  update: (id, data) => request.put(`/common/knowledge/${id}/`, data),
  
  /**
   * 删除知识条目
   * @param {number} id - 知识ID
   * @returns {Promise} 删除结果
   */
  delete: (id) => request.delete(`/common/knowledge/${id}/`),
  
  /**
   * 增加浏览次数
   * @param {number} id - 知识ID
   * @returns {Promise} 操作结果
   */
  view: (id) => request.post(`/common/knowledge/${id}/view/`),
  
  /**
   * 增加有用次数
   * @param {number} id - 知识ID
   * @returns {Promise} 操作结果
   */
  useful: (id) => request.post(`/common/knowledge/${id}/useful/`)
}

/**
 * 维修日志API
 * 
 * 提供维修日志的管理功能。
 */
export const repairLogApi = {
  /**
   * 获取维修日志列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 日志列表
   */
  list: (params) => request.get('/common/repair-logs/', { params }),
  
  /**
   * 创建维修日志
   * @param {Object} data - 日志数据
   * @returns {Promise} 创建结果
   */
  create: (data) => request.post('/common/repair-logs/', data)
}

/**
 * 数据导出API
 * 
 * 提供数据导出功能，支持Excel和PDF格式。
 */
export const exportApi = {
  /**
   * 导出报修工单Excel
   * @param {Object} params - 筛选参数
   * @returns {Promise} Excel文件Blob
   */
  repairOrdersExcel: (params) => request.get('/common/export/repair_orders_excel/', { params, responseType: 'blob' }),
  
  /**
   * 导出报修工单PDF
   * @param {Object} params - 筛选参数
   * @returns {Promise} PDF文件Blob
   */
  repairOrdersPdf: (params) => request.get('/common/export/repair_orders_pdf/', { params, responseType: 'blob' }),
  
  /**
   * 导出备件库存Excel
   * @param {Object} params - 筛选参数
   * @returns {Promise} Excel文件Blob
   */
  sparePartsExcel: (params) => request.get('/common/export/spare_parts_excel/', { params, responseType: 'blob' })
}

/**
 * 位置管理API
 * 
 * 提供校区、楼栋、楼层的管理功能。
 */
export const locationApi = {
  // 校区管理
  campus: {
    /**
     * 获取校区列表
     * @returns {Promise} 校区列表
     */
    list: () => request.get('/equipment/campus/'),
    
    /**
     * 获取校区详情
     * @param {number} id - 校区ID
     * @returns {Promise} 校区详情
     */
    get: (id) => request.get(`/equipment/campus/${id}/`),
    
    /**
     * 创建校区
     * @param {Object} data - 校区数据
     * @returns {Promise} 创建结果
     */
    create: (data) => request.post('/equipment/campus/', data),
    
    /**
     * 更新校区
     * @param {number} id - 校区ID
     * @param {Object} data - 更新数据
     * @returns {Promise} 更新结果
     */
    update: (id, data) => request.put(`/equipment/campus/${id}/`, data),
    
    /**
     * 删除校区
     * @param {number} id - 校区ID
     * @returns {Promise} 删除结果
     */
    delete: (id) => request.delete(`/equipment/campus/${id}/`)
  },
  
  // 楼栋管理
  building: {
    /**
     * 获取楼栋列表
     * @param {Object} params - 查询参数
     * @returns {Promise} 楼栋列表
     */
    list: (params) => request.get('/equipment/buildings/', { params }),
    
    /**
     * 获取所有楼栋（不分页）
     * @returns {Promise} 楼栋列表
     */
    listAll: () => request.get('/equipment/buildings/list_all/'),
    
    /**
     * 获取楼栋详情
     * @param {number} id - 楼栋ID
     * @returns {Promise} 楼栋详情
     */
    get: (id) => request.get(`/equipment/buildings/${id}/`),
    
    /**
     * 创建楼栋
     * @param {Object} data - 楼栋数据
     * @returns {Promise} 创建结果
     */
    create: (data) => request.post('/equipment/buildings/', data),
    
    /**
     * 更新楼栋
     * @param {number} id - 楼栋ID
     * @param {Object} data - 更新数据
     * @returns {Promise} 更新结果
     */
    update: (id, data) => request.put(`/equipment/buildings/${id}/`, data),
    
    /**
     * 删除楼栋
     * @param {number} id - 楼栋ID
     * @returns {Promise} 删除结果
     */
    delete: (id) => request.delete(`/equipment/buildings/${id}/`)
  },
  
  // 楼层管理
  floor: {
    /**
     * 获取楼层列表
     * @param {Object} params - 查询参数
     * @returns {Promise} 楼层列表
     */
    list: (params) => request.get('/equipment/floors/', { params }),
    
    /**
     * 获取所有楼层（不分页）
     * @returns {Promise} 楼层列表
     */
    listAll: () => request.get('/equipment/floors/list_all/'),
    
    /**
     * 获取楼层详情
     * @param {number} id - 楼层ID
     * @returns {Promise} 楼层详情
     */
    get: (id) => request.get(`/equipment/floors/${id}/`),
    
    /**
     * 创建楼层
     * @param {Object} data - 楼层数据
     * @returns {Promise} 创建结果
     */
    create: (data) => request.post('/equipment/floors/', data),
    
    /**
     * 更新楼层
     * @param {number} id - 楼层ID
     * @param {Object} data - 更新数据
     * @returns {Promise} 更新结果
     */
    update: (id, data) => request.put(`/equipment/floors/${id}/`, data),
    
    /**
     * 删除楼层
     * @param {number} id - 楼层ID
     * @returns {Promise} 删除结果
     */
    delete: (id) => request.delete(`/equipment/floors/${id}/`),
    
    /**
     * 按楼栋获取楼层
     * @param {number} buildingId - 楼栋ID
     * @returns {Promise} 楼层列表
     */
    byBuilding: (buildingId) => request.get(`/equipment/floors/by_building/${buildingId}/`),
    
    /**
     * 批量创建楼层
     * @param {Object} data - { building, start_floor, end_floor }
     * @returns {Promise} 创建结果
     */
    batchCreate: (data) => request.post('/equipment/floors/batch_create/', data)
  },

  room: {
    list: (params) => request.get('/location/rooms/', { params }),
    get: (id) => request.get(`/location/rooms/${id}/`),
    create: (data) => request.post('/location/rooms/', data),
    update: (id, data) => request.put(`/location/rooms/${id}/`, data),
    delete: (id) => request.delete(`/location/rooms/${id}/`),
    byFloor: (floorId) => request.get('/location/rooms/', { params: { floor_id: floorId } }),
    byBuilding: (buildingId) => request.get('/location/rooms/', { params: { building_id: buildingId } }),
    byCampus: (campusId) => request.get('/location/rooms/', { params: { campus_id: campusId } }),
    batchCreate: (data) => request.post('/location/rooms/batch_create/', data),
  }
}

/**
 * 统计数据API
 * 
 * 提供系统统计数据。
 */
export const statsApi = {
  /**
   * 获取系统概览统计
   * @returns {Promise} 统计数据
   */
  summary: () => request.get('/common/stats/summary/')
}

export const messageBoardApi = {
  list: (params) => request.get('/user/messages/', { params }),
  get: (id) => request.get(`/user/messages/${id}/`),
  create: (data) => request.post('/user/messages/', data),
  delete: (id) => request.delete(`/user/messages/${id}/`),
  adminList: (params) => request.get('/user/messages/', { params })
}

/**
 * 上传API
 * 
 * 提供文件上传功能。
 */
export const uploadApi = {
  /**
   * 上传文件
   * @param {FormData} formData - 表单数据，包含file文件和type类型
   * @returns {Promise} 上传结果
   */
  upload: (formData) => request.post('/api/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
