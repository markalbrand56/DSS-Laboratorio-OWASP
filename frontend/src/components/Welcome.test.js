// frontend/src/components/Welcome.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Welcome from './Welcome.vue' //

describe('Welcome.vue', () => {
    it('renders props correctly', () => {
        const email = 'test@example.com'
        const token = 'abc1234567890'

        const wrapper = mount(Welcome, {
            props: { email, token } //
        })

        // Comprueba que el email y el token se muestren
        expect(wrapper.text()).toContain(email)
        expect(wrapper.text()).toContain(token)
    })
})