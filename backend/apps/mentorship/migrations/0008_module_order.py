from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mentorship", "0007_alter_mentor_github_user_alter_mentor_nest_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="module",
            name="order",
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text="Display order of the module within its program.",
                verbose_name="Order",
            ),
        ),
        migrations.AlterModelOptions(
            name="module",
            options={
                "ordering": ["order", "started_at"],
                "verbose_name_plural": "Modules",
            },
        ),
    ]
