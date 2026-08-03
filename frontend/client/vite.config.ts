import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],

  // Django serves the built assets from static/dist, so both the
  // manifest and the emitted files need to land there.
  build: {
    manifest: true,
    outDir: path.resolve(__dirname, "../../backend/static/dist"),
    emptyOutDir: true,
    rollupOptions: {
      // Same entry point main.tsx already imports.
      input: path.resolve(__dirname, "src/main.tsx"),
    },
  },

  server: {
    // Must match DJANGO_VITE dev_server_port in settings.py
    port: 5173,
    strictPort: true,
    // Let Django's dev server (localhost:8000) fetch this cross-origin
    cors: true,
  },
});
