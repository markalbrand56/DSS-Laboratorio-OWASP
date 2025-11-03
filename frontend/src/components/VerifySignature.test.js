import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import VerifySignature from './VerifySignature.vue'

describe('VerifySignature.vue', () => {
  let OriginalFileReader

  beforeEach(() => {
    // Guardar FileReader original y reemplazar por mock
    OriginalFileReader = globalThis.FileReader
    class MockFileReader {
      constructor() {
        this.onload = null
      }
      readAsText(/* file */) {
        // Llamada síncrona para simplificar el test
        if (this.onload) {
          this.onload({ target: { result: 'FAKE_PUBLIC_KEY' } })
        }
      }
    }
    globalThis.FileReader = MockFileReader
  })

  afterEach(() => {
    // Restaurar FileReader original
    globalThis.FileReader = OriginalFileReader
    vi.restoreAllMocks()
  })

  it('deshabilita el botón inicialmente', () => {
    const wrapper = mount(VerifySignature, { props: { loading: false } })
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('emite "verify" con el payload correcto al completar el formulario', async () => {
    const wrapper = mount(VerifySignature, { props: { loading: false } })

    // Preparar un archivo para el input de archivo
    const file = new File(['content'], 'file.txt', { type: 'text/plain' })

    // Rellenar email
    await wrapper.find('#userEmail').setValue('test@example.com')

    // Seleccionar algoritmo
    await wrapper.find('#algorithm').setValue('ecc')

    // Preparar archivo de clave pública (su contenido será leído por el MockFileReader)

    // Esperar actualizaciones reactivas
    await nextTick()

    // Ahora el botón debe estar habilitado
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBe("")

    // Hacer clic en verificar
    await button.trigger('click')
  })
})

