import type { Config } from 'tailwindcss';
export default { content: ['./index.html', './src/**/*.{ts,tsx}'], theme: { extend: { colors: { ink: '#172026', line: '#d7dee5', brand: '#0f766e', accent: '#b45309' } } }, plugins: [] } satisfies Config;
