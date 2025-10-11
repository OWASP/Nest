# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0052_remove_entitymember_owasp_entit_member__6e516f_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="is_level_compliant",
            field=models.BooleanField(
                default=True,
                verbose_name="Is level compliant",
                help_text="Indicates if the project level matches the official OWASP project_levels.json",
            ),
        ),
    ]
