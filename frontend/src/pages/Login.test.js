import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

// --- Mocks ---

// 1. Mockea la *ruta* del módulo. Esto se eleva (hoisted) automáticamente.
vi.mock('../api/auth')

// 2. Mockea el Router
const mockRouter = {
    push: vi.fn()
}
vi.mock('vue-router', () => ({
    useRouter: () => mockRouter
}))

// 3. Mockea sessionStorage
const mockSessionStorage = {
    setItem: vi.fn()
}
vi.stubGlobal('sessionStorage', mockSessionStorage)
vi.stubGlobal('alert', vi.fn()) // Mockea 'alert' para evitar popups

// 4. AHORA importa el componente y la función mockeada
import Login from './Login.vue' // Asegúrate que la ruta sea correcta
import { login } from '../api/auth' // Importa la *versión mockeada*

// 5. Limpieza y configuración antes de CADA test
beforeEach(() => {
    vi.clearAllMocks()

    // Resetea el mock de 'login' a un éxito por defecto usando vi.mocked()
    vi.mocked(login).mockResolvedValue({
        jwt_token: 'fake_token_123',
        email: 'test@user.com'
    })
})

// --- Tests ---

describe('Login.vue', () => {
    // Test 1: Renderizado inicial
    it('renderiza el formulario con el botón habilitado', () => {
        const wrapper = mount(Login)

        expect(wrapper.find('input[type="email"]').exists()).toBe(true)
        expect(wrapper.find('input[type="password"]').exists()).toBe(true)

        const button = wrapper.find('button[type="submit"]')
        expect(button.text()).toContain('Login')
        expect(button.attributes('disabled')).toBeUndefined()
    })

    // Test 2: Estado de carga
    it('muestra "Logging in..." y deshabilita el botón durante el login', async () => {
        const wrapper = mount(Login)

        // 1. Dispara el submit (esto llama a handleLogin e inmediatamente setea loading.value = true)
        wrapper.find('form').trigger('submit.prevent')

        // 2. Espera solo un "tick" del DOM para que Vue renderice el estado 'loading = true'
        await wrapper.vm.$nextTick()

        // 3. AHORA comprueba el estado de "cargando", ANTES de que la promesa se resuelva
        let button = wrapper.find('button[type="submit"]')
        expect(button.text()).toContain('Logging in...')
        expect(button.attributes('disabled')).toBeDefined()

        // 4. Ahora sí, permite que la promesa se complete (y se ejecute el 'finally')
        await flushPromises()

        // 5. Verifica que el botón se restaura
        button = wrapper.find('button[type="submit"]') // Re-busca el botón
        expect(button.text()).toContain('Login')
        expect(button.attributes('disabled')).toBeUndefined()
    })

    // Test 3: Navegación a Registro
    it('llama a router.push("/register") al hacer clic en el enlace', async () => {
        const wrapper = mount(Login)
        await wrapper.find('a', { text: 'Regístrate aquí' }).trigger('click')
        expect(mockRouter.push).toHaveBeenCalledWith('/register')
    })

    // Test 4: Login Exitoso
    it('llama a la API, guarda en sessionStorage y navega a /home en un login exitoso', async () => {
        const wrapper = mount(Login)

        await wrapper.find('input[type="email"]').setValue('test@user.com')
        await wrapper.find('input[type="password"]').setValue('password123')
        await wrapper.find('form').trigger('submit.prevent')

        expect(login).toHaveBeenCalledWith('test@user.com', 'password123')
        await flushPromises()

        expect(mockSessionStorage.setItem).toHaveBeenCalledWith('jwt_token', 'fake_token_123')
        expect(mockSessionStorage.setItem).toHaveBeenCalledWith('email', 'test@user.com')
        expect(mockRouter.push).toHaveBeenCalledWith('/home')
    })

    // Test 5: Login Fallido (401 - Credenciales inválidas)
    it('muestra "Credenciales inválidas" en un error 401', async () => {
        const apiError = new Error('Unauthorized')
        apiError.status = 401
        vi.mocked(login).mockRejectedValue(apiError)

        const wrapper = mount(Login)
        await wrapper.find('form').trigger('submit.prevent')
        await flushPromises()

        const errorP = wrapper.find('p.error')
        expect(errorP.text()).toContain('Credenciales inválidas')
        expect(mockSessionStorage.setItem).not.toHaveBeenCalled()
        expect(mockRouter.push).not.toHaveBeenCalled()
    })

    // Test 6: Login Fallido (429 - Rate Limit)
    it('muestra "Demasiados intentos" en un error 429', async () => {
        const apiError = new Error('Too many requests')
        apiError.status = 429
        vi.mocked(login).mockRejectedValue(apiError)

        const wrapper = mount(Login)
        await wrapper.find('form').trigger('submit.prevent')
        await flushPromises()

        const errorP = wrapper.find('p.error')
        expect(errorP.text()).toContain('Demasiados intentos')
    })
})
