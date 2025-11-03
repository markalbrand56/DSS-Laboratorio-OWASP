import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

    test: {
        globals: true,
        environment: 'jsdom', // Entorno para simular el DOM
        coverage: {
            provider: 'istanbul', // Usar istanbul para el reporte
            reporter: ['text', 'lcov'], // 'lcov' es el formato que SonarQube necesita
            reportsDirectory: './reports/coverage' // Carpeta de salida
        }
    }
})
