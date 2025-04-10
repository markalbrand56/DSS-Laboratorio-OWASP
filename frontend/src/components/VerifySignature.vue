<template>
  <div class="card">
    <h2>Verify Signature</h2>
    <input type="file" @change="onFileChange" />
    <input type="file" @change="onPublicKeyChange" />
    <input type="file" @change="onSignatureChange" />
    <button @click="onVerify" :disabled="loading || !file || !publicKey || !signature">
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
  text-align: center;

  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  justify-content: center;
}
</style>
