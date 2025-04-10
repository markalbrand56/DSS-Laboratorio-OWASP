<!-- src/App.vue -->
<!-- Puedes poner esto en App.vue o crear un componente de navegación -->
<template>
  <nav>
    <router-link to="/login">Login</router-link> |
    <router-link to="/register">Register</router-link> |
    <router-link to="/home">Home</router-link>
  </nav>
  <router-view />
</template>

<script setup>
</script>

<style>
</style>