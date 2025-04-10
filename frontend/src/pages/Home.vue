<template>
  <div class="home-page">
    <nav class="navbar">
      <span class="logo">Laboratorio 4</span>
      <button @click="logout">Logout</button>
    </nav>

    <main>
      <!-- Card Welcome -->
      <div class="card welcome-card">
        <h1>Welcome!</h1>
        <p>You are logged in as <strong>{{ email }}</strong></p>
        <p>The first 15 characters of your JWT are:</p>
        <code class="jwt-preview">{{ token }}</code>
      </div>

      <!-- Grouped Cards (Generate Keys, Upload, Download, Validate) -->
      <div class="card-group">
        <!-- Card Generate Keys -->
        <div class="card">
          <h2>Generate Keys</h2>
          <button @click="generateNewKeys" :disabled="loading">
            {{ loading ? 'Generating keys...' : 'Generate Keys' }}
          </button>
        </div>

        <!-- Card Upload File -->
        <div class="card">
          <h2>Upload File</h2>
          <input type="file" @change="handleFileUpload" />
          <button @click="uploadFiles" :disabled="loadingUpload">
            {{ loadingUpload ? 'Uploading...' : 'Upload File' }}
          </button>
        </div>

        <!-- Card Download File -->
        <div class="card">
          <h2>Download File</h2>
          <input v-model="fileIdToDownload" type="text" placeholder="Enter file ID" />
          <button @click="downloadFiles">Download File</button>
        </div>

        <!-- Card Validate Signature -->
        <div class="card">
          <h2>Validate File Signature</h2>
          <input v-model="fileIdToValidate" type="text" placeholder="Enter file ID" />
          <button @click="validateSignature">Validate Signature</button>
        </div>
      </div>

      <!-- Error and Success Messages -->
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">Operation completed successfully!</p>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadFile, downloadFile, validateFileSignature } from '../api/files'
import { generateKeys } from '../api/auth'

const router = useRouter() // Manejo de rutas
const email = ref('') // Email del usuario guardado en el sessionStorage
const token = ref('') // Token JWT del usuario guardado en el sessionStorage
const fileToUpload = ref(null) // Archivo a subir
const fileIdToDownload = ref('') // ID del archivo a descargar
const fileIdToValidate = ref('') // ID del archivo a validar
const loading = ref(false) // Estado de carga para la generación de llaves
const loadingUpload = ref(false) // Estado de carga para la subida de archivos
const error = ref(null) // Mensaje de error
const success = ref(false) // Mensaje de éxito

onMounted(() => {
  // Verificamos si el usuario está autenticado
  const storedToken = sessionStorage.getItem('jwt_token')
  const storedEmail = sessionStorage.getItem('email')

  if (!storedToken || !storedEmail) {
    router.push('/login')
  } else {
    email.value = storedEmail
    token.value = storedToken.slice(0, 15)
  }
})

// Función para cerrar sesión
const logout = () => {
  // Limpiamos el sessionStorage y redirigimos al login
  sessionStorage.clear()
  router.push('/login')
}

// Función para descargar los archivos de llaves
const downloadKey = (content, filename) => {
  const blob = new Blob([content], { type: 'application/octet-stream' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
}

// Función para generar nuevas llaves
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
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 85%;
  max-width: 500px;
  margin: 2rem 1rem;
  text-align: center;
}

.card h2 {
  margin-bottom: 1rem;
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

button {
  background: #3f51b5;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 1rem;
}

button:hover {
  background: #303f9f;
}

.error {
  color: red;
  margin-top: 1rem;
}

.success {
  color: green;
  margin-top: 1rem;
}

/* Styles for the card group (grid layout) */
.card-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 1rem;
  width: 100%;
  max-width: 1100px;
  margin: 1rem;
}
</style>
