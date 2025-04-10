<!-- src/views/Register.vue -->
<template>
  <div class="register-page">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <div>
        <label>Email</label>
        <input v-model="email" type="email" required />
      </div>
      <div>
        <label>Password</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Registering...' : 'Register' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">Registration successful! Redirecting...</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/auth'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(false)

const handleRegister = async () => {
  loading.value = true
  error.value = null
  success.value = false
  try {
    await register(email.value, password.value)
    success.value = true
    setTimeout(() => router.push('/login'), 1500)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  max-width: 400px;
  margin: auto;
  padding: 2rem;
}
.error {
  color: red;
  margin-top: 1rem;
}
.success {
  color: green;
  margin-top: 1rem;
}
</style>
