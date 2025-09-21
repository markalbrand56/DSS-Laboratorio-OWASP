// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Home from '../pages/Home.vue'
import Account from '../pages/Account.vue'

const routes = [
    { path: '/', redirect: '/login' }, // redirige por defecto a login
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/home', component: Home, meta: { requiresAuth: true } }, // ruta protegida
    {path: '/account', component: Account, meta: { requiresAuth: true }}, // ruta protegida
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to, from, next) => {
    if (to.meta.requiresAuth) {
        const token = sessionStorage.getItem('jwt_token')
        if (!token) {
            next('/login') // Redirige a login si no está autenticado
        } else {
            next() // Permite la navegación si está autenticado
        }
    } else {
        next() // Si no requiere autenticación, permite la navegación
    }
})

export default router
