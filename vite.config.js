import { defineConfig } from "vite"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({

  root: "parser/pages",

  server : {
    host: "0.0.0.0",
    port: 5173,

    // wsl2 windows filesystem watch 
    watch : {
      usePolling: true
    },

  },


  optimizeDeps: {
    exclude: ["@tailwindcss/vite"]
  },

  plugins: [
    tailwindcss(),
  ],
})