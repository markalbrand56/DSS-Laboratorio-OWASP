<template>
  <div class="home-page">
    <nav class="navbar">
      <span class="logo">Laboratorio 4</span>
      <button @click="logout">Logout</button>
    </nav>

    <main>
      <!-- Card Welcome -->
      <Welcome :email="email" :token="token" />

      <!-- Grouped Cards -->
      <div class="card-group">
        <GenerateKeys :loading="loading" @generate="generateNewKeys" />

        <FileUpload
            :loading="loadingUpload"
            @upload="({ file, signed: s, method: m, privateKey: k }) => {
            fileToUpload = file;
            signed = s;
            method = m;
            privateKey = k;
            uploadFiles();
          }"
        />

        <FileDownload :loading="loadingDownload" @download="downloadFiles" />

        <VerifySignature :loading="loadingVerify" @verify="verifySignature" />

        <AllFiles :files="userFiles" :loading="loadingFiles" @refresh="fetchUserFiles" />
      </div>

      <!-- Metadata -->
      <FileMetadata :metadata="fileMetadata" />

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">Operation completed successfully!</p>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  downloadFile,
  getFileMetadata,
  getUserFiles,
  uploadFile,
  verifyFileSignature
} from '../api/files'
import { generateKeys } from '../api/auth'

import Welcome from "../components/Welcome.vue";
import GenerateKeys from "../components/GenerateKeys.vue";
import FileUpload from "../components/FileUpload.vue";
import FileDownload from "../components/FileDownload.vue";
import VerifySignature from "../components/VerifySignature.vue";
import AllFiles from "../components/AllFiles.vue";
import FileMetadata from "../components/FileMetadata.vue";

// Router y usuario
const router = useRouter()
const email = ref('')
const token = ref('')

// Estados globales
const error = ref(null)
const success = ref(false)
const loading = ref(false)
const loadingUpload = ref(false)
const loadingDownload = ref(false)
const loadingVerify = ref(false)
const loadingFiles = ref(false)

// Archivos
let fileToUpload = null
let fileIdToDownload = ref('')
let fileEmailToDownload = ref('')
let signed = false
let method = ''
let privateKey = ''

const userFiles = ref([])
const fileMetadata = ref(null)

// Sesión
onMounted(() => {
  const storedToken = sessionStorage.getItem('jwt_token')
  const storedEmail = sessionStorage.getItem('email')

  if (!storedToken || !storedEmail) {
    router.push('/login')
  } else {
    email.value = storedEmail
    token.value = storedToken.slice(0, 15)
    fetchUserFiles()
  }
})

const logout = () => {
  sessionStorage.clear()
  router.push('/login')
}

// Generar nuevas llaves
const generateNewKeys = async () => {
  loading.value = true
  success.value = false
  error.value = null

  try {
    const res = await generateKeys()
    downloadKey(res.rsa_private_key, 'rsa_private_key.pem')
    downloadKey(res.ecc_private_key, 'ecc_private_key.pem')
    success.value = true
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Subir archivo
const uploadFiles = async () => {
  if (!fileToUpload) {
    error.value = 'Please select a file to upload.'
    return
  }

  loadingUpload.value = true
  error.value = null
  success.value = false

  try {
    await uploadFile(fileToUpload, signed, method, privateKey)
    success.value = 'File uploaded successfully!'
    fileToUpload = null
    signed = false
    method = ''
    privateKey = ''
    await fetchUserFiles()
  } catch (err) {
    error.value = err.message
  } finally {
    loadingUpload.value = false
  }
}

// Descargar archivo
const downloadFiles = async ({ email, fileId }) => {
  fileIdToDownload.value = fileId
  fileEmailToDownload.value = email

  loadingDownload.value = true
  error.value = null
  success.value = false

  try {
    await downloadFile(email, fileId)
    await fetchFileMetadata(fileId)
    success.value = true
  } catch (err) {
    error.value = err.message
  } finally {
    loadingDownload.value = false
  }
}

// Verificar firma
const verifySignature = async ({ file, email, publicKey: pubKey, algorithm }) => {
  if (!file || !email || !pubKey) {
    error.value = 'Please provide all required fields.'
    return
  }

  loadingVerify.value = true
  error.value = null
  success.value = false

  try {
    const res = await verifyFileSignature(file, email, pubKey, algorithm)
    success.value = res.message
  } catch (err) {
    error.value = err.message
  } finally {
    loadingVerify.value = false
  }
}

// Obtener metadata
const fetchFileMetadata = async (filename) => {
  try {
    fileMetadata.value = await getFileMetadata(fileEmailToDownload.value, filename)
  } catch (err) {
    error.value = err.message
  }
}

// Descargar clave
const downloadKey = (content, filename) => {
  const blob = new Blob([content], { type: 'application/octet-stream' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
}

// Obtener archivos del usuario
const fetchUserFiles = async () => {
  loadingFiles.value = true
  try {
    userFiles.value = await getUserFiles()
  } catch (err) {
    error.value = err.message
  } finally {
    loadingFiles.value = false
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

.card-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 1rem;
  width: 100%;
  max-width: 1100px;
  margin: 1rem;
}
</style>
