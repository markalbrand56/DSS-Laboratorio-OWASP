# Infraestructura del Proyecto

## Diagrama de infraestructa

![Diagrama de infraestructura](Laboratorio-4.png)

## Tecnologías Utilizadas

### 📌 Frontend

- **Framework**: React
- **Almacenamiento de Tokens**: JWT almacenado en el navegador
- **Características principales**:
  - Formulario de Login/Register
  - Pantalla de inicio con generación de claves RSA
  - Subida y verificación de archivos firmados digitalmente

### 📡 Backend

- **Framework**: FastAPI (Python)
- **Autenticación**: JSON Web Tokens (JWT)
- **Cifrado de Contraseñas**: SHA-256
- **Firma Digital**: RSA/ECC para validación de archivos
- **Manejo de Archivos**: FastAPI UploadFile

### 🗄 Base de Datos

- **Tipo**: NoSQL
- **Gestor**: MongoDB
- **Colecciones**:
  - `users`: Almacena credenciales y claves públicas de los usuarios
  - `files`: Guarda archivos con sus respectivas firmas y claves públicas

### 🔐 Rutas de Autenticación (`/auth`)

| Endpoint              | Método | Descripción                                                                 |
|-----------------------|--------|-----------------------------------------------------------------------------|
| `/auth/register`      | POST   | Registro de nuevos usuarios.                                               |
| `/auth/login`         | POST   | Autenticación de usuarios. Retorna un JWT y el correo del usuario.         |
| `/auth/generate-keys` | POST   | Genera un par de llaves RSA y ECC para el usuario autenticado.             |

---

### 📁 Rutas de Archivos (`/file`)

| Endpoint                                                        | Método | Descripción                                                                                                                        |
|------------------------------------------------------------------|--------|------------------------------------------------------------------------------------------------------------------------------------|
| `/file/upload`                                                  | POST   | Sube un archivo a la carpeta del usuario. Puede firmarse con RSA/ECC si se especifica el método y la clave privada.               |
| `/file/files`                                                   | GET    | Obtiene todos los archivos subidos por cada usuario, excluyendo los `.hash.txt` y `.sig`. Devuelve la información agrupada.       |
| `/file/archivos/{user_email}/{file_name}/descargar`             | GET    | Descarga un archivo específico según el usuario que lo subió y el nombre del archivo.                                              |
| `/file/archivos/{user_email}/{file_name}/metadata`              | GET    | Devuelve las claves públicas del archivo solicitado, identificando al usuario y al archivo.                                        |
| `/file/verificar`                                               | POST   | Recibe un archivo y una clave pública para verificar su autenticidad o integridad (si no está firmado).                           |


## 🔄 Flujo de Trabajo

1️⃣ **Registro/Login**

- El usuario se registra o inicia sesión, obteniendo un token JWT

2️⃣ **Generación de Claves**

- Se genera un par de claves RSA (privada y pública)
- La clave privada se descarga, la clave pública se almacena en la BD

3️⃣ **Subida de Archivos**

- Los usuarios pueden subir archivos con o sin firma digital
- Si se firma, se requiere la clave privada
- Los archivos se almacenan en MongoDB con la firma y la clave pública

4️⃣ **Descarga de Archivos**

- Los usuarios pueden descargar archivos junto con la clave pública del propietario

5️⃣ **Verificación de Firma**

- Se valida la firma de un archivo antes de la descarga usando la clave pública

## 📜 Consideraciones de Seguridad

- Uso de **JWT** para autenticación segura
- Cifrado de contraseñas con **SHA-256**
- Firma digital con **RSA/ECC** para garantizar la autenticidad de los archivos
- Almacenamiento seguro de claves públicas en la base de datos

## 🚀 Instalación y Configuración

1. **Clonar el repositorio**

```bash
  git clone https://github.com/Jskenpo/LAB4_CIFRADOS_ASIMETRICOS.git

```

2. **Backend (FastAPI)**

```bash
  pip install -r requirements.txt
  uvicorn main:app --reload
```

3. **Frontend (Vue)**

```bash
  npm install
  npm start
```

4. **Base de Datos (SQLite)**

- Configurar una instancia de SQLite local

##

