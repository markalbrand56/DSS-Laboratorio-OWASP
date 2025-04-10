<template>
  <div class="home-page">
    <nav class="navbar">
      <span class="logo">MyApp</span>
      <button @click="logout">Logout</button>
    </nav>

    <main>
      <div class="card">
        <h1>Welcome!</h1>
        <p>You are logged in as <strong>{{ email }}</strong></p>
        <p>The first 15 characters of your JWT are:</p>
        <code class="jwt-preview">{{ token }}</code>
      </div>
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

  if (!storedToken || !storedEmail) {
    router.push('/login')
  } else {
    email.value = storedEmail
    token.value = storedToken.slice(0, 15)
  }
})

const logout = () => {
  sessionStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #3f51b5;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.logo {
  font-weight: 600;
  font-size: 1.2rem;
}

.navbar button {
  background: #f44336;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.navbar button:hover {
  background: #d32f2f;
}

main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.card {
  background: white;
  padding: 2rem 3rem;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  text-align: center;
}

h1 {
  margin-bottom: 1rem;
  color: #3f51b5;
}

.jwt-preview {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #eee;
  border-radius: 6px;
  font-family: monospace;
  color: #333;
}
</style>
