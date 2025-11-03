import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AllFiles from './AllFiles.vue' // Asegúrate que la ruta sea correcta

describe('AllFiles.vue', () => {
    // Test 1: Estado de carga (Loading)
    it('muestra el estado de carga correctamente', () => {
        const wrapper = mount(AllFiles, {
            props: { files: [], loading: true }
        })

        // El botón debe decir "Refreshing..." y estar deshabilitado
        const button = wrapper.find('button')
        expect(button.text()).toContain('Refreshing...')
        expect(button.attributes('disabled')).toBeDefined()
    })

    // Test 2: Estado vacío (Sin archivos)
    it('muestra "No files found" cuando la prop "files" está vacía', () => {
        const wrapper = mount(AllFiles, {
            props: { files: [], loading: false }
        })

        // Debe mostrar el mensaje de estado vacío
        expect(wrapper.text()).toContain('No files found.')
    })

    // Test 3: Renderizado de archivos
    it('renderiza la lista de usuarios y archivos correctamente', () => {
        const mockFiles = [
            { user: 'user1@test.com', files: ['file1.txt', 'file2.pdf'] },
            { user: 'user2@test.com', files: ['report.docx'] }
        ]

        const wrapper = mount(AllFiles, {
            props: { files: mockFiles, loading: false }
        })

        // Verifica que los emails y nombres de archivo estén en el DOM
        const text = wrapper.text()
        expect(text).toContain('user1@test.com')
        expect(text).toContain('file1.txt')
        expect(text).toContain('user2@test.com')
        expect(text).toContain('report.docx')

        // No debe mostrar el mensaje de estado vacío
        expect(text).not.toContain('No files found.')
    })

    // Test 4: Emisión de evento 'refresh'
    it('emite el evento "refresh" al hacer clic en el botón', async () => {
        const wrapper = mount(AllFiles, {
            props: { files: [], loading: false }
        })

        // Simula el clic en el botón
        await wrapper.find('button').trigger('click')

        // Verifica que el evento 'refresh' fue emitido una vez
        expect(wrapper.emitted()).toHaveProperty('refresh')
        expect(wrapper.emitted('refresh')).toHaveLength(1)
    })
})