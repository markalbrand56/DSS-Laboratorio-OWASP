import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

// --- Mocks ---

// 1. Mockea la *ruta* del módulo.
vi.mock('../api/auth')

// 2. Mockea el Router
const mockRouter = {
    push: vi.fn()
}
vi.mock('vue-router', () => ({
    useRouter: () => mockRouter
}))

// 3. Mockea Timers para controlar setTimeout
beforeEach(() => {
    vi.useFakeTimers()
})

// 4. Importa el componente y la función mockeada
import Register from './Register.vue' // Asegúrate que la ruta sea correcta
import { register } from '../api/auth' // Importa la *versión mockeada*

// 5. Limpieza antes de cada test
beforeEach(() => {
    vi.clearAllMocks()

    // Resetea el mock de 'register' a un éxito por defecto
    vi.mocked(register).mockResolvedValue({
        message: 'User created successfully'
    })
})

// --- Tests ---

describe('Register.vue', () => {
    // Test 1: Renderizado inicial
    it('renderiza el formulario con el botón "Register" habilitado', () => {
        const wrapper = mount(Register)

        expect(wrapper.find('input[type="email"]').exists()).toBe(true)
        expect(wrapper.find('input[type="password"]').exists()).toBe(true)

        const button = wrapper.find('button[type="submit"]')
        expect(button.text()).toContain('Register')
        expect(button.attributes('disabled')).toBeUndefined()
    })

    // Test 2: Navegación a Login (goToLogin)
    it('llama a router.push("/login") al hacer clic en el enlace', async () => {
        const wrapper = mount(Register)

        await wrapper.find('a', { text: 'Inicia sesión aquí' }).trigger('click')

        expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    // Test 3: Registro Exitoso (handleRegister)
    it('llama a la API y redirige a /login en un registro exitoso', async () => {
        const wrapper = mount(Register)

        // --- INICIO DE LA CORRECCIÓN ---
        const textInputs = wrapper.findAll('input[type="text"]')
        // --- FIN DE LA CORRECCIÓN ---

        // 1. Llena el formulario
        await wrapper.find('input[type="email"]').setValue('new@user.com')
        await wrapper.find('input[type="password"]').setValue('newpassword123')
        await textInputs[0].setValue('New') // Input de Name
        await textInputs[1].setValue('User') // Input de Surname
        await wrapper.find('input[type="date"]').setValue('2000-01-01')

        // 2. Envía el formulario
        await wrapper.find('form').trigger('submit.prevent')

        // 3. Verifica que la API fue llamada con los datos correctos
        expect(register).toHaveBeenCalledWith(
            'new@user.com',
            'newpassword123',
            'New',
            'User',
            '2000-01-01'
        )

        // 4. Espera que la promesa de registro se resuelva
        await flushPromises()

        // 5. Verifica que se muestra el mensaje de éxito
        expect(wrapper.text()).toContain('¡Registro exitoso! Redirigiendo...')

        // 6. Ejecuta el setTimeout
        vi.runAllTimers()

        // 7. Verifica que se redirigió a /login
        expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    // Test 4: Registro Fallido (handleRegister)
    it('muestra un mensaje de error si la API falla', async () => {
        // Configura el mock para que falle
        const apiError = new Error('Email already exists')
        vi.mocked(register).mockRejectedValue(apiError)

        const wrapper = mount(Register)

        // --- INICIO DE LA CORRECCIÓN ---
        const textInputs = wrapper.findAll('input[type="text"]')
        // --- FIN DE LA CORRECCIÓN ---

        // 1. Llena y envía el formulario
        await wrapper.find('input[type="email"]').setValue('bad@user.com')
        await wrapper.find('input[type="password"]').setValue('12345678')
        await textInputs[0].setValue('Bad') // Input de Name
        await textInputs[1].setValue('User') // Input de Surname
        await wrapper.find('input[type="date"]').setValue('2000-01-01')
        await wrapper.find('form').trigger('submit.prevent')

        await flushPromises() // Espera que la promesa fallida se resuelva

        // 2. Verifica que se muestra el error
        const errorP = wrapper.find('p.error')
        expect(errorP.exists()).toBe(true)
        expect(errorP.text()).toContain('Email already exists')

        // 3. Verifica que NO se redirigió
        expect(mockRouter.push).not.toHaveBeenCalled()
    })

    // Test 5: Validación de cliente (Sanitize)
    it('falla la validación del cliente si el nombre contiene HTML', async () => {
        const wrapper = mount(Register)

        // --- INICIO DE LA CORRECCIÓN ---
        const textInputs = wrapper.findAll('input[type="text"]')
        // --- FIN DE LA CORRECCIÓN ---

        // 1. Llena el formulario con datos inválidos
        await wrapper.find('input[type="email"]').setValue('new@user.com')
        await wrapper.find('input[type="password"]').setValue('newpassword123')
        await textInputs[0].setValue('<script>') // Input de Name (Payload)
        await textInputs[1].setValue('User') // Input de Surname
        await wrapper.find('input[type="date"]').setValue('2000-01-01')

        // 2. Envía el formulario
        await wrapper.find('form').trigger('submit.prevent')
    })
})