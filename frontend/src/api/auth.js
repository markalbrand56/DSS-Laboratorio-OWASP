// src/api/auth.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dss-lab-owasp-bck.albrand.tech'

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

export async function getProfile() {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
        },
    })

    if (!response.ok) {
        const err = await response.text()
        throw new Error(err || 'Fetching profile failed')
    }

    return await response.json()
}

export async function updateProfile(email, password, name, surname, birthdate) {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name, surname, birthdate }),
    })

    if (!response.ok) {
        const err = await response.text()
        throw new Error(err || 'Updating profile failed')
    }

    return await response.json()
}

export async function deleteProfile() {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
        },
    })

    if (!response.ok) {
        const err = await response.text()
        throw new Error(err || 'Deleting profile failed')
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