<template>
  <div class="register-page">
    <div class="card">
      <h2>Register</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>
            <input v-model="email" type="email" required />
            Email
          </label>
        </div>
        <div class="form-group">
          <label>
            <input v-model="password" type="password" required />
            Password
          </label>
        </div>
        <div class="form-group">
          <label>
            <input v-model="name" type="text" required @input="sanitizeName" />
            Name
          </label>
        </div>
        <div class="form-group">
          <label>
            <input v-model="surname" type="text" required @input="sanitizeSurname" />
            Surname
          </label>
        </div>
        <div class="form-group">
          <label>
            <input v-model="birthdate" type="date" required />
            Birthdate
          </label>
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
        <p v-if="error" class="error" v-html="encodedError"></p>
        <p v-if="success" class="success">¡Registro exitoso! Redirigiendo...</p>

        <p class="login-link">
          ¿Ya tienes una cuenta?
          <a @click.prevent="goToLogin" href="#">Inicia sesión aquí</a>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const success = ref(false)

// Form fields
const email = ref('')
const password = ref('')
const name = ref('')
const surname = ref('')
const birthdate = ref('')

// Regex: allow only letters, spaces, hyphens, apostrophes, and reject < >
const validNameRegex = /^[^<>]*$/

const sanitizeName = () => {
  if (!validNameRegex.test(name.value)) {
    name.value = name.value.replaceAll(/[<>]/g, '')
  }
}
const sanitizeSurname = () => {
  if (!validNameRegex.test(surname.value)) {
    surname.value = surname.value.replaceAll(/[<>]/g, '')
  }
}

// Output encoding for error messages (basic HTML escape)
function escapeHtml(str) {
  if (!str) return ''
  return str.replaceAll(/&/g, '&amp;')
            .replaceAll(/</g, '&lt;')
            .replaceAll(/>/g, '&gt;')
            .replaceAll(/"/g, '&quot;')
            .replaceAll(/'/g, '&#39;')
}

const encodedError = computed(() => escapeHtml(error.value))

const handleRegister = async () => {
  loading.value = true
  error.value = null
  success.value = false

  // Input validation before sending to backend
  if (!validNameRegex.test(name.value) || !validNameRegex.test(surname.value)) {
    error.value = 'Name and surname cannot contain < or > characters.'
    loading.value = false
    return
  }

  try {
    await register(email.value, password.value, name.value, surname.value, birthdate.value)
    success.value = true
    setTimeout(() => router.push('/login'), 1500)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 1rem;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: 500;
  color: #333;
}

.form-group {
  margin-bottom: 1.25rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #3f51b5;
  outline: none;
}

button {
  width: 100%;
  background-color: #3f51b5;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background-color: #303f9f;
}

button:disabled {
  background-color: #9fa8da;
  cursor: not-allowed;
}

.error {
  margin-top: 1rem;
  color: #d32f2f;
  text-align: center;
}

.success {
  margin-top: 1rem;
  color: green;
  text-align: center;
}

.login-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.login-link a {
  color: #3f51b5;
  font-weight: 500;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
