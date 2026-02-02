from django.db import migrations


def update_bug_slash_css_class(apps, _schema_editor):
    """Rename stored css_class from 'bug_slash' to 'bugSlash'."""
    Badge = apps.get_model("nest", "Badge")
    Badge.objects.filter(css_class="bug_slash").update(css_class="bugSlash")


def reverse_bug_slash_css_class(apps, _schema_editor):
    """Rollback css_class from 'bugSlash' to 'bug_slash'."""
    Badge = apps.get_model("nest", "Badge")
    Badge.objects.filter(css_class="bugSlash").update(css_class="bug_slash")


class Migration(migrations.Migration):
    dependencies = [
        ("nest", "0072"),
    ]

    operations = [
        migrations.RunPython(
            update_bug_slash_css_class,
            reverse_bug_slash_css_class,
        ),
    ]
