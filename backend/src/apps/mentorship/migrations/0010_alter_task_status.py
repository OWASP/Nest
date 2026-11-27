from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mentorship", "0009_module_mentees_can_manage_deadlines"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("TODO", "To Do"),
                    ("IN_PROGRESS", "In Progress"),
                    ("IN_REVIEW", "In Review"),
                    ("COMPLETED", "Completed"),
                    ("UNASSIGNED", "Unassigned"),
                ],
                default="TODO",
                max_length=20,
                verbose_name="Task status",
            ),
        ),
    ]
