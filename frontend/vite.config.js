import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const apiPort = process.env.MODEX_PREVIEW_PORT || "8080";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/dashboard/",
  server: {
    proxy: {
      "/api": `http://localhost:${apiPort}`,
      "/run": `http://localhost:${apiPort}`,
      "/apps": `http://localhost:${apiPort}`,
    },
  },
  build: {
    outDir: "dist",
  },
});
