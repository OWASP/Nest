"""A command to perform fuzzy and exact matching of leaders/slack members with User model."""

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from thefuzz import fuzz

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project

ID_MIN_LENGTH = 2


class Command(BaseCommand):
    help = "Matches entity leader names with GitHub Users and creates EntityMember records."

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name",
            type=str,
            choices=("chapter", "committee", "project"),
            help="Model to process: chapter, committee, project.",
        )
        parser.add_argument(
            "--threshold",
            type=int,
            default=75,
            help="Threshold for fuzzy matching (0-100)",
        )

    def handle(self, *_args, **kwargs):
        model_name = kwargs["model_name"].lower()
        threshold = max(0, min(kwargs["threshold"], 100))

        model_map = {
            "chapter": Chapter,
            "committee": Committee,
            "project": Project,
        }

        if model_name not in model_map:
            self.stdout.write(
                self.style.ERROR("Invalid model name! Choose from: chapter, committee, project")
            )
            return

        models_to_process = model_map[model_name]

        all_users = list(User.objects.values("id", "login", "name"))
        valid_users = [u for u in all_users if self.is_valid_user(u["login"], u["name"])]

        self.process_entities(models_to_process, valid_users, threshold)

        self.stdout.write(self.style.SUCCESS("\nCommand finished successfully."))

    def process_entities(self, model_class, users_list, threshold):
        """Process entries."""
        model_label = model_class.__name__.capitalize()
        self.stdout.write(f"\n--- Processing {model_label} ---")

        new_members_to_create = []

        entity_type = ContentType.objects.get_for_model(model_class)

        for entity in model_class.objects.filter(is_active=True, has_active_repositories=True):
            if not entity.leaders_raw:
                continue

            for index, leader_name in enumerate(entity.leaders_raw):
                matched_users = self.find_all_user_matches(leader_name, users_list, threshold)

                if not matched_users:
                    continue

                new_members_to_create.extend(
                    EntityMember(
                        entity_type=entity_type,
                        entity_id=entity.pk,
                        member_id=user["id"],
                        kind=EntityMember.MemberKind.LEADER,
                        is_reviewed=False,
                        order=((index + 1) * 10),
                    )
                    for user in matched_users
                )

        if new_members_to_create:
            created_records = EntityMember.objects.bulk_create(
                new_members_to_create,
                ignore_conflicts=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  -> Created {len(created_records)} new leader records for {model_label}."
                )
            )
        else:
            self.stdout.write(
                self.style.NOTICE(f"  -> No new leader records to create for {model_label}.")
            )

    def is_valid_user(self, login, name):
        """Check if GitHub user meets minimum requirements."""
        return len(login) >= ID_MIN_LENGTH and len(name or "") >= ID_MIN_LENGTH

    def find_all_user_matches(self, leader_name, users_list, threshold):
        """Find user matches for a list of raw leader names."""
        if not leader_name:
            return []

        leader_lower = leader_name.lower()

        matches = [
            user
            for user in users_list
            if user["login"].lower() == leader_lower
            or (user["name"] and user["name"].lower() == leader_lower)
        ]

        if not matches:
            for user in users_list:
                score = fuzz.token_sort_ratio(leader_lower, user["login"].lower())
                if user["name"]:
                    score = max(score, fuzz.token_sort_ratio(leader_lower, user["name"].lower()))

                if score >= threshold:
                    matches.append(user)

        return list({user["id"]: user for user in matches}.values())
