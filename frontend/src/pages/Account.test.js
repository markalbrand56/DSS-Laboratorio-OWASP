import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Account from './Account.vue' // Asegúrate que la ruta sea correcta

// --- Mocks ---

// 1. Mock de las API (para evitar llamadas reales)
vi.mock('../api/auth', () => ({
    getProfile: vi.fn(() => Promise.resolve({
        email: 'test@user.com',
        name: 'Test',
        surname: 'User',
        birthdate: '2000-01-01T00:00:00Z'
    })),
    updateProfile: vi.fn(() => Promise.resolve()),
    deleteProfile: vi.fn(() => Promise.resolve())
}))

// 2. Mock del Router (para simular el 'router.push')
const mockRouter = {
    push: vi.fn()
}
vi.mock('vue-router', () => ({
    useRouter: () => mockRouter
}))

// 3. Mock de window.confirm
vi.stubGlobal('confirm', vi.fn(() => true)) // Simula que el usuario siempre presiona "OK"

// 4. Mock de Timers (para controlar 'setTimeout')
beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
})

// --- Tests ---

describe('Account.vue', () => {
    // Test 1: Carga de datos inicial (fetchProfile)
    it('carga y muestra los datos del perfil al montar', async () => {
        const wrapper = mount(Account)
        await flushPromises()
        const emailInput = wrapper.find('input[type="email"]')
        expect(emailInput.element.value).toBe('test@user.com')
    })

    // Test 2: Flujo de Edición (editing = true)
    it('habilita los inputs al hacer clic en "Edit Profile"', async () => {
        const wrapper = mount(Account)
        await flushPromises()

        const emailInput = wrapper.find('input[type="email"]')
        const editButton = wrapper.find('button', { text: 'Edit Profile' })

        expect(emailInput.attributes('disabled')).toBeDefined()
        await editButton.trigger('click')
        expect(emailInput.attributes('disabled')).toBeUndefined()
    })

    // Test 3: Flujo de Cancelar (cancelEdit)
    it('deshabilita los inputs y restaura datos al hacer clic en "Cancel"', async () => {
        const wrapper = mount(Account)
        await flushPromises()

        await wrapper.find('button', { text: 'Edit Profile' }).trigger('click')

        const nameInput = wrapper.findAll('input[type="text"]')[0]
        await nameInput.setValue('Nuevo Nombre')
        expect(nameInput.element.value).toBe('Nuevo Nombre')

        await wrapper.find('button.secondary-btn', { text: 'Cancel' }).trigger('click')

        expect(nameInput.attributes('disabled')).toBeDefined()
        expect(nameInput.element.value).toBe('Test')
    })

    // Test 4: Guardar cambios (handleUpdate)
    it('llama a updateProfile al hacer clic en "Save Changes"', async () => {
        const wrapper = mount(Account)
        await flushPromises()

        await wrapper.find('button', { text: 'Edit Profile' }).trigger('click')
        await wrapper.find('form').trigger('submit.prevent')

        const { updateProfile } = await import('../api/auth')
        expect(updateProfile).toHaveBeenCalled()
    })

    // Test 5: Borrar cuenta (handleDelete)
    it('llama a deleteProfile al hacer clic en "Delete Account"', async () => {
        const wrapper = mount(Account)
        await flushPromises()

        await wrapper.find('button.danger-btn').trigger('click')
        expect(confirm).toHaveBeenCalled()

        const { deleteProfile } = await import('../api/auth')
        expect(deleteProfile).toHaveBeenCalled()
    })

    // Test 6: Navegación (goToHome)
    it('navega a /home al hacer clic en "Back to Home"', async () => {
        const wrapper = mount(Account)
        await flushPromises()

        const backButton = wrapper.find('button[style*="margin-top: 1rem"]')
        await backButton.trigger('click')

        expect(mockRouter.push).toHaveBeenCalledWith('/home')
    })
})