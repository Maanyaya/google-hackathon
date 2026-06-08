import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/dashboard/",
  server: {
    proxy: {
      "/api": "http://localhost:8080",
      "/run": "http://localhost:8080",
      "/apps": "http://localhost:8080",
    },
  },
  build: {
    outDir: "dist",
  },
});
