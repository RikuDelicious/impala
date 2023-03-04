/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/front/**/*.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/forms')],
}
