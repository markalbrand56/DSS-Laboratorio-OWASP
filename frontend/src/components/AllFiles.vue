<template>
  <div class="card">
    <h2>Available Files</h2>

    <button @click="refresh" :disabled="loading">
      {{ loading ? 'Refreshing...' : 'Refresh List' }}
    </button>

    <ul v-if="files.length > 0" class="file-list">
      <li v-for="(file, index) in files" :key="index">
        {{ file }}
      </li>
    </ul>

    <p v-else>No files found.</p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

defineProps({
  files: Array,
  loading: Boolean
})

const emit = defineEmits(['refresh'])

const refresh = () => {
  emit('refresh')
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

.file-list {
  list-style-type: none;
  padding: 0;
  margin-top: 1rem;
  max-height: 300px;
  overflow-y: auto;
  width: 100%;
  text-align: left;
}

.file-list li {
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
  word-break: break-word;
}
</style>
