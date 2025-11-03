import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FileMetadata from './FileMetadata.vue' // Asegúrate que la ruta sea correcta

describe('FileMetadata.vue', () => {
    // Test 1: Estado vacío (sin metadata)
    it('no renderiza el card si la prop metadata es nula o indefinida', () => {
        // Monta el componente sin props
        const wrapper = mount(FileMetadata)

        // El 'v-if="metadata"' debería hacer que el card no exista
        expect(wrapper.find('.card').exists()).toBe(false)

        // Intenta de nuevo montándolo con prop 'null'
        const wrapperNull = mount(FileMetadata, {
            props: { metadata: null }
        })
        expect(wrapperNull.find('.card').exists()).toBe(false)
    })

    // Test 2: Renderizado con datos
    it('renderiza la metadata correctamente cuando se le pasan props', () => {
        const mockMetadata = {
            metodos_firma: ['rsa', 'ecc'],
            llaves_publicas: {
                rsa: '---BEGIN RSA PUBLIC KEY---',
                ecc: '---BEGIN ECC PUBLIC KEY---'
            }
        }

        const wrapper = mount(FileMetadata, {
            props: { metadata: mockMetadata }
        })

        const text = wrapper.text()

        // 1. Verifica que el card ahora sí existe
        expect(wrapper.find('.card').exists()).toBe(true)

        // 2. Verifica que los métodos de firma se muestren
        expect(text).toContain('Methods of Signature: rsa, ecc')

        // 3. Verifica que la llave RSA se muestre
        expect(text).toContain('RSA Public Key')
        expect(text).toContain('---BEGIN RSA PUBLIC KEY---')

        // 4. Verifica que la llave ECC se muestre
        expect(text).toContain('ECC Public Key')
        expect(text).toContain('---BEGIN ECC PUBLIC KEY---')

        // 5. Verifica que existan los dos botones de descarga
        const buttons = wrapper.findAll('button')
        expect(buttons.length).toBe(2)
        expect(buttons[0].text()).toContain('Download Public Key')
    })

})