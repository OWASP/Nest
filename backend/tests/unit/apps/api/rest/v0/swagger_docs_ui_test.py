import re

from django.conf import settings


class TestSwaggerDocsUI:
    def test_theme_toggle_has_tooltip_defaults(self):
        template_content = (settings.BASE_DIR / "templates" / "ninja" / "swagger.html").read_text(
            encoding="utf-8"
        )

        assert 'class="toggle-theme-btn"' in template_content
        assert 'aria-label="Switch to dark mode"' in template_content
        assert 'title="Switch to dark mode"' in template_content
        assert (
            'theme === "dark" ? "Switch to light mode" : "Switch to dark mode"' in template_content
        )
        assert 'toggleButton.setAttribute("aria-label", label);' in template_content
        assert 'toggleButton.setAttribute("title", label);' in template_content

    def test_theme_toggle_uses_pointer_cursor(self):
        css_content = (settings.BASE_DIR / "static" / "css" / "swagger-custom-ui.css").read_text(
            encoding="utf-8"
        )

        toggle_button_sections = re.findall(
            r"\.nest-top-bar \.toggle-theme-btn \{([^}]*)\}",
            css_content,
            flags=re.DOTALL,
        )
        assert any("cursor: pointer;" in section for section in toggle_button_sections)
