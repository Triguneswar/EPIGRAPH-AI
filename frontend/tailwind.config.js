/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        parchment: "#f4ecd8",
        ink: "#2b2418",
        clay: "#8a5a3b",
        bronze: "#a97142",
      },
    },
  },
  plugins: [],
};
