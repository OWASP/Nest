from pathlib import Path


class TestSwaggerTheme:
    """Tests for Swagger UI theme support."""

    def test_swagger_template_exists(self):
        """Tests that the custom swagger template override exists."""
        template_path = Path("templates/ninja/swagger.html")
        assert template_path.exists()

    def test_swagger_template_includes_theme_stylesheet(self):
        """Tests that the custom theme CSS is referenced in the template."""
        template_path = Path("templates/ninja/swagger.html")
        content = template_path.read_text()
        assert "swagger-theme.css" in content

    def test_swagger_template_includes_theme_script(self):
        """Tests that the theme sync script is referenced in the template."""
        template_path = Path("templates/ninja/swagger.html")
        content = template_path.read_text()
        assert "swagger-theme.js" in content

    def test_swagger_theme_css_exists(self):
        """Tests that the custom theme CSS file exists."""
        css_path = Path("static/css/swagger-theme.css")
        assert css_path.exists()

    def test_swagger_theme_js_exists(self):
        """Tests that the theme sync JS file exists."""
        js_path = Path("static/js/swagger-theme.js")
        assert js_path.exists()

    def test_swagger_theme_css_has_dark_mode_variables(self):
        """Tests that the theme CSS defines dark mode CSS variables."""
        css_path = Path("static/css/swagger-theme.css")
        content = css_path.read_text()
        assert "html.dark" in content

    def test_swagger_theme_js_syncs_from_local_storage(self):
        """Tests that the theme JS reads from localStorage."""
        js_path = Path("static/js/swagger-theme.js")
        content = js_path.read_text()
        assert "localStorage" in content
