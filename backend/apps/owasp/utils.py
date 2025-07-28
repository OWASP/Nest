"""OWASP App utilities."""

from reportlab.platypus import Table, TableStyle


def create_table(data, col_widths="*"):
    """Create a styled table for PDF generation."""
    return Table(
        data,
        colWidths=col_widths,
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), "#f2f2f2"),
                ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("BACKGROUND", (0, 1), (-1, -1), "#ffffff"),
                ("GRID", (0, 0), (-1, -1), 1, "#dddddd"),
            ]
        ),
    )
