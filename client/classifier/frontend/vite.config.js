import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import eslint from 'vite-plugin-eslint';

export default defineConfig({
    plugins: [
        react(),
        eslint({
            cache: false,
            include: [ './src/**/*.js', './src/**/*.jsx' ],
            exclude: [],
        }),
    ],
    server: {
        port: 5175,
        strictPort: true,
    },
})

