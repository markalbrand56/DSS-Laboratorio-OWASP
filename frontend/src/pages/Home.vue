<template>
  <div class="home-page">
    <nav class="navbar">
      <span class="logo">Laboratorio 4</span>
      <button @click="logout">Logout</button>
    </nav>

    <main>
      <!-- Card Welcome -->
      <Welcome :email="email" :token="token" />

      <!-- Grouped Cards (Generate Keys, Upload, Download, Validate, Files) -->
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
          <label>
            <input type="checkbox" v-model="signed" /> Sign the file
          </label>
          <input type="text" v-model="method" placeholder="Method (optional)" />
          <input type="file" @change="handlePrivateKeyUpload" />
          <button @click="uploadFiles" :disabled="loadingUpload">
            {{ loadingUpload ? 'Uploading...' : 'Upload File' }}
          </button>
        </div>

        <!-- Card Download File -->
        <div class="card">
          <h2>Download File</h2>
          <input v-model="fileEmailToDownload" type="text" placeholder="Enter email" />
          <input v-model="fileIdToDownload" type="text" placeholder="Enter file ID" />
          <button @click="downloadFiles">Download File</button>
        </div>

        <!-- Card Verificar Firma -->
        <div class="card">
          <h2>Verificar Firma de Archivo</h2>
          <input type="file" @change="handleFileVerification" />
          <input v-model="verificationEmail" type="email" placeholder="Correo del propietario" />
          <input v-model="publicKey" type="text" placeholder="Clave pública" />
          <select v-model="algorithm">
            <option value="rsa">RSA</option>
            <option value="ecc">ECC</option>
          </select>
          <button @click="verifySignature" :disabled="loadingVerification">
            {{ loadingVerification ? 'Verificando...' : 'Verificar Firma' }}
          </button>
          <p v-if="errorVerification" class="error">{{ errorVerification }}</p>
          <p v-if="successVerification" class="success">{{ successVerification }}</p>
        </div>

        <!-- Card List User Files -->
        <div class="card">
          <h2>All Files</h2>
          <div v-if="userFiles.length">
            <ul>
              <li v-for="(userFilesList, index) in userFiles" :key="index">
                <strong>User: {{ userFilesList.user }}</strong>
                <ul>
                  <li v-for="file in userFilesList.files" :key="file">
                    {{ file }}
                  </li>
                </ul>
              </li>
            </ul>
          </div>
          <div v-else>
            <p>No files available.</p>
          </div>
        </div>
      </div>


      <!-- Card File Metadata -->
      <div class="card" v-if="fileMetadata">
        <h2>File Metadata</h2>
        <p><strong>Methods of Signature:</strong> {{ fileMetadata.metodos_firma.join(', ') }}</p>
        <div v-if="fileMetadata.llaves_publicas">
          <div v-for="(key, method) in fileMetadata.llaves_publicas" :key="method">
            <h3>{{ method.toUpperCase() }} Public Key</h3>
            <pre>{{ key }}</pre>
            <button @click="downloadPublicKey(key, method)">Download Public Key</button>
          </div>
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
import {
  uploadFile,
  downloadFile,
  verifyFileSignature,
  getUserFiles,
  getFileMetadata,
} from '../api/files'
import { generateKeys } from '../api/auth'
import Welcome from "../components/Welcome.vue";

const router = useRouter() // Manejo de rutas
const email = ref('') // Email del usuario guardado en el sessionStorage
const token = ref('') // Token JWT del usuario guardado en el sessionStorage

const fileToUpload = ref(null) // Archivo a subir
const fileIdToDownload = ref('') // ID del archivo a descargar
const fileEmailToDownload = ref('') // Email del usuario que subió el archivo
const fileIdToValidate = ref('') // ID del archivo a validar
const userFiles = ref([]) // Lista de archivos del usuario
const fileMetadata = ref(null) // Metadata del archivo (método de firma y clave pública)

const signed = ref(false)
const method = ref('')
const privateKey = ref('')

const loading = ref(false) // Estado de carga para la generación de llaves
const loadingUpload = ref(false) // Estado de carga para la subida de archivos
const error = ref(null) // Mensaje de error
const success = ref(false) // Mensaje de éxito

// src/components/Home.vue
const verificationEmail = ref('') // Email del propietario
const publicKey = ref('') // Clave pública proporcionada por el usuario
const algorithm = ref('rsa') // Algoritmo seleccionado (RSA o ECC)
const fileVerification = ref(null) // Archivo a verificar

const loadingVerification = ref(false) // Estado de carga para la verificación de la firma
const errorVerification = ref(null) // Mensaje de error en la verificación de la firma
const successVerification = ref('') // Mensaje de éxito en la verificación

onMounted(() => {
  // Verificamos si el usuario está autenticado
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

// Función para cerrar sesión
const logout = () => {
  // Limpiamos el sessionStorage y redirigimos al login
  sessionStorage.clear()
  router.push('/login')
}

// Función para manejar el archivo a verificar
const handleFileVerification = (event) => {
  fileVerification.value = event.target.files[0]
}

// Función para verificar la firma del archivo
const verifySignature = async () => {
  if (!fileVerification.value || !publicKey.value || !verificationEmail.value) {
    errorVerification.value = 'Please provide all required fields (file, public key, and email).';
    return;
  }

  loadingVerification.value = true
  errorVerification.value = null
  successVerification.value = ''

  try {
    const response = await verifyFileSignature(fileVerification.value, verificationEmail.value, publicKey.value, algorithm.value);
    successVerification.value = response.message; // Mostrar el mensaje de éxito de la respuesta
  } catch (err) {
    errorVerification.value = err.message; // Mostrar el mensaje de error si la verificación falla
  } finally {
    loadingVerification.value = false
  }
}

// Función para obtener metadatos del archivo
const fetchFileMetadata = async (filename) => {
  try {
    fileMetadata.value = await getFileMetadata(fileEmailToDownload.value, filename)
  } catch (err) {
    error.value = err.message
  }
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

const privateKeyFile = ref(null);

// Función para manejar la carga de la clave privada
const handlePrivateKeyUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      privateKey.value = e.target.result; // Asigna el contenido del archivo al modelo `privateKey`
    };
    reader.readAsText(file);
  }
};


// Función para manejar el archivo subido
const handleFileUpload = (event) => {
  fileToUpload.value = event.target.files[0]
}

// Función para subir el archivo
const uploadFiles = async () => {
  if (!fileToUpload.value) {
    error.value = 'Please select a file to upload.';
    return;
  }

  loadingUpload.value = true;
  error.value = null;
  success.value = false;

  try {
    await uploadFile(fileToUpload.value, signed.value, method.value, privateKey.value);
    success.value = 'File uploaded successfully!';
    // Limpiar campos después de la subida
    fileToUpload.value = null;
    privateKey.value = '';
    signed.value = false;
    method.value = '';
    // Actualizar lista de archivos después de subir uno
    await fetchUserFiles();
  } catch (err) {
    error.value = err.message;
  } finally {
    loadingUpload.value = false
  }
}

// Función para descargar el archivo
const downloadFiles = async () => {
  if (!fileIdToDownload.value) return

  try {
    await downloadFile(fileEmailToDownload.value, fileIdToDownload.value)
    // Metadata del archivo
    await fetchFileMetadata(fileIdToDownload.value)

    success.value = true
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

// Función para obtener los archivos del usuario
const fetchUserFiles = async () => {
  try {
    const listFiles = await getUserFiles() // Esta función debe devolver todos los archivos de todos los usuarios
    console.log('listFiles', listFiles)
    userFiles.value = listFiles // Ya no filtramos solo por el email, ahora mostramos todos los archivos
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

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
