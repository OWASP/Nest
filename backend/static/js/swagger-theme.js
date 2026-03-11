/**
 * Syncs the Swagger UI page theme with the active OWASP Nest theme.
 * The theme is stored in localStorage by next-themes under the key "theme".
 * Defaults to dark mode to match the application's default theme.
 */
(function () {
    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }

    var stored = localStorage.getItem('theme');
    applyTheme(stored || 'dark');

    // Keep in sync if the user changes the theme in another tab
    window.addEventListener('storage', function (e) {
        if (e.key === 'theme') {
            applyTheme(e.newValue || 'dark');
        }
    });
}());
