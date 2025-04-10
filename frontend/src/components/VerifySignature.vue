<template>
  <div class="card">
    <h2>Verify Signature</h2>
    <p>Upload the file, public key, and signature to verify the authenticity.</p>

    <div class="input-group">
      <label for="file">📄 File</label>
      <input id="file" type="file" @change="onFileChange" />
    </div>

    <div class="input-group">
      <label for="publicKey">🔑 Public Key</label>
      <input id="publicKey" type="file" @change="onPublicKeyChange" />
    </div>

    <div class="input-group">
      <label for="signature">🖋️ Signature</label>
      <input id="signature" type="file" @change="onSignatureChange" />
    </div>

    <button
        class="verify-button"
        @click="onVerify"
        :disabled="loading || !file || !publicKey || !signature"
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
const signature = ref('')

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

const onSignatureChange = (e) => {
  const reader = new FileReader()
  reader.onload = (event) => {
    signature.value = event.target.result
  }
  reader.readAsText(e.target.files[0])
}

const onVerify = () => {
  emit('verify', {
    file: file.value,
    publicKey: publicKey.value,
    signature: signature.value
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

input[type="file"] {
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
