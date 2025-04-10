// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Home from '../pages/Home.vue'

const routes = [
    { path: '/', redirect: '/login' }, // redirige por defecto a login
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/home', component: Home },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
