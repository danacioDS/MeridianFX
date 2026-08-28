/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0A0A0F",
        surface: "#14141D",
        primary: "#00D4AA",
        "text-primary": "#FFFFFF",
        "text-secondary": "#8A8A9A",
        border: "#2A2A3A",
        success: "#00D4AA",
        warning: "#F5A623",
        error: "#FF6B6B",
        info: "#4A9EFF",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      screens: {
        tablet: "768px",
        desktop: "1200px",
      },
    },
  },
  plugins: [],
};