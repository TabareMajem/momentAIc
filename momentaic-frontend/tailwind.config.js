/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
        "./pages/**/*.{js,ts,jsx,tsx}",
        "./components/**/*.{js,ts,jsx,tsx}",
        "./App.tsx"
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    purple: '#a855f7',
                    blue: '#00f0ff',
                    dark: '#050508'
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['Space Grotesk', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'fade-in-up': 'fade-in-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'slide-up': 'slide-up-fade 0.6s ease-out forwards',
                'scale-bounce': 'scale-bounce 0.5s ease-out forwards',
                'confetti': 'confetti 2s ease-out forwards',
                'fade-in': 'fade-in 0.5s ease-out forwards',
            },
            keyframes: {
                'fade-in': {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' }
                },
                'fade-in-up': {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
                'slide-up-fade': {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
                'scale-bounce': {
                    '0%': { transform: 'scale(0)' },
                    '50%': { transform: 'scale(1.1)' },
                    '100%': { transform: 'scale(1)' }
                },
                'confetti': {
                    '0%': { transform: 'translateY(0) rotate(0deg) scale(1)', opacity: '1' },
                    '100%': { transform: 'translateY(-100vh) rotate(720deg) scale(0)', opacity: '0' }
                }
            }
        }
    },
    plugins: [],
}
