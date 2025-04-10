<template>
  <div class="card">
    <h2>Upload File</h2>
    <input type="file" @change="onFileChange" />
    <label>
      <input type="checkbox" v-model="signed" /> Sign the file
    </label>
    <input type="text" v-model="method" placeholder="Method (optional)" />
    <input type="file" @change="onPrivateKeyUpload" />
    <button @click="onUpload" :disabled="loading">
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

  // Reset form (opcional)
  // file.value = null
  // signed.value = false
  // method.value = ''
  // privateKey.value = ''
}
</script>

<style scoped>
.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 100%;
  text-align: center;

  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  justify-content: center;
}
</style>
