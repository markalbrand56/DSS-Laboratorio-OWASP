import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FileDownload from './FileDownload.vue' // Asegúrate que la ruta sea correcta

describe('FileDownload.vue', () => {
    // Test 1: Estado inicial
    it('renderiza con el botón de descarga deshabilitado', () => {
        const wrapper = mount(FileDownload, {
            props: { loading: false }
        })

        const button = wrapper.find('button')
        expect(button.text()).toContain('Download')
        // Deshabilitado porque 'filename' (fileId) está vacío
        expect(button.attributes('disabled')).toBeDefined()
    })

    // Test 2: Estado de carga (Loading)
    it('muestra el estado de carga correctamente', () => {
        const wrapper = mount(FileDownload, {
            props: { loading: true }
        })

        const button = wrapper.find('button')
        expect(button.text()).toContain('Downloading...')
        expect(button.attributes('disabled')).toBeDefined()
    })

    // Test 3: Habilitar botón y emitir evento
    it('emite el evento "download" con email y filename al hacer clic', async () => {
        const wrapper = mount(FileDownload, {
            props: { loading: false }
        })

        // Busca los inputs por su placeholder
        const emailInput = wrapper.find('input[placeholder="Enter email"]')
        const fileInput = wrapper.find('input[placeholder="Enter filename"]')
        const button = wrapper.find('button')

        // Simula la entrada del usuario
        await emailInput.setValue('test@user.com')
        await fileInput.setValue('mi_archivo.zip')

        // Ahora el botón debería estar habilitado (porque filename ya no está vacío)
        expect(button.attributes('disabled')).toBeUndefined()

        // Simula el clic
        await button.trigger('click')

        // Verifica que el evento 'download' fue emitido
        expect(wrapper.emitted()).toHaveProperty('download')
        expect(wrapper.emitted('download')).toHaveLength(1)

        // Verifica que el payload (los datos emitidos) es correcto
        expect(wrapper.emitted('download')[0][0]).toEqual({
            email: 'test@user.com',
            fileId: 'mi_archivo.zip'
        })
    })

    // Test 4: Botón deshabilitado si falta filename
    it('mantiene el botón deshabilitado si solo se ingresa el email', async () => {
        const wrapper = mount(FileDownload, {
            props: { loading: false }
        })

        const emailInput = wrapper.find('input[placeholder="Enter email"]')
        const button = wrapper.find('button')

        await emailInput.setValue('test@user.com')

        // El botón debe seguir deshabilitado porque filename está vacío
        expect(button.attributes('disabled')).toBeDefined()
    })
})