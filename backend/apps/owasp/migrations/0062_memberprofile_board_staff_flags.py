# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0061_membersnapshot_repository_contributions"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberprofile",
            name="is_owasp_board_member",
            field=models.BooleanField(
                default=False,
                help_text="Whether the member is currently serving on the OWASP Board of Directors",
                verbose_name="Is OWASP Board Member",
            ),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="is_former_owasp_staff",
            field=models.BooleanField(
                default=False,
                help_text="Whether the member is a former OWASP staff member",
                verbose_name="Is Former OWASP Staff",
            ),
        ),
    ]
