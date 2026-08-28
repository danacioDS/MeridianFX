/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Colores del mockup
        paper: '#ffffff',
        panel: '#F8F9FB',
        'panel-2': '#F2F4F7',
        ink: '#10151F',
        'ink-soft': '#4B5566',
        muted: '#8891A0',
        line: '#E6E9EE',
        navy: '#16233F',
        meridian: '#0E7C86',
        'meridian-soft': '#E4F2F1',
        bull: '#0E8F5F',
        'bull-soft': '#E7F5EE',
        bear: '#C4453A',
        'bear-soft': '#FBEAE8',
        amber: '#B8860B',
        'amber-soft': '#FBF3DF',
        violet: '#5B4EA8',
        'violet-soft': '#EFEDFA',
      },
      fontFamily: {
        mono: ['IBM Plex Mono', 'monospace'],
        serif: ['Instrument Serif', 'serif'],
      },
      borderRadius: {
        'mockup': '12px',
        'mockup-sm': '8px',
      },
    },
  },
  plugins: [],
}
