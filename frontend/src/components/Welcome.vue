<template>
  <div class="card welcome-card">
    <h1>Welcome!</h1>
    <p>You are logged in as <strong>{{ email }}</strong></p>
    <p>The first 15 characters of your JWT are:</p>
    <code class="jwt-preview">{{ token }}</code>
  </div>
</template>

<script setup>
defineProps({
  email: {
    type: String,
    required: true
  },
  token: {
    type: String,
    required: true
  }
})
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

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.jwt-preview {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #eee;
  border-radius: 6px;
  font-family: monospace;
  color: #333;
}
</style>
