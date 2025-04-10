<template>
  <div class="card">
    <h2>Verify File Authenticity</h2>
    <p>Upload the file, public key, and provide your email to verify the authenticity of the file.</p>

    <div class="input-group">
      <label for="file">📄 File</label>
      <input id="file" type="file" @change="onFileChange" />
    </div>

    <div class="input-group">
      <label for="userEmail">📧 User Email</label>
      <input id="userEmail" type="email" v-model="userEmail" placeholder="Enter your email" />
    </div>

    <div class="input-group">
      <label for="publicKey">🔑 Public Key</label>
      <input id="publicKey" type="file" @change="onPublicKeyChange" />
    </div>

    <div class="input-group">
      <label for="algorithm">⚙️ Algorithm</label>
      <select id="algorithm" v-model="algorithm">
        <option value="rsa">RSA</option>
        <option value="ecc">ECC</option>
      </select>
    </div>

    <button
        class="verify-button"
        @click="onVerify"
        :disabled="loading || !file || !publicKey || !userEmail || !algorithm"
    >
      {{ loading ? 'Verifying...' : 'Verify Signature' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  loading: Boolean
})

const emit = defineEmits(['verify'])

const file = ref(null)
const publicKey = ref('')
const userEmail = ref('')
const algorithm = ref('rsa')

const onFileChange = (e) => {
  file.value = e.target.files[0]
}

const onPublicKeyChange = (e) => {
  const reader = new FileReader()
  reader.onload = (event) => {
    publicKey.value = event.target.result
  }
  reader.readAsText(e.target.files[0])
}

const onVerify = () => {
  emit('verify', {
    file: file.value,
    publicKey: publicKey.value,
    userEmail: userEmail.value,
    algorithm: algorithm.value
  })
}
</script>

<style scoped>
.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
}

.input-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

input[type="file"], input[type="email"], select {
  padding: 0.5rem;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.verify-button {
  background: #3f51b5;
  color: white;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.verify-button:hover {
  background: #303f9f;
}

.verify-button:disabled {
  background: #aaa;
  cursor: not-allowed;
}
</style>
