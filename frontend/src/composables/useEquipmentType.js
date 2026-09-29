import { equipmentApi } from '@/api'
import { ref } from 'vue'

const equipmentTypes = ref([])
const loading = ref(false)
let loaded = false

export function useEquipmentType() {
  const loadEquipmentTypes = async (forceRefresh = false) => {
    if (loaded && !forceRefresh && equipmentTypes.value.length > 0) {
      return equipmentTypes.value
    }
    
    loading.value = true
    try {
      const res = await equipmentApi.typeList({ page_size: 100 })
      equipmentTypes.value = res.results || []
      loaded = true
      return equipmentTypes.value
    } catch (error) {
      console.error('加载设备类型失败:', error)
      return []
    } finally {
      loading.value = false
    }
  }
  
  const getTypeName = (typeId) => {
    if (!typeId) return '-'
    const type = equipmentTypes.value.find(t => t.id === typeId)
    return type?.type_name || '-'
  }
  
  const getTypeById = (typeId) => {
    if (!typeId) return null
    return equipmentTypes.value.find(t => t.id === typeId)
  }
  
  const refreshTypes = () => {
    return loadEquipmentTypes(true)
  }
  
  return {
    equipmentTypes,
    loading,
    loadEquipmentTypes,
    getTypeName,
    getTypeById,
    refreshTypes
  }
}
