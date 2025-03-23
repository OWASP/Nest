"""A command to perform fuzzy and exact matching of leaders/slack members with User model."""

from django.core.management.base import BaseCommand
from django.db.utils import DatabaseError
from thefuzz import fuzz

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project
from apps.slack.models import Member

MIN_NO_OF_WORDS = 2


class Command(BaseCommand):
    help = "Match leaders or Slack members with GitHub users using exact and fuzzy matching."

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name",
            type=str,
            choices=["chapter", "committee", "project", "member"],
            help="Model name to process: chapter, committee, project, or member",
        )
        parser.add_argument(
            "--threshold",
            type=int,
            default=75,
            help="Threshold for fuzzy matching (0-100)",
        )

    def handle(self, *args, **kwargs):
        model_name = kwargs["model_name"].lower()
        threshold = max(0, min(kwargs["threshold"], 100))

        model_map = {
            "chapter": (Chapter, "suggested_leaders"),
            "committee": (Committee, "suggested_leaders"),
            "project": (Project, "suggested_leaders"),
            "member": (Member, "suggested_users"),
        }

        if model_name not in model_map:
            self.stdout.write(
                self.style.ERROR(
                    "Invalid model name! Choose from: chapter, committee, project, member"
                )
            )
            return

        model_class, relation_field = model_map[model_name]

        # Pre-fetch GitHub users
        all_users = User.objects.values("id", "login", "name")
        filtered_users = {
            u["id"]: u for u in all_users if self._is_valid_user(u["login"], u["name"])
        }

        instances = model_class.objects.prefetch_related(relation_field)
        for instance in instances:
            self.stdout.write(f"Processing {model_name} {instance.id}...")
            if model_name == "member":
                leaders_raw = [field for field in [instance.username, instance.real_name] if field]
            else:
                leaders_raw = instance.leaders_raw

            exact_matches, fuzzy_matches, unmatched = self.process_leaders(
                leaders_raw, threshold, filtered_users
            )

            matched_user_ids = {user["id"] for user in exact_matches + fuzzy_matches}
            getattr(instance, relation_field).set(matched_user_ids)

            if unmatched:
                self.stdout.write(f"Unmatched for {instance}: {unmatched}")

    def _is_valid_user(self, login, name):
        """Check if GitHub user meets minimum requirements."""
        return len(login) >= MIN_NO_OF_WORDS and name and len(name) >= MIN_NO_OF_WORDS

    def process_leaders(self, leaders_raw, threshold, filtered_users):
        """Process leaders with optimized matching, capturing all exact matches."""
        if not leaders_raw:
            return [], [], []

        exact_matches = []
        fuzzy_matches = []
        unmatched_leaders = []
        processed_leaders = set()

        user_list = list(filtered_users.values())

        for leader in leaders_raw:
            if not leader or leader in processed_leaders:
                continue

            processed_leaders.add(leader)
            leader_lower = leader.lower()

            try:
                # Find all exact matches
                exact_matches_for_leader = [
                    u
                    for u in user_list
                    if u["login"].lower() == leader_lower
                    or (u["name"] and u["name"].lower() == leader_lower)
                ]

                if exact_matches_for_leader:
                    exact_matches.extend(exact_matches_for_leader)
                    for match in exact_matches_for_leader:
                        self.stdout.write(f"Exact match found for {leader}: {match['login']}")
                    continue

                # Fuzzy matching with token_sort_ratio
                matches = [
                    u
                    for u in user_list
                    if (fuzz.token_sort_ratio(leader_lower, u["login"].lower()) >= threshold)
                    or (
                        u["name"]
                        and fuzz.token_sort_ratio(leader_lower, u["name"].lower()) >= threshold
                    )
                ]

                new_fuzzy_matches = [m for m in matches if m not in exact_matches]
                if new_fuzzy_matches:
                    fuzzy_matches.extend(new_fuzzy_matches)
                    for match in new_fuzzy_matches:
                        self.stdout.write(f"Fuzzy match found for {leader}: {match['login']}")
                else:
                    unmatched_leaders.append(leader)

            except DatabaseError as e:
                unmatched_leaders.append(leader)
                self.stdout.write(self.style.ERROR(f"Error processing leader {leader}: {e}"))

        return exact_matches, fuzzy_matches, unmatched_leaders
