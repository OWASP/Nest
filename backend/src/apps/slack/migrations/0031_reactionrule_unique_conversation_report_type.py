from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0030_alter_reaction_help_text"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="reactionrule",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="reactionrule",
            constraint=models.UniqueConstraint(
                fields=("conversation", "report_type"),
                name="unique_reactionrule_conversation_report_type",
                violation_error_message=(
                    "A reaction rule already exists for this conversation and report type."
                ),
            ),
        ),
    ]
