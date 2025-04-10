<!-- src/App.vue -->
<template>
  <router-view />
  <footer>
    <p>&copy; 2025 Mark Albrand & Jose Santisteban</p>
  </footer>
</template>

<script setup>
</script>

<style>
body {
  margin: 0;
  display: flex;
  flex-direction: column; /* Asegura que los elementos se apilen verticalmente */
}

footer {
  margin-top: auto; /* Empuja el footer al final de la página */
  text-align: center;
  padding: 1rem;
  background-color: #3f51b5;
  color: white;
}
</style>