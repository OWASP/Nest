"use strict";

(() => {
    const THEME_STORAGE_KEY = "theme";
    const prefersDarkQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const root = document.documentElement;

    function applyTheme(theme, persist = false) {
        root.dataset.theme = theme;
        if (persist) localStorage.setItem(THEME_STORAGE_KEY, theme);
    }

    function cycleTheme() {
        const currentTheme = root.dataset.theme || getStoredTheme() || getSystemTheme();
        applyTheme(currentTheme === "dark" ? "light" : "dark", true);
    }

    const getStoredTheme = () => {
        const theme = localStorage.getItem(THEME_STORAGE_KEY);
        return theme === "light" || theme === "dark" ? theme : null;
    };

    const getSystemTheme = () => (prefersDarkQuery.matches ? "dark" : "light");

    prefersDarkQuery.addEventListener("change", () => {
        if (!getStoredTheme()) {
            applyTheme(getSystemTheme());
        }
    });

    window.addEventListener("load", () => {
        document.querySelectorAll(".theme-toggle").forEach((btn) => {
            btn.addEventListener("click", (event) => {
                event.preventDefault();
                cycleTheme();
            });
        });
    });

    applyTheme(getStoredTheme() || getSystemTheme());
})();
