<template>
  <div class="card" v-if="metadata">
    <h2>File Metadata</h2>
    <p><strong>Methods of Signature:</strong> {{ metadata.metodos_firma.join(', ') }}</p>

    <div v-if="metadata.llaves_publicas">
      <div
          v-for="(key, method) in metadata.llaves_publicas"
          :key="method"
          class="key-section"
      >
        <h3>{{ method.toUpperCase() }} Public Key</h3>
        <pre>{{ key }}</pre>
        <button @click="downloadKey(key, `${method}_public_key.pem`)">
          Download Public Key
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  metadata: Object
})

const downloadKey = (content, filename) => {
  const blob = new Blob([content], { type: 'application/octet-stream' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
}
</script>

<style scoped>
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

.key-section {
  margin-top: 1rem;
  text-align: left;
}

pre {
  background: #f0f0f0;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}
</style>
