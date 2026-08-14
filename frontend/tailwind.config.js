/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366f1', // Royal Purple
          light: '#818cf8',
          dark: '#4f46e5',
        },
        accent: {
          DEFAULT: '#06b6d4', // Teal/Cyan
          light: '#22d3ee',
          dark: '#0891b2',
        },
        surface: {
          DEFAULT: '#ffffff', // White surface
          light: '#f9fafb',   // Light gray background
          dark: '#111827',    // Dark background if needed
        },
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
