<!--
  根组件 - App.vue
  
  该组件是Vue应用的根组件，作为整个应用的容器。
  主要功能：
  - 提供路由视图出口（router-view）
  - 全局错误捕获和处理
  
  组件结构：
  - template：包含router-view，用于渲染当前路由匹配的组件
  - script：配置全局错误捕获
  - style：设置根元素样式
  
  作者：FMRS系统开发者-范广宇
  创建日期：2026年
-->

<template>
  <!-- 路由视图出口 -->
  <!-- 根据当前路由路径，渲染匹配的组件 -->
  <router-view />
</template>

<script setup>
/**
 * 组件脚本
 * 
 * 使用Vue 3的组合式API（Composition API）编写。
 * 主要配置全局错误捕获器。
 */
import { onErrorCaptured } from 'vue'

/**
 * 全局错误捕获器
 * 
 * 捕获组件生命周期钩子、事件处理器、侦听器等抛出的错误。
 * 
 * 参数说明：
 * @param {Error} err - 捕获的错误对象
 * @param {ComponentPublicInstance} instance - 触发错误的组件实例
 * @param {string} info - 错误来源信息（如生命周期钩子名称）
 * 
 * 返回值：
 * @returns {boolean} false - 阻止错误继续向上传播
 */
onErrorCaptured((err, instance, info) => {
  // 将错误信息输出到控制台，便于调试
  console.error('全局错误捕获:', err, info)
  
  // 返回false阻止错误继续向上传播
  // 如果返回true，错误会被继续传递给父组件的错误捕获器
  return false
})
</script>

<style>
/**
 * 根元素样式
 * 
 * 设置#app元素的宽高为100%，确保应用占满整个视口。
 */
#app {
  width: 100%;
  height: 100%;
}
</style>
