<template>
  <div class="login-page">
    <div class="card">
      <h2>Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input v-model="email" type="email" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required />
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <!-- Enlace para registrarse -->
      <p class="register-link">
        ¿No tienes una cuenta?
        <a @click.prevent="goToRegister" href="#">Regístrate aquí</a>
      </p>
    </div>
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
    // Si la API devuelve status
    if (err.status === 429) {
      error.value = 'Demasiados intentos fallidos. Intenta de nuevo más tarde.'
      alert(error.value)
    } else if (err.status === 401) {
      error.value = 'Credenciales inválidas.'
    } else {
      error.value = 'Error al iniciar sesión. Intenta nuevamente.'
    }
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
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

.register-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.register-link a {
  color: #3f51b5;
  font-weight: 500;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
