import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0028_reactionrule_emojis"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reactionrule",
            name="threshold",
            field=models.PositiveSmallIntegerField(
                default=10,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]
