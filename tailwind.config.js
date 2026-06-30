/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ['selector', '[data-theme="dark"]'],
    content: [
        './templates/**/*.html',
        './accounts/templates/**/*.html',
        './articles/templates/**/*.html',
    ],
    safelist: ['input', 'pr-11'],
    theme: {
        container: {
            center: true,
            padding: '1.5rem',
            screens: { '2xl': '1200px' },
        },
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
                mono: ['"JetBrains Mono"', 'monospace'],
            },
            colors: {
                border: 'hsl(var(--border))',
                input: 'hsl(var(--input))',
                ring: 'hsl(var(--ring))',
                background: 'hsl(var(--background))',
                foreground: 'hsl(var(--foreground))',
                rating: 'hsl(var(--rating))',
                primary: {
                    DEFAULT: 'hsl(var(--primary))',
                    foreground: 'hsl(var(--primary-foreground))',
                },
                secondary: {
                    DEFAULT: 'hsl(var(--secondary))',
                    foreground: 'hsl(var(--secondary-foreground))',
                },
                muted: {
                    DEFAULT: 'hsl(var(--muted))',
                    foreground: 'hsl(var(--muted-foreground))',
                },
                accent: {
                    DEFAULT: 'hsl(var(--accent))',
                    foreground: 'hsl(var(--accent-foreground))',
                },
                destructive: {
                    DEFAULT: 'hsl(var(--destructive))',
                    foreground: 'hsl(var(--destructive-foreground))',
                },
                card: {
                    DEFAULT: 'hsl(var(--card))',
                    foreground: 'hsl(var(--card-foreground))',
                },
                popover: {
                    DEFAULT: 'hsl(var(--popover))',
                    foreground: 'hsl(var(--popover-foreground))',
                },
            },
            borderRadius: {
                lg: 'var(--radius)',
                md: 'calc(var(--radius) - 2px)',
                sm: 'calc(var(--radius) - 4px)',
            },
            keyframes: {
                'fade-in': {
                    from: { opacity: '0', transform: 'translateY(8px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
                'fade-in-scale': {
                    from: { opacity: '0', transform: 'scale(0.97)' },
                    to: { opacity: '1', transform: 'scale(1)' },
                },
            },
            animation: {
                'fade-in': 'fade-in 0.5s ease both',
                'fade-in-scale': 'fade-in-scale 0.25s ease both',
            },
        },
    },
    plugins: [],
};
