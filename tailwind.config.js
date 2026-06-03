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
          50: "#ecfeff",
          100: "#cffafe",
          500: "#06b6d4",
          700: "#0e7490",
          950: "#082f49"
        },
        accent: {
          50: "#fef7e8",
          100: "#fdeec8",
          200: "#fbdd8e",
          300: "#f8c854",
          400: "#e8b84b",
          500: "#d4a43e",
          600: "#c9973a",
          700: "#a67a2d",
          800: "#855e22",
          900: "#634319",
          950: "#3d280e"
        }
      },
      fontFamily: {
        sans: ["DM Sans", "sans-serif"],
        display: ["Syne", "sans-serif"]
      },
      boxShadow: {
        glow: "0 20px 60px rgba(14, 116, 144, 0.25)",
        accent: "0 8px 32px rgba(232, 184, 75, 0.2)"
      }
    }
  },
  plugins: [require("@tailwindcss/forms")]
};
