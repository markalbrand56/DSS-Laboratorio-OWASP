<!-- src/views/Login.vue -->
<template>
  <div class="login-page">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label>Email</label>
        <input v-model="email" type="email" required />
      </div>
      <div>
        <label>Password</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const handleLogin = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await login(email.value, password.value)
    sessionStorage.setItem('jwt_token', res.jwt_token)
    sessionStorage.setItem('email', res.email)
    router.push('/home')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  max-width: 400px;
  margin: auto;
  padding: 2rem;
}
.error {
  color: red;
  margin-top: 1rem;
}
</style>