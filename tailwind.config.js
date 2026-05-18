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
        }
      },
      fontFamily: {
        sans: ["Manrope", "sans-serif"]
      },
      boxShadow: {
        glow: "0 20px 60px rgba(14, 116, 144, 0.25)"
      }
    }
  },
  plugins: [require("@tailwindcss/forms")]
};
