module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f3f8ff',
          100: '#ddecff',
          200: '#bcd2ff',
          300: '#8ab1ff',
          400: '#5e84ff',
          500: '#3a63ff',
          600: '#2f4be6',
          700: '#263baa',
          800: '#1f2c7d',
          900: '#161b53'
        }
      },
      boxShadow: {
        futuristic: '0 0 40px rgba(56, 189, 248, 0.16)',
      },
      backgroundImage: {
        'radial-grid': 'radial-gradient(circle at center, rgba(56, 189, 248, 0.16) 1px, transparent 1px)',
      }
    }
  },
  plugins: [],
};
