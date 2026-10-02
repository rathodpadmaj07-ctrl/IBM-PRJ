import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: process.env.PORT ? parseInt(process.env.PORT, 10) : 80,
    allowedHosts: ["onespace.local", "localhost", "127.0.0.1"],
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://127.0.0.1:5000",
        changeOrigin: true
      }
    }
  }
});
