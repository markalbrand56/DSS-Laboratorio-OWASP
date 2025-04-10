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
