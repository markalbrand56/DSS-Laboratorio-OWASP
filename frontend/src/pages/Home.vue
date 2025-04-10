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

        <!-- Botón para generar llaves -->
        <div class="generate-keys">
          <button @click="generateNewKeys" :disabled="loading">
            {{ loading ? 'Generating keys...' : 'Generate Keys' }}
          </button>
        </div>

        <!-- Subir archivo -->
        <div class="upload-file">
          <h2>Upload File</h2>
          <input type="file" @change="handleFileUpload" />
          <button @click="uploadFiles" :disabled="loadingUpload">
            {{ loadingUpload ? 'Uploading...' : 'Upload File' }}
          </button>
        </div>

        <!-- Descargar archivo -->
        <div class="file-download">
          <h2>Download File</h2>
          <input v-model="fileIdToDownload" type="text" placeholder="Enter file ID" />
          <button @click="downloadFiles">Download File</button>
        </div>

        <!-- Validar firma -->
        <div class="file-validation">
          <h2>Validate File Signature</h2>
          <input v-model="fileIdToValidate" type="text" placeholder="Enter file ID" />
          <button @click="validateSignature">Validate Signature</button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">Operation completed successfully!</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadFile, downloadFile, validateFileSignature } from '../api/files'
import { generateKeys } from '../api/auth'

const router = useRouter()
const email = ref('')
const token = ref('')
const fileToUpload = ref(null)
const fileIdToDownload = ref('')
const fileIdToValidate = ref('')
const loading = ref(false)
const loadingUpload = ref(false)
const error = ref(null)
const success = ref(false)

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

const downloadKey = (content, filename) => {
  const blob = new Blob([content], { type: 'application/octet-stream' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
}

const generateNewKeys = async () => {
  loading.value = true
  success.value = false
  error.value = null

  try {
    const res = await generateKeys()
    // Descargamos las llaves privadas
    downloadKey(res.rsa_private_key, 'rsa_private_key.pem')
    downloadKey(res.ecc_private_key, 'ecc_private_key.pem')
    success.value = true
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Función para manejar el archivo subido
const handleFileUpload = (event) => {
  fileToUpload.value = event.target.files[0]
}

// Función para subir el archivo
const uploadFiles = async () => {
  if (!fileToUpload.value) return

  loadingUpload.value = true
  error.value = null
  success.value = false

  try {
    const response = await uploadFile(fileToUpload.value)
    success.value = true
  } catch (err) {
    error.value = err.message
  } finally {
    loadingUpload.value = false
  }
}

// Función para descargar el archivo
const downloadFiles = async () => {
  if (!fileIdToDownload.value) return

  try {
    await downloadFile(fileIdToDownload.value)
  } catch (err) {
    error.value = err.message
  }
}

// Función para validar la firma del archivo
const validateSignature = async () => {
  if (!fileIdToValidate.value) return

  try {
    await validateFileSignature(fileIdToValidate.value)
    success.value = true
  } catch (err) {
    error.value = err.message
  }
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
