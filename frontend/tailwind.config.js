/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        border: "var(--border)",
        text: "var(--text)",
        "owasp-blue": "#98AFC7",
      },
    },
  },
  darkMode: "selector",
  plugins: [],
};
