module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1A237E',
        accent: '#1976D2',
        success: '#43A047',
        error: '#E53935',
        background: '#E3F2FD',
        neutral: '#F5F5F5',
        text: '#212121',
        secondary: '#757575',
      },
      fontFamily: {
        heading: ['Roboto Slab', 'serif'],
        body: ['Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}; 