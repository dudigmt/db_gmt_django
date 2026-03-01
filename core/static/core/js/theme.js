// Theme toggle functionality
(function() {
    console.log('Theme.js loaded');  // <-- tambah ini
    console.log('Theme toggle button:', document.getElementById('theme-toggle'));  // <-- tambah ini
    // Get theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check for saved theme preference or system preference
    function getInitialTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }
    
    // Apply theme
    function setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('theme', theme);
    }
    
    // Initial theme setup
    const initialTheme = getInitialTheme();
    setTheme(initialTheme);
    
    // Toggle theme on button click
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
})();