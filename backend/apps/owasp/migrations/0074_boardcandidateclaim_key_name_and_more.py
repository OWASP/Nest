# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add key and rename title to name for claim models."""

    dependencies = [
        ("owasp", "0073_boardcandidateclaim_boardcandidateclaimevidence_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="boardcandidateclaim",
            name="key",
            field=models.CharField(default="", max_length=100, unique=True, verbose_name="Key"),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name="boardcandidateclaim",
            old_name="title",
            new_name="name",
        ),
        migrations.AddField(
            model_name="boardcandidateclaimevidence",
            name="key",
            field=models.CharField(default="", max_length=100, unique=True, verbose_name="Key"),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name="boardcandidateclaimevidence",
            old_name="title",
            new_name="name",
        ),
    ]
