import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server for the SSE + SWR demo client. Talks directly to Django
// (CORS_ALLOW_ALL_ORIGINS = True in settings.py), so no proxy needed locally.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
