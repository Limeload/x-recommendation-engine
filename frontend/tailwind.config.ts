import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#000000',
        'dark-secondary': '#16181c',
        'dark-border': '#38444d',
      },
    },
  },
  plugins: [],
}
export default config
