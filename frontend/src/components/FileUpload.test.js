import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FileUpload from './FileUpload.vue' // Asegúrate que la ruta sea correcta

describe('FileUpload.vue', () => {
    // Test 1: Estado inicial
    it('renderiza con el botón de subida deshabilitado', () => {
        const wrapper = mount(FileUpload, {
            props: { loading: false }
        })

        const button = wrapper.find('button.upload-button')
        // El botón debe estar deshabilitado porque 'file' (el archivo) es nulo
        expect(button.attributes('disabled')).toBeDefined()
    })

    // Test 2: Habilitar el botón al seleccionar archivo
    it('habilita el botón de subida solo cuando se selecciona un archivo', async () => {
        const wrapper = mount(FileUpload)
        const button = wrapper.find('button.upload-button')

        // 1. Botón deshabilitado inicialmente
        expect(button.attributes('disabled')).toBeDefined()

        // 2. Simula la selección de un archivo
        // Creamos un archivo falso
        const mockFile = new File(['contenido del archivo'], 'test-file.txt', { type: 'text/plain' })

        // Obtenemos el input del archivo (por su ID)
        const fileInput = wrapper.find('#file')

        // Asignamos el archivo al input (requiere mockear 'files' del elemento)
        await Object.defineProperty(fileInput.element, 'files', {
            value: [mockFile],
            writable: true
        })

        // Disparamos el evento 'change'
        await fileInput.trigger('change')

        // 3. El botón ahora debe estar habilitado
        expect(button.attributes('disabled')).toBeUndefined()
    })

    // Test 3: Emisión de evento con datos
    it('emite el evento "upload" con los datos correctos al hacer clic', async () => {
        const wrapper = mount(FileUpload)

        // 1. Simula la selección de un archivo
        const mockFile = new File(['contenido'], 'file.txt')
        const fileInput = wrapper.find('#file')
        await Object.defineProperty(fileInput.element, 'files', { value: [mockFile], writable: true })
        await fileInput.trigger('change')

        // 2. Simula cambiar los inputs
        // Marca el checkbox 'signed'
        await wrapper.find('input[type="checkbox"]').setValue(true)
        // Cambia el método a 'ecc'
        await wrapper.find('select').setValue('ecc')

        // 3. Simula el clic en el botón de subida
        await wrapper.find('button.upload-button').trigger('click')

        // 4. Verifica que el evento 'upload' fue emitido
        expect(wrapper.emitted()).toHaveProperty('upload')

        // 5. Verifica el payload (los datos emitidos)
        // El privateKey estará vacío porque no simulamos la carga (es más complejo)
        expect(wrapper.emitted('upload')[0][0]).toEqual({
            file: mockFile,
            signed: true,
            method: 'ecc',
            privateKey: '' // Esto es esperado
        })
    })
})