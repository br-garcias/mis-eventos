import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'es2022',
    sourcemap: false,
    cssCodeSplit: true,
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return;
          if (/react-router|\/react\/|\/react-dom\//.test(id)) return 'react';
          if (/react-hook-form|@hookform|\/zod\//.test(id)) return 'forms';
          if (/lucide-react|sonner|radix-ui/.test(id)) return 'ui';
          if (/\/zustand\//.test(id)) return 'state';
        },
      },
    },
  },
});
