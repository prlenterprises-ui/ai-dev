/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Space Grotesk', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        // Custom color palette - warm earth tones with electric accents
        sand: {
          50: '#fdfcfb',
          100: '#f7f4f0',
          200: '#ede6dd',
          300: '#ddd2c3',
          400: '#c9b8a4',
          500: '#b59d85',
          600: '#a08670',
          700: '#866e5c',
          800: '#6e5b4e',
          900: '#5b4c42',
        },
        electric: {
          50: '#f0fdff',
          100: '#ccfbfe',
          200: '#99f5fd',
          300: '#5deefb',
          400: '#1addf1',
          500: '#00c4d7',
          600: '#039db4',
          700: '#0a7d91',
          800: '#126476',
          900: '#145363',
        },
        coral: {
          400: '#fb7a6e',
          500: '#f95d4f',
          600: '#e63c2f',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

