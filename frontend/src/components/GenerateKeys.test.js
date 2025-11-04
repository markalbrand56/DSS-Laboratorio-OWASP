import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GenerateKeys from './GenerateKeys.vue' // Asegúrate que la ruta sea correcta

describe('GenerateKeys.vue', () => {
    // Test 1: Renderizado normal
    it('renderiza el botón correctamente', () => {
        const wrapper = mount(GenerateKeys, {
            props: { loading: false }
        })

        const button = wrapper.find('button')
        expect(button.text()).toContain('Generate Keys')
        expect(button.attributes('disabled')).toBeUndefined()
    })

    // Test 2: Estado de carga (Loading)
    it('muestra el estado de carga cuando "loading" es true', () => {
        const wrapper = mount(GenerateKeys, {
            props: { loading: true }
        })

        const button = wrapper.find('button')
        expect(button.text()).toContain('Generating keys...')
        expect(button.attributes('disabled')).toBeDefined()
    })

    // Test 3: Emisión de evento 'generate'
    it('emite el evento "generate" al hacer clic', async () => {
        const wrapper = mount(GenerateKeys)

        // Simula el clic en el botón
        await wrapper.find('button').trigger('click')

        // Verifica que el evento 'generate' fue emitido
        expect(wrapper.emitted()).toHaveProperty('generate')
        expect(wrapper.emitted('generate')).toHaveLength(1)
    })
})