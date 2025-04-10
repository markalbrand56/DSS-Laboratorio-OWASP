<template>
  <div class="card">
    <h2>Download File</h2>
    <input type="text" v-model="email" placeholder="Enter email" />
    <input type="text" v-model="filename" placeholder="Enter filename" />
    <button @click="onDownload" :disabled="loading || !filename">
      {{ loading ? 'Downloading...' : 'Download' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  loading: Boolean
})

const emit = defineEmits(['download'])

const filename = ref('')
const email = ref('')

const onDownload = () => {
  if (!filename.value) return
  emit('download', { email: email.value, fileId: filename.value });
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
