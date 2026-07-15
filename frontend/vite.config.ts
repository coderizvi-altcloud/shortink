import path from "node:path";
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Read .env from project root (Vite loads VITE_* vars at build time, but config runs first)
const envPath = path.resolve(__dirname, "..", ".env");
const envContent = fs.existsSync(envPath) ? fs.readFileSync(envPath, "utf-8") : "";
const envVars = Object.fromEntries(
  envContent.split("\n").filter(l => l && !l.startsWith("#")).map(l => l.split("=").map(s => s.trim()))
);
const HOSTED_API = envVars.VITE_HOSTED_API_URL || envVars.PUBLIC_BASE_URL || "";

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
