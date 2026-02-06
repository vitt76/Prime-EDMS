import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isRegistered: false,
    lastRegisterEmail: ''
  }),
  actions: {
    markRegistered(email: string) {
      this.isRegistered = true
      this.lastRegisterEmail = email
    }
  }
})
