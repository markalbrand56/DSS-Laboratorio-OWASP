<template>
  <div class="card">
    <h2>Upload File</h2>

    <div class="input-group">
      <label for="file">📄 Select File</label>
      <input id="file" type="file" @change="onFileChange" />
    </div>

    <div class="input-group">
      <label>
        <input type="checkbox" v-model="signed" /> Sign the file
      </label>
    </div>

    <div class="input-group">
      <label for="method">📝 Method (optional)</label>
      <input id="method" type="text" v-model="method" placeholder="Method" />
    </div>

    <div class="input-group">
      <label for="privateKey">🔑 Upload Private Key</label>
      <input id="privateKey" type="file" @change="onPrivateKeyUpload" />
    </div>

    <button
        class="upload-button"
        @click="onUpload"
        :disabled="loading || !file"
    >
      {{ loading ? 'Uploading...' : 'Upload File' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  loading: Boolean
})

const emit = defineEmits(['upload'])

const file = ref(null)
const privateKey = ref('')
const signed = ref(false)
const method = ref('')

const onFileChange = (e) => {
  file.value = e.target.files[0]
}

const onPrivateKeyUpload = (e) => {
  const fileInput = e.target.files[0]
  if (fileInput) {
    const reader = new FileReader()
    reader.onload = (event) => {
      privateKey.value = event.target.result
    }
    reader.readAsText(fileInput)
  }
}

const onUpload = () => {
  emit('upload', {
    file: file.value,
    signed: signed.value,
    method: method.value,
    privateKey: privateKey.value
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

input[type="file"], input[type="text"] {
  padding: 0.5rem;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
}

input[type="checkbox"] {
  margin-right: 0.5rem;
}

.upload-button {
  background: #3f51b5;
  color: white;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.upload-button:hover {
  background: #303f9f;
}

.upload-button:disabled {
  background: #aaa;
  cursor: not-allowed;
}
</style>
