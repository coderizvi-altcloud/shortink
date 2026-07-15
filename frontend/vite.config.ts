import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const HOSTED_API = "https://shortink-10c51a1f.fastapicloud.dev";

// During `npm run dev`, relative /shortlinks and /auth requests
// are proxied to the hosted Shortink API.
// Env vars come from the single project-root .env (not frontend/).
export default defineConfig({
  envDir: path.resolve(__dirname, ".."),
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/shortlinks": {
        target: HOSTED_API,
        changeOrigin: true,
        secure: true,
      },
      "/auth": {
        target: HOSTED_API,
        changeOrigin: true,
        secure: true,
      },
    },
  },
});
