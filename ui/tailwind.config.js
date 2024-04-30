/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        oda: { primary: '#00d4aa', bg: '#0e1117', surface: '#1a1d24', accent: '#ff6b6b' },
      },
      boxShadow: {
        card: '0 4px 24px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.04)',
      },
    },
  },
  plugins: [],
}
