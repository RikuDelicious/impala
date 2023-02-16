// postcss ./tailwind-input.css -o ./static/front/dist/style.css --watch
module.exports = {
    plugins: {
        'postcss-import': {},
        'tailwindcss/nesting': {},
        tailwindcss: {},
        autoprefixer: {},
    }
}