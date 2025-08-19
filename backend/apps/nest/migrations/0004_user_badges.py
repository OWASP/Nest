from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nest", "0003_badge"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="badges",
            field=models.ManyToManyField(
                blank=True,
                related_name="users",
                to="nest.badge",
                verbose_name="Badges",
            ),
        ),
    ]
