from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0023_alter_workspace_charfield_defaults"),
    ]

    operations = [
        migrations.RenameField(
            model_name="workspace",
            old_name="invite_link_alert_message_ts",
            new_name="invite_link_last_alert_message_ts",
        ),
    ]
