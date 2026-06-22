/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        charcoal: {
          DEFAULT: '#1a1a1a',
          light: '#242424',
          border: '#2e2e2e',
        },
        cream: {
          DEFAULT: '#f5f0e8',
          muted: '#a09880',
          subtle: '#6b6055',
        },
        saffron: {
          DEFAULT: '#e8a838',
          dark: '#d4942a',
          light: '#f0be62',
        },
      },
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      typography: (theme) => ({
        invert: {
          css: {
            '--tw-prose-body': theme('colors.cream.muted'),
            '--tw-prose-headings': theme('colors.cream.DEFAULT'),
            '--tw-prose-bold': theme('colors.cream.DEFAULT'),
            '--tw-prose-bullets': theme('colors.saffron.DEFAULT'),
            '--tw-prose-hr': theme('colors.charcoal.border'),
            '--tw-prose-links': theme('colors.saffron.DEFAULT'),
            '--tw-prose-code': theme('colors.saffron.light'),
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
