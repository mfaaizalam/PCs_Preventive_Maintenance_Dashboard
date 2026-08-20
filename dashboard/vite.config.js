import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendTarget = env.VITE_API_BASE_URL || "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      // The backend (backend/app/main.py) has no CORSMiddleware configured,
      // so a browser calling it directly from a different origin/port will
      // be blocked by CORS. Proxying /api and /health through Vite's own
      // dev server avoids that entirely — the browser only ever talks to
      // this origin, and Vite forwards server-side (not subject to CORS).
      // See README.md "Connecting to the backend" for the production
      // equivalent (a reverse proxy) or the alternative of enabling
      // CORSMiddleware on the backend itself.
      proxy: {
        "/api": { target: backendTarget, changeOrigin: true },
        "/health": { target: backendTarget, changeOrigin: true },
        "/ws": { target: backendTarget, changeOrigin: true, ws: true },
      },
    },
  };
});
