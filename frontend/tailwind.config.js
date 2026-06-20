/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B1220",
        surface: "#111827",
        primary: "#00E5FF",
        success: "#10B981",
        warning: "#F59E0B",
        error: "#EF4444",
        textPrimary: "#F8FAFC",
        textSecondary: "#94A3B8",
        borderDark: "#1E293B",
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
