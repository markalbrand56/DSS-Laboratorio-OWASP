// src/api/files.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dss-lab-owasp-bck.albrand.tech'

// Subir un archivo (puede ser firmado o no)
export async function uploadFile(file, signed = false, method = null, privateKey = null) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('sign', signed)
    if (method) formData.append('method', method)
    if (privateKey) formData.append('private_key', privateKey)

    const response = await fetch(`${API_BASE_URL}/file/upload`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
        },
        body: formData,
    })

    if (!response.ok) {
        const err = await response.text()
        throw new Error(err || 'Upload failed')
    }

    return await response.json()
}


// Descargar un archivo
export async function downloadFile(userEmail, filename) {
    const response = await fetch(`${API_BASE_URL}/file/archivos/${userEmail}/${filename}/descargar`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
        },
    });

    if (!response.ok) {
        const err = await response.text();
        throw new Error(err || 'Failed to download file');
    }

    // Creamos un enlace de descarga y lo activamos
    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// Función para verificar la firma del archivo
export async function verifyFileSignature(file, userEmail, publicKey, algorithm) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_email', userEmail);
    formData.append('public_key', publicKey);
    formData.append('algorithm', algorithm);

    const response = await fetch(`${API_BASE_URL}/file/verificar`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
        },
        body: formData,
    });

    if (!response.ok) {
        const err = await response.text();
        throw new Error(err || 'File verification failed');
    }

    return await response.json();
}


// Obtener la lista de archivos de un usuario
export async function getUserFiles() {
    const response = await fetch(`${API_BASE_URL}/file/files`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
        },
    });

    if (!response.ok) {
        const err = await response.text();
        throw new Error(err || 'Failed to fetch files');
    }

    return await response.json();
}

// Obtener metadatos del archivo
export async function getFileMetadata(userEmail, filename) {
    const response = await fetch(`${API_BASE_URL}/file/archivos/${userEmail}/${filename}/metadata`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
        },
    });

    if (!response.ok) {
        const err = await response.text();
        throw new Error(err || 'Failed to fetch file metadata');
    }

    return await response.json();
}
