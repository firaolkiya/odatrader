/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        oda: { primary: '#00d4aa', bg: '#0e1117', surface: '#1a1d24', accent: '#ff6b6b' },
      },
    },
  },
  plugins: [],
}
