from django.db import migrations, models


def copy_emoji_name_to_emojis(apps, _schema_editor):
    """Copy each reaction rule's single emoji name into the emojis list."""
    reaction_rule_model = apps.get_model("slack", "ReactionRule")
    for rule in reaction_rule_model.objects.all():
        rule.emojis = [rule.emoji_name] if rule.emoji_name else []
        rule.save(update_fields=["emojis"])


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0027_alter_reactionrule_emoji_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="reactionrule",
            name="emojis",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Slack emojis that trigger this reaction rule.",
            ),
        ),
        migrations.RunPython(
            copy_emoji_name_to_emojis,
            migrations.RunPython.noop,
        ),
        migrations.AlterUniqueTogether(
            name="reactionrule",
            unique_together={("conversation", "report_type")},
        ),
        migrations.RemoveField(
            model_name="reactionrule",
            name="emoji_name",
        ),
    ]
