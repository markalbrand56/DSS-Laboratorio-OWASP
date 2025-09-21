// src/api/auth.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
        const err = await response.text()
        throw new Error(err || 'Login failed')
    }

    return await response.json()
}

export async function register(email, password, name, surname, birthdate) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name, surname, birthdate }),
    })

    if (!response.ok) {
        const err = await response.text()
        throw new Error(err || 'Register failed')
    }

    return await response.json()
}

// Función para generar llaves RSA y ECC
export async function generateKeys() {
    const response = await fetch(`${API_BASE_URL}/auth/generate-keys`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
            'Content-Type': 'application/json',
        },
    })

    if (!response.ok) {
        const err = await response.text()
        throw new Error(err || 'Key generation failed')
    }

    return await response.json()
}