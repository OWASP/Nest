/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'owasp-blue': '#98AFC7',
      }
    },
  },
  plugins: [],
  darkMode: 'selector',
};
