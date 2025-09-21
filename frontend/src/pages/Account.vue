<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProfile, updateProfile, deleteProfile } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const success = ref(false)
const deleted = ref(false)
const editing = ref(false)
const form = reactive({
  email: '',
  password: '',
  name: '',
  surname: '',
  birthdate: ''
})
const original = reactive({})

const fetchProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const profile = await getProfile()
    form.email = profile.email
    form.name = profile.name
    form.surname = profile.surname
    form.birthdate = profile.birthdate?.slice(0, 10) || ''
    form.password = ''
    Object.assign(original, { ...form })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const handleUpdate = async () => {
  loading.value = true
  error.value = null
  success.value = false
  try {
    await updateProfile(form.email, form.password, form.name, form.surname, form.birthdate)
    success.value = true
    editing.value = false
    Object.assign(original, { ...form, password: '' })
    form.password = ''
    setTimeout(() => (success.value = false), 1500)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const cancelEdit = () => {
  Object.assign(form, original)
  form.password = ''
  editing.value = false
  error.value = null
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) return
  loading.value = true
  error.value = null
  try {
    await deleteProfile()
    deleted.value = true
    sessionStorage.removeItem('jwt_token')
    setTimeout(() => router.push('/login'), 1500)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchProfile)

const goToHome = () => {
  router.push('/home')
}

</script>

<template>
  <div class="account-page">
    <div class="card">
      <h2>Account Profile</h2>
      <form v-if="!deleted" @submit.prevent="handleUpdate">
        <div class="form-group">
          <label>Email</label>
          <input v-model="form.email" type="email" required :disabled="!editing" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="form.password" type="password" :required="editing" :disabled="!editing" placeholder="Enter new password" />
        </div>
        <div class="form-group">
          <label>Name</label>
          <input v-model="form.name" type="text" required :disabled="!editing" />
        </div>
        <div class="form-group">
          <label>Surname</label>
          <input v-model="form.surname" type="text" required :disabled="!editing" />
        </div>
        <div class="form-group">
          <label>Birthdate</label>
          <input v-model="form.birthdate" type="date" required :disabled="!editing" />
        </div>
        <div v-if="editing">
          <button type="submit" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save Changes' }}
          </button>
          <button type="button" @click="cancelEdit" :disabled="loading" class="secondary-btn">
            Cancel
          </button>
        </div>
        <div v-else>
          <button type="button" @click="editing = true">
            Edit Profile
          </button>
          <button type="button" @click="handleDelete" class="danger-btn" :disabled="loading">
            Delete Account
          </button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">Profile updated!</p>
        <p v-if="deleted" class="success">Account deleted. Logging out...</p>
      </form>
    </div>

    <div>
      <button @click="goToHome" style="margin-top: 1rem; width: 100%;">Back to Home</button>
    </div>
  </div>
</template>

<style scoped>
.account-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 1rem;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: 500;
  color: #333;
}

.form-group {
  margin-bottom: 1.25rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #3f51b5;
  outline: none;
}

button {
  width: 100%;
  background-color: #3f51b5;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
  margin-bottom: 0.5rem;
}

button.secondary-btn {
  background-color: #e0e0e0;
  color: #333;
  margin-top: 0.5rem;
}

button.danger-btn {
  background-color: #d32f2f;
  color: white;
  margin-top: 0.5rem;
}

button:hover:not(:disabled) {
  background-color: #303f9f;
}

button.secondary-btn:hover:not(:disabled) {
  background-color: #bdbdbd;
}

button.danger-btn:hover:not(:disabled) {
  background-color: #b71c1c;
}

button:disabled {
  background-color: #9fa8da;
  cursor: not-allowed;
}

.error {
  margin-top: 1rem;
  color: #d32f2f;
  text-align: center;
}

.success {
  margin-top: 1rem;
  color: green;
  text-align: center;
}
</style>