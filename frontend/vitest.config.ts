import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    env: { TZ: "UTC" },
    setupFiles: ["./src/tests/index.ts"],
    include: ["src/tests/**/*.test.ts", "src/tests/**/*.test.tsx"],
    css: false,
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});