from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0044_user_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="calculated_score",
            field=models.FloatField(
                db_index=True,
                default=0,
                help_text="Composite ranking score from multiple factors",
                verbose_name="Calculated score",
            ),
        ),
    ]
