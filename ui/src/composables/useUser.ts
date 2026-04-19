// ── useUser ──
// Singleton reactive user state backed by localStorage.

import { ref, computed } from 'vue'

const STORAGE_KEY_ID = 'user_id'
const STORAGE_KEY_NAME = 'user_name'

// Module-level refs — singleton across the app
const userId = ref<number | null>(
  localStorage.getItem(STORAGE_KEY_ID)
    ? Number(localStorage.getItem(STORAGE_KEY_ID))
    : null,
)
const userName = ref<string>(localStorage.getItem(STORAGE_KEY_NAME) ?? '')

export function useUser() {
  function setUser(id: number, name: string) {
    userId.value = id
    userName.value = name
    localStorage.setItem(STORAGE_KEY_ID, String(id))
    localStorage.setItem(STORAGE_KEY_NAME, name)
  }

  function clearUser() {
    userId.value = null
    userName.value = ''
    localStorage.removeItem(STORAGE_KEY_ID)
    localStorage.removeItem(STORAGE_KEY_NAME)
  }

  return {
    userId: computed(() => userId.value),
    userName: computed(() => userName.value),
    setUser,
    clearUser,
  }
}
