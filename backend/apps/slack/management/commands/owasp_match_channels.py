"""A command to populate EntityChannel records from Slack data."""

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from thefuzz import fuzz

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.project import Project
from apps.slack.models import Conversation


class Command(BaseCommand):
    help = "Populate EntityChannel links for Chapters, Committees, and Projects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually saving to database",
        )
        parser.add_argument(
            "--threshold",
            type=int,
            default=80,
            help="Threshold for fuzzy matching (0-100)",
        )

    def handle(self, *args, **options):
        conversation_model = ContentType.objects.get_for_model(Conversation)
        created_count = 0
        dry_run = options["dry_run"]
        threshold = max(0, min(options["threshold"], 100))

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be saved to database")
            )
            self.stdout.write("")

        self.stdout.write(f"Using fuzzy matching with threshold: {threshold}%")
        all_conversations = list(Conversation.objects.only("id", "name").iterator())

        project_conversations = [
            conv
            for conv in all_conversations
            if conv.name and conv.name.lower().startswith("project-")
        ]
        self.stdout.write(f"Found {len(project_conversations)} project-specific channels")

        chapter_conversations = [
            conv
            for conv in all_conversations
            if conv.name and conv.name.lower().startswith("chapter-")
        ]
        self.stdout.write(f"Found {len(chapter_conversations)} chapter-specific channels")

        for model in (Chapter, Committee, Project):
            content_type = ContentType.objects.get_for_model(model)
            model_name = model.__name__

            if dry_run:
                self.stdout.write(f"Checking {model_name}s...")

            for entity in model.objects.filter(is_active=True).only("id", "name").iterator():
                if not entity.name:
                    continue

                if model == Project:
                    matches = self.find_fuzzy_matches(
                        entity.name, project_conversations, threshold
                    )
                elif model == Chapter:
                    matches = self.find_fuzzy_matches(
                        entity.name, chapter_conversations, threshold
                    )
                else:
                    matches = self.find_fuzzy_matches(entity.name, all_conversations, threshold)

                for conversation, match_score in matches:
                    if dry_run:
                        existing = EntityChannel.objects.filter(
                            entity_id=entity.id,
                            entity_type=content_type,
                            channel_id=conversation.id,
                            channel_type=conversation_model,
                        ).exists()

                        status = "EXISTS" if existing else "WOULD CREATE"
                        self.stdout.write(
                            f"  {status}: {model_name} '{entity.name}' -> "
                            f"Channel '{conversation.name}' (score: {match_score}%)"
                        )

                        if not existing:
                            created_count += 1
                    else:
                        _, created = EntityChannel.objects.get_or_create(
                            entity_id=entity.id,
                            entity_type=content_type,
                            channel_id=conversation.id,
                            channel_type=conversation_model,
                            defaults={
                                "is_active": True,
                                "is_default": True,
                                "is_reviewed": False,
                                "platform": EntityChannel.Platform.SLACK,
                            },
                        )

                        if created:
                            created_count += 1

        if dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(f"Would create {created_count} EntityChannel records.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Created {created_count} EntityChannel records.")
            )

    def find_fuzzy_matches(self, entity_name, all_conversations, threshold):
        """Find the single best conversation match using fuzzy matching."""
        cleaned_name = self.strip_owasp_prefix(entity_name)
        entity_slug = slugify(cleaned_name)
        best_match = None
        best_score = 0

        for conversation in all_conversations:
            if not conversation.name:
                continue

            conversation_slug = slugify(conversation.name)

            scores = [
                fuzz.ratio(entity_slug, conversation_slug),
                fuzz.partial_ratio(entity_slug, conversation_slug),
                fuzz.token_sort_ratio(entity_slug, conversation_slug),
                fuzz.token_set_ratio(entity_slug, conversation_slug),
            ]

            current_score = max(scores)

            if current_score >= threshold and current_score > best_score:
                best_match = conversation
                best_score = current_score

        return [(best_match, best_score)] if best_match else []

    def strip_owasp_prefix(self, name):
        """Strip 'OWASP' prefix from entity name for better matching."""
        if not name:
            return name

        name_stripped = name.strip()
        if name_stripped.upper().startswith("OWASP"):
            cleaned = name_stripped[5:].strip(" -")
            return cleaned if cleaned else name_stripped

        return name_stripped
