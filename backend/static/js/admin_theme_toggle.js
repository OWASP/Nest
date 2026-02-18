"use strict";

(() => {
    const THEME_STORAGE_KEY = "theme";
    const prefersDarkQuery = window.matchMedia("(prefers-color-scheme: dark)");

    function getSystemTheme() {
        return prefersDarkQuery.matches ? "dark" : "light";
    }

    function getStoredTheme() {
        const theme = localStorage.getItem(THEME_STORAGE_KEY);
        return theme === "light" || theme === "dark" ? theme : null;
    }

    function setTheme(mode, { persist } = { persist: true }) {
        const resolvedMode = mode === "light" || mode === "dark" ? mode : getSystemTheme();
        document.documentElement.dataset.theme = resolvedMode;
        if (persist) {
            localStorage.setItem(THEME_STORAGE_KEY, resolvedMode);
        }
    }

    function cycleTheme() {
        const currentTheme = document.documentElement.dataset.theme || getSystemTheme();
        setTheme(currentTheme === "dark" ? "light" : "dark", { persist: true });
    }

    function initTheme() {

        const storedTheme = getStoredTheme();
        if (storedTheme) {
            setTheme(storedTheme, { persist: true });
            return;
        }

        setTheme(getSystemTheme(), { persist: false });
    }

    prefersDarkQuery.addEventListener("change", () => {
        if (!getStoredTheme()) {
            setTheme(getSystemTheme(), { persist: false });
        }
    });

    window.addEventListener("load", () => {
        Array.from(document.getElementsByClassName("theme-toggle")).forEach((btn) => {
            btn.addEventListener("click", cycleTheme);
        });
    });

    initTheme();
})();
