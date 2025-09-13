import { defineConfig } from "vite"
import tailwindcss from "@tailwindcss/vite"
import path from "path"

const root = "frontend";

export default defineConfig({

  root: root,

  server : {
    host: "0.0.0.0",
    port: 5173,
    // wsl2 windows filesystem watch 
    watch : {
      usePolling: true
    },

    proxy: {
      '/app': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },

      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },

  },
  
  resolve: {
    alias: {
      "@": path.resolve(__dirname, root, "src"),
    },
  },

  optimizeDeps: {
    exclude: ["@tailwindcss/vite"]
  },

  plugins: [
    tailwindcss(),
  ],
})