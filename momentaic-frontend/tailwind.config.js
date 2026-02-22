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
                sans: ['Space Grotesk', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'spin-slow': 'spin 20s linear infinite',
                'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'shimmer': 'shimmer 2s linear infinite',
                'marquee-vertical': 'marquee-vertical 20s linear infinite',
                'grid-flow': 'grid-flow 2s linear infinite',
                'fade-in-up': 'fade-in-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'slide-up': 'slide-up-fade 0.6s ease-out forwards',
                'scale-bounce': 'scale-bounce 0.5s ease-out forwards',
                'glow': 'glow-pulse 2s ease-in-out infinite',
                'float': 'float 3s ease-in-out infinite',
                'confetti': 'confetti 2s ease-out forwards',
                'fade-in': 'fade-in 0.5s ease-out forwards',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'gradient': 'gradient 8s linear infinite',
            },
            keyframes: {
                gradient: {
                    '0%, 100%': {
                        'background-size': '200% 200%',
                        'background-position': 'left center'
                    },
                    '50%': {
                        'background-size': '200% 200%',
                        'background-position': 'right center'
                    }
                },
                'fade-in': {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' }
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% center' },
                    '100%': { backgroundPosition: '200% center' },
                },
                'marquee-vertical': {
                    '0%': { transform: 'translateY(0)' },
                    '100%': { transform: 'translateY(-50%)' }
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
                'grid-flow': {
                    '0%': { transform: 'perspective(1000px) rotateX(60deg) translateY(0)' },
                    '100%': { transform: 'perspective(1000px) rotateX(60deg) translateY(50px)' }
                },
                'glow-pulse': {
                    '0%, 100%': { boxShadow: '0 0 20px rgba(168, 85, 247, 0.4)' },
                    '50%': { boxShadow: '0 0 40px rgba(168, 85, 247, 0.8)' }
                },
                'float': {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-10px)' }
                },
                'confetti': {
                    '0%': { transform: 'translateY(0) rotate(0deg) scale(1)', opacity: '1' },
                    '100%': { transform: 'translateY(-100vh) rotate(720deg) scale(0)', opacity: '0' }
                },
                'scanline': {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' }
                },
                'glitch': {
                    '0%': { transform: 'translate(0)' },
                    '20%': { transform: 'translate(-2px, 2px)' },
                    '40%': { transform: 'translate(-2px, -2px)' },
                    '60%': { transform: 'translate(2px, 2px)' },
                    '80%': { transform: 'translate(2px, -2px)' },
                    '100%': { transform: 'translate(0)' }
                },
                'pulse-neon': {
                    '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
                    '50%': { opacity: '0.7', filter: 'brightness(0.8)' }
                },
                'scanline': {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' }
                },
                'glitch': {
                    '0%': { transform: 'translate(0)' },
                    '20%': { transform: 'translate(-2px, 2px)' },
                    '40%': { transform: 'translate(-2px, -2px)' },
                    '60%': { transform: 'translate(2px, 2px)' },
                    '80%': { transform: 'translate(2px, -2px)' },
                    '100%': { transform: 'translate(0)' }
                },
                'pulse-neon': {
                    '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
                    '50%': { opacity: '0.7', filter: 'brightness(0.8)' }
                }
            },
            animation: {
                'spin-slow': 'spin 20s linear infinite',
                'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'shimmer': 'shimmer 2s linear infinite',
                'marquee-vertical': 'marquee-vertical 20s linear infinite',
                'grid-flow': 'grid-flow 2s linear infinite',
                'fade-in-up': 'fade-in-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'slide-up': 'slide-up-fade 0.6s ease-out forwards',
                'scale-bounce': 'scale-bounce 0.5s ease-out forwards',
                'glow': 'glow-pulse 2s ease-in-out infinite',
                'float': 'float 3s ease-in-out infinite',
                'confetti': 'confetti 2s ease-out forwards',
                'fade-in': 'fade-in 0.5s ease-out forwards',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'gradient': 'gradient 8s linear infinite',
                'scanline': 'scanline 8s linear infinite',
                'glitch': 'glitch 0.5s cubic-bezier(.25, .46, .45, .94) both infinite',
                'pulse-neon': 'pulse-neon 2s ease-in-out infinite',
            }
        }
    },
    plugins: [],
}
