<template>
  <div class="card">
    <h2>Available Files</h2>

    <button @click="refresh" :disabled="loading">
      {{ loading ? 'Refreshing...' : 'Refresh List' }}
    </button>

    <div v-if="files.length > 0" class="users-list">
      <div v-for="(user, index) in files" :key="index" class="user-section">
        <h3 class="user-email">📧 {{ user.user }}</h3>
        <ul class="file-list">
          <li v-for="(file, idx) in user.files" :key="idx" class="file-item">
            📄 {{ file }}
          </li>
        </ul>
      </div>
    </div>

    <p v-else>No files found.</p>
  </div>
</template>

<script setup>
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
  max-width: 600px;
  text-align: center;

  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.users-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-section {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.user-email {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #3f51b5;
}

.file-list {
  list-style: none;
  padding-left: 1rem;
  margin: 0;
}

.file-item {
  padding: 0.3rem 0;
  border-bottom: 1px solid #e0e0e0;
  word-break: break-word;
}
</style>
