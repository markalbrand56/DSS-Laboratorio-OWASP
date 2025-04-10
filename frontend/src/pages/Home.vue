<template>
  <div class="home-page">
    <nav class="navbar">
      <span class="logo">MyApp</span>
      <button @click="logout">Logout</button>
    </nav>

    <main>
      <h1>Welcome!</h1>
      <p>You are logged in as <strong>{{ email }}</strong></p>
      <p>The first 15 characters of the JWT are {{ token }}</p>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const token = ref('')

onMounted(() => {
  const storedToken = sessionStorage.getItem('jwt_token')
  const storedEmail = sessionStorage.getItem('email')


  if (!token || !storedEmail) {
    router.push('/login')
  } else {
    email.value = storedEmail
    token.value = storedToken.slice(0, 15) // Get the first 15 characters of the JWT
  }
})

const logout = () => {
  sessionStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  padding: 1rem;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #333;
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 8px;
}

.navbar .logo {
  font-weight: bold;
}

.navbar button {
  background: #f44336;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.navbar button:hover {
  background: #d32f2f;
}

main {
  margin-top: 2rem;
  text-align: center;
}
</style>
