"""A command to match existing EntityMember leaders with GitHub Users."""

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
    help = (
        "Matches existing EntityMember leaders with GitHub Users and updates their member field."
    )

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

        model_class = model_map[model_name]

        all_users = list(User.objects.values("id", "login", "name", "email"))
        valid_users = [u for u in all_users if self.is_valid_user(u["login"], u["name"])]

        self.process_entity_members(model_class, valid_users, threshold)

    def process_entity_members(self, model_class, users_list, threshold):
        """Process existing EntityMember records for the given model."""
        model_label = model_class.__name__.capitalize()
        self.stdout.write(f"Processing {model_label} EntityMember leaders")

        entity_type = ContentType.objects.get_for_model(model_class)
        unmatched_members = EntityMember.objects.filter(
            entity_type=entity_type, role=EntityMember.Role.LEADER, member__isnull=True
        ).select_related("entity_type")

        total_members = unmatched_members.count()
        if total_members == 0:
            self.stdout.write(self.style.NOTICE(f"No unmatched {model_label} leaders found."))
            return

        self.stdout.write(f"Found {total_members} unmatched {model_label} leaders")

        matched_count = 0
        unmatched_count = 0

        for entity_member in unmatched_members:
            best_match = self.find_best_user_match(
                entity_member.member_name, entity_member.member_email, users_list, threshold
            )

            if best_match:
                entity_member.member_id = best_match["id"]
                entity_member.save(update_fields=["member"])
                matched_count += 1
                self.stdout.write(
                    f"  ✓ Matched '{entity_member.member_name}' -> {best_match['login']}"
                )
            else:
                unmatched_count += 1
                self.stdout.write(
                    self.style.WARNING(f"  ✗ No match found for '{entity_member.member_name}'")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Matched {matched_count} out of {total_members} {model_label} leaders"
            )
        )
        if unmatched_count > 0:
            self.stdout.write(self.style.WARNING(f"{unmatched_count} leaders remain unmatched"))

    def is_valid_user(self, login, name):
        """Check if GitHub user meets minimum requirements."""
        return len(login) >= ID_MIN_LENGTH and len(name or "") >= ID_MIN_LENGTH

    def find_best_user_match(self, member_name, member_email, users_list, threshold):
        """Find the best matching GitHub user for an EntityMember."""
        if not member_name:
            return None

        member_name_lower = member_name.lower()
        member_email_lower = (member_email or "").lower()

        exact_matches = []

        for user in users_list:
            user_login_lower = user["login"].lower()
            user_name_lower = (user["name"] or "").lower()
            user_email_lower = (user["email"] or "").lower()

            if user_login_lower == member_name_lower:
                exact_matches.append((user, 100, "login"))
            elif user_name_lower and user_name_lower == member_name_lower:
                exact_matches.append((user, 100, "name"))
            elif (
                member_email_lower and user_email_lower and user_email_lower == member_email_lower
            ):
                exact_matches.append((user, 100, "email"))

        if exact_matches:
            priority_order = {"login": 0, "name": 1, "email": 2}
            exact_matches.sort(key=lambda x: priority_order.get(x[2], 3))
            return exact_matches[0][0]

        fuzzy_matches = []

        for user in users_list:
            user_login_lower = user["login"].lower()
            user_name_lower = (user["name"] or "").lower()
            user_email_lower = (user["email"] or "").lower()

            login_score = fuzz.token_sort_ratio(member_name_lower, user_login_lower)
            name_score = 0
            if user_name_lower:
                name_score = fuzz.token_sort_ratio(member_name_lower, user_name_lower)
            email_score = 0
            if member_email_lower and user_email_lower:
                email_score = fuzz.token_sort_ratio(member_email_lower, user_email_lower)

            best_score = max(login_score, name_score, email_score)

            if best_score >= threshold:
                if login_score == best_score:
                    match_type = "login"
                elif name_score == best_score:
                    match_type = "name"
                else:
                    match_type = "email"
                fuzzy_matches.append((user, best_score, match_type))

        if fuzzy_matches:
            priority_order = {"login": 0, "name": 1, "email": 2}
            fuzzy_matches.sort(key=lambda x: (-x[1], priority_order.get(x[2], 3)))
            return fuzzy_matches[0][0]

        return None
