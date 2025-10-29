/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      animation: {
        slideIn: 'slideIn 0.3s ease-out',
        slideInRight: 'slideInRight 0.3s ease-out',
        fadeIn: 'fadeIn 0.3s ease-out',
        borderDraw: 'borderDraw 1.5s ease-out',
      },
      keyframes: {
        slideIn: {
          from: { opacity: '0', transform: 'translateX(-20px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        slideInRight: {
          from: { opacity: '0', transform: 'translateX(20px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        borderDraw: {
          '0%': { 
            clipPath: 'inset(0 100% 100% 0)' 
          },
          '25%': { 
            clipPath: 'inset(0 0 100% 0)' 
          },
          '50%': { 
            clipPath: 'inset(0 0 0 0)' 
          },
          '75%': { 
            clipPath: 'inset(0 0 0 100%)' 
          },
          '100%': { 
            clipPath: 'inset(0 0 0 0)' 
          },
        },
      },
    },
  },
  plugins: [],
}