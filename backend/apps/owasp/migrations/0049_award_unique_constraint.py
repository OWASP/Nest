# No-op migration: Award.name field is already unique

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0048_entitymember"),
    ]

    # No operations: Award.name field is already unique and sufficient
    operations = []
