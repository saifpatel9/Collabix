/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./backend/templates/**/*.html",
    "./backend/frontend/templates/**/*.html",
    "./backend/frontend/src/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#fff8e7",
          100: "#ffedbd",
          200: "#f8dc8f",
          300: "#f5d080",
          400: "#e8b84b",
          500: "#d6a137",
          600: "#b98328",
          700: "#94651f",
          800: "#64451d",
          900: "#372715",
          950: "#17110a"
        },
        ink: {
          50: "#f4f6fb",
          100: "#e8ecf5",
          200: "#c7d0e2",
          300: "#8899bb",
          400: "#4a5a78",
          500: "#26344f",
          600: "#1f2d42",
          700: "#1a2438",
          800: "#141c2e",
          900: "#0d1426",
          950: "#0a0f1e"
        }
      },
      fontFamily: {
        sans: ["DM Sans", "sans-serif"],
        display: ["Syne", "sans-serif"]
      },
      boxShadow: {
        glow: "0 20px 60px rgba(232, 184, 75, 0.18)",
        workspace: "0 22px 70px rgba(0, 0, 0, 0.32)"
      }
    }
  },
  plugins: [require("@tailwindcss/forms")]
};
