/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '**/templates/**/*.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui')
  ],
  daisyui: {
    styled: true,
    themes: [
      {
        nitro: {
          "primary": "#FFD44E",
          "secondary": "#D926A9",
          "accent": "#1FB2A6",
          "neutral": "#191D24",
          "base-100": "#2A303C",
          "info": "#3ABFF8",
          "success": "#36D399",
          "warning": "#7F6926",
          "error": "#F87272",
        }
      }
    ],
    base: true,
    utils: true,
    logs: true,
    rtl: false,
    prefix: "",
    darkTheme: "dark",
  },
}
