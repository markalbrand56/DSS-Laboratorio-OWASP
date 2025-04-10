<template>
  <div class="card">
    <h2>Generate Keys</h2>
    <button @click="onGenerateKeys" :disabled="loading">
      {{ loading ? 'Generating keys...' : 'Generate Keys' }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  loading: Boolean
})

const emit = defineEmits(['generate'])

const onGenerateKeys = () => {
  emit('generate')
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
  align-items: center;
  justify-content: center;
}
</style>
