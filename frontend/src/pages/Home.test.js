import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

// --- Mocks ---

// 1. Mockea las APIs
// No necesitamos controlar lo que devuelven, solo que existan.
vi.mock('../api/auth', () => ({
    generateKeys: vi.fn()
}))
vi.mock('../api/files', () => ({
    getUserFiles: vi.fn(() => Promise.resolve([])), // Devuelve una promesa para onMounted
    uploadFile: vi.fn(),
    downloadFile: vi.fn(),
    verifyFileSignature: vi.fn(),
    getFileMetadata: vi.fn()
}))

// 2. Mockea el Router
const mockRouter = {
    push: vi.fn()
}
vi.mock('vue-router', () => ({
    useRouter: () => mockRouter
}))

// 3. Mockea SessionStorage
const mockSessionStorage = {
    getItem: vi.fn(),
    clear: vi.fn()
}
vi.stubGlobal('sessionStorage', mockSessionStorage)

// 4. Importa el componente
import Home from './Home.vue'
import { getUserFiles } from '../api/files' // Importa el mock

// 5. Limpieza antes de cada test
beforeEach(() => {
    vi.clearAllMocks()
})

// --- Tests ---

describe('Home.vue (Simple)', () => {

    // Test 1: Lógica de onMounted (Sin Token)
    // Prueba que si no hay token, redirige a /login
    it('redirige a /login si no hay token en sessionStorage', () => {
        // Simula que getItem devuelve 'null' (sin token)
        vi.mocked(mockSessionStorage.getItem).mockReturnValue(null)

        mount(Home)

        // Verifica que se llamó al router para redirigir
        expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    // Test 2: Lógica de onMounted (Con Token)
    // Prueba que si hay token, llama a fetchUserFiles
    it('llama a fetchUserFiles si hay un token', async () => {
        // Simula que getItem devuelve un token
        vi.mocked(mockSessionStorage.getItem).mockImplementation((key) => {
            if (key === 'jwt_token') return 'fake-token'
            if (key === 'email') return 'test@user.com'
            return null
        })

        mount(Home)

        // Espera a que se resuelvan las promesas de onMounted
        await flushPromises()

        // Verifica que NO se redirigió
        expect(mockRouter.push).not.toHaveBeenCalled()
        // Verifica que SÍ se llamaron los datos del usuario
        expect(getUserFiles).toHaveBeenCalled()
    })

    // Test 3: Lógica de Logout
    it('limpia sessionStorage y redirige a /login al hacer logout', async () => {
        // Monta el componente (asumiendo que tiene token)
        vi.mocked(mockSessionStorage.getItem).mockReturnValue('fake-token')
        const wrapper = mount(Home)

        // Encuentra el botón de Logout y haz clic
        await wrapper.find('button', { text: 'Logout' }).trigger('click')

    })

    // Test 4: Lógica de Go To Account
    it('redirige a /account al hacer clic en Account', async () => {
        // Monta el componente (asumiendo que tiene token)
        vi.mocked(mockSessionStorage.getItem).mockReturnValue('fake-token')
        const wrapper = mount(Home)

        // Encuentra el botón de Account y haz clic
        await wrapper.find('button', { text: 'Account' }).trigger('click')

        // Verifica que se redirigió a /account
        expect(mockRouter.push).toHaveBeenCalledWith('/account')
    })

})