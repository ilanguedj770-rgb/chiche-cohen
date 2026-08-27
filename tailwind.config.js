/** @type {import('tailwindcss').Config} */

// Charte « chaleureuse » : papier sable, encre bleu-nuit, bleu profond et cuivre.
// Les échelles gray/blue/… de Tailwind sont redéfinies plutôt qu'ajoutées : les
// classes déjà présentes dans les pages adoptent la charte sans réécriture.
const sand = {
  50: '#FAF7F2',
  100: '#F1ECE3',
  200: '#E2DCD1',
  300: '#C9C2B5',
  400: '#7E786D',
  500: '#5C574E',
  600: '#474339',
  700: '#38352E',
  800: '#262A2F',
  900: '#1B2430',
}

const blue = {
  50: '#EFF3FB',
  100: '#DDE5F6',
  200: '#C2D0EE',
  300: '#97AEE0',
  400: '#7FA0DC',
  500: '#3A62BE',
  600: '#1E40AF',
  700: '#1A3796',
  800: '#16307F',
  900: '#132861',
}

const copper = {
  50: '#FDF5EC',
  100: '#F8E6D0',
  200: '#EFCDA4',
  300: '#E0A567',
  400: '#D08B3D',
  500: '#C2761F',
  600: '#B45309',
  700: '#92400E',
  800: '#78350F',
  900: '#5C280B',
}

const green = {
  50: '#EDF4EF',
  100: '#D8E8DE',
  200: '#B9D5C4',
  300: '#8FBBA1',
  400: '#6BA383',
  500: '#4B8A66',
  600: '#2F6E4E',
  700: '#245840',
  800: '#1D4634',
  900: '#153529',
}

const red = {
  50: '#FBF0EE',
  100: '#F5DDD9',
  200: '#EBC3BC',
  300: '#DDA69D',
  400: '#CE8478',
  500: '#B85E4E',
  600: '#A34435',
  700: '#85372B',
  800: '#6B2C23',
  900: '#52221B',
}

const purple = {
  50: '#F4F1F8',
  100: '#E7E1F0',
  200: '#D3C9E3',
  300: '#B4A5CE',
  400: '#9686B7',
  500: '#7A6BA3',
  600: '#665690',
  700: '#544674',
  800: '#43395C',
  900: '#332C46',
}

const amber = {
  50: '#FDF6E7',
  100: '#F9E9C6',
  200: '#F2D79A',
  300: '#E8C06B',
  400: '#D9A742',
  500: '#C08C29',
  600: '#A0731F',
  700: '#7E5A1A',
  800: '#634716',
  900: '#4A3611',
}

module.exports = {
  content: [
    './*.html',
    './blog/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        display: ['Fraunces', 'Iowan Old Style', 'Georgia', 'serif'],
      },
      colors: {
        gray: sand,
        slate: sand,
        stone: sand,
        neutral: sand,
        zinc: sand,
        blue,
        indigo: blue,
        sky: blue,
        copper,
        orange: copper,
        green,
        emerald: green,
        teal: green,
        red,
        rose: red,
        purple,
        violet: purple,
        fuchsia: purple,
        pink: red,
        amber,
        yellow: amber,
        // Repères sémantiques utilisés directement dans les pages.
        ink: sand[900],
        sand: sand[50],
        paper: '#FDFBF8',
      },
      fontWeight: {
        // Les titres étaient en 900 sur toute la ligne : trop appuyé pour une
        // serif. On plafonne à 700, le HTML reste inchangé.
        black: '700',
        extrabold: '700',
      },
      letterSpacing: {
        tighter: '-0.02em',
        tight: '-0.012em',
      },
      borderRadius: {
        xl: '0.875rem',
        '2xl': '1.125rem',
        '3xl': '1.5rem',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        // Ombres diffuses et teintées d'encre plutôt que du noir pur.
        soft: '0 1px 2px rgba(27, 36, 48, 0.04), 0 8px 24px -14px rgba(27, 36, 48, 0.18)',
        glass: '0 1px 3px rgba(27, 36, 48, 0.04), 0 18px 44px -24px rgba(27, 36, 48, 0.22)',
        sm: '0 1px 2px rgba(27, 36, 48, 0.05)',
        DEFAULT: '0 1px 2px rgba(27, 36, 48, 0.05), 0 4px 12px -8px rgba(27, 36, 48, 0.14)',
        md: '0 2px 4px rgba(27, 36, 48, 0.04), 0 10px 24px -14px rgba(27, 36, 48, 0.18)',
        lg: '0 2px 6px rgba(27, 36, 48, 0.04), 0 16px 36px -20px rgba(27, 36, 48, 0.20)',
        xl: '0 4px 10px rgba(27, 36, 48, 0.04), 0 26px 56px -28px rgba(27, 36, 48, 0.24)',
        '2xl': '0 6px 14px rgba(27, 36, 48, 0.05), 0 40px 80px -36px rgba(27, 36, 48, 0.28)',
      },
    },
  },
  plugins: [],
}
