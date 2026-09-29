/**
 * 事件总线模块
 * 
 * 该模块实现了一个简单的事件总线（Event Bus），用于组件间的通信。
 * 在Vue 3中，由于移除了$on、$off、$once等实例方法，
 * 需要手动实现一个事件总线来支持跨组件通信。
 * 
 * 主要功能：
 * - EventBus.emit(event, data): 触发事件，向所有监听器发送数据
 * - EventBus.on(event, handler): 订阅事件，注册事件处理器
 * - EventBus.off(event, handler): 取消订阅，移除事件处理器
 * 
 * 使用场景：
 * - 跨组件通信（非父子关系）
 * - 全局状态更新通知
 * - 组件间的解耦通信
 * 
 * 使用示例：
 * // 组件A：订阅事件
 * import { EventBus, Events } from '@/utils/eventBus'
 * EventBus.on(Events.DATA_REFRESH, (data) => {
 *   console.log('收到数据刷新通知', data)
 * })
 * 
 * // 组件B：触发事件
 * EventBus.emit(Events.DATA_REFRESH, { type: 'order' })
 * 
 * 作者：FMRS开发团队
 * 创建日期：2024年
 */

// 导入Vue的ref响应式引用（当前未使用，保留备用）
import { ref } from 'vue'

/**
 * 事件处理器存储映射
 * 
 * 使用Map数据结构存储事件名称与处理器函数集合的映射关系。
 * - Key: 事件名称（字符串）
 * - Value: 处理器函数集合（Set）
 * 
 * 使用Set存储处理器的好处：
 * - 自动去重，同一处理器不会被重复添加
 * - 方便添加和删除处理器
 */
const eventHandlers = new Map()

/**
 * 事件总线对象
 * 
 * 提供事件的订阅、发布、取消订阅功能。
 */
export const EventBus = {
  /**
   * 触发事件
   * 
   * 向指定事件的所有监听器发送数据。
   * 
   * @param {string} event - 事件名称
   * @param {*} data - 要传递的数据，可以是任意类型
   * 
   * @example
   * EventBus.emit('user:login', { userId: 1, name: '张三' })
   */
  emit(event, data) {
    // 获取该事件的所有处理器
    const handlers = eventHandlers.get(event)
    
    // 如果存在处理器，遍历执行每个处理器函数
    if (handlers) {
      handlers.forEach(handler => handler(data))
    }
  },
  
  /**
   * 订阅事件
   * 
   * 为指定事件注册一个处理器函数。
   * 当事件被触发时，处理器函数会被调用。
   * 
   * @param {string} event - 事件名称
   * @param {Function} handler - 事件处理器函数
   * 
   * @example
   * EventBus.on('user:login', (data) => {
   *   console.log('用户登录:', data.name)
   * })
   */
  on(event, handler) {
    // 如果该事件还没有处理器集合，创建一个新的Set
    if (!eventHandlers.has(event)) {
      eventHandlers.set(event, new Set())
    }
    
    // 将处理器添加到集合中
    eventHandlers.get(event).add(handler)
  },
  
  /**
   * 取消订阅事件
   * 
   * 从指定事件的处理器集合中移除指定的处理器函数。
   * 
   * @param {string} event - 事件名称
   * @param {Function} handler - 要移除的事件处理器函数
   * 
   * @example
   * const handler = (data) => console.log(data)
   * EventBus.on('user:login', handler)
   * // 之后取消订阅
   * EventBus.off('user:login', handler)
   */
  off(event, handler) {
    // 获取该事件的处理器集合
    const handlers = eventHandlers.get(event)
    
    // 如果存在处理器集合，从中删除指定的处理器
    if (handlers) {
      handlers.delete(handler)
    }
  }
}

/**
 * 预定义事件常量
 * 
 * 定义系统中使用的所有事件名称常量，便于统一管理和避免拼写错误。
 * 使用命名空间格式（模块:动作）来组织事件名称。
 */
export const Events = {
  /**
   * 维修记录删除事件
   * 当维修记录被删除时触发
   */
  RECORD_DELETED: 'record:deleted',
  
  /**
   * 工单删除事件
   * 当报修工单被删除时触发
   */
  ORDER_DELETED: 'order:deleted',
  
  /**
   * 评价变更事件
   * 当评价信息发生变化时触发（新增、修改、删除）
   */
  EVALUATION_CHANGED: 'evaluation:changed',
  
  /**
   * 数据刷新事件
   * 当需要刷新列表数据时触发
   */
  DATA_REFRESH: 'data:refresh',
  
  /**
   * 设备类型变更事件
   * 当设备类型信息发生变化时触发
   */
  EQUIPMENT_TYPE_CHANGED: 'equipment_type:changed',
  
  /**
   * 设备变更事件
   * 当设备信息发生变化时触发
   */
  EQUIPMENT_CHANGED: 'equipment:changed'
}
