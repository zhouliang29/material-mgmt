import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMe, login as loginApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  async function login(username, password) {
    const res = await loginApi({ username, password })
    token.value = res.access_token
    userInfo.value = res.user
    localStorage.setItem('token', res.access_token)
    return res
  }

  async function fetchUserInfo() {
    try {
      const res = await getMe()
      userInfo.value = res
      return res
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return { token, userInfo, login, fetchUserInfo, logout }
})
