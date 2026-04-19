import { ref, computed } from 'vue'

const STORAGE_KEY_NAME = import.meta.env.VITE_STORAGE_KEY_USER_NAME || 'user_name'
const STORAGE_KEY_ID = import.meta.env.VITE_STORAGE_KEY_USER_ID || 'user_id'

const name = ref<string>(localStorage.getItem(STORAGE_KEY_NAME) || '')
const userId = ref<number | null>(
  localStorage.getItem(STORAGE_KEY_ID)
    ? Number(localStorage.getItem(STORAGE_KEY_ID))
    : null
)

export function useUser() {
  function setName(n: string) {
    name.value = n
    localStorage.setItem(STORAGE_KEY_NAME, n)
  }

  function setUserId(id: number) {
    userId.value = id
    localStorage.setItem(STORAGE_KEY_ID, String(id))
  }

  function clear() {
    name.value = ''
    userId.value = null
    localStorage.removeItem(STORAGE_KEY_NAME)
    localStorage.removeItem(STORAGE_KEY_ID)
  }

  return {
    name,
    userId: computed(() => userId.value),
    setName,
    setUserId,
    clear,
  }
}