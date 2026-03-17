from pathlib import Path
import re


class TestSwaggerDocsUI:
    def test_theme_toggle_has_tooltip_defaults(self):
        template_path = (
            Path(__file__).resolve().parents[5] / "templates" / "ninja" / "swagger.html"
        )
        template_content = template_path.read_text(encoding="utf-8")

        assert 'class="toggle-theme-btn"' in template_content
        assert 'aria-label="Switch to dark mode"' in template_content
        assert 'title="Switch to dark mode"' in template_content
        assert 'theme === "dark" ? "Switch to light mode" : "Switch to dark mode"' in template_content
        assert 'toggleButton.setAttribute("aria-label", label);' in template_content
        assert 'toggleButton.setAttribute("title", label);' in template_content

    def test_theme_toggle_uses_pointer_cursor(self):
        css_path = (
            Path(__file__).resolve().parents[5]
            / "static"
            / "css"
            / "swagger-custom-ui.css"
        )
        css_content = css_path.read_text(encoding="utf-8")

        toggle_button_sections = re.findall(
            r"\.nest-top-bar \.toggle-theme-btn \{([^}]*)\}",
            css_content,
            flags=re.DOTALL,
        )
        assert any("cursor: pointer;" in section for section in toggle_button_sections)
