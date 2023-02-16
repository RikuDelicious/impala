/** @type {import('tailwindcss').Config} */
// npx tailwindcss -i ./tailwind-input.css -o ./static/front/dist/style.css --watch
module.exports = {
  content: [
    "./templates/front/**/*.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
