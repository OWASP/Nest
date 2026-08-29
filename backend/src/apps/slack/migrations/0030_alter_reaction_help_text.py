from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0029_alter_reactionrule_threshold"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reactionrule",
            name="alert_user_ids",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Slack user IDs mentioned when this reaction rule triggers.",
            ),
        ),
        migrations.AlterField(
            model_name="reactionalert",
            name="reporter_user_ids",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text=(
                    "Slack user IDs that reacted with a listed emoji when the alert was posted."
                ),
            ),
        ),
    ]
