"""A command to perform fuzzy and exact matching of leaders with GitHub users models."""

from django.core.management.base import BaseCommand
from django.db.utils import DatabaseError
from thefuzz import fuzz

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project

MIN_NO_OF_WORDS = 2


class Command(BaseCommand):
    help = "Process raw leaders for multiple models and suggest leaders."

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name",
            type=str,
            choices=["chapter", "committee", "project"],
            help="Model name to process leaders for (chapter, committee, project)",
        )
        parser.add_argument(
            "--threshold",
            type=int,
            default=85,
            help="Threshold for fuzzy matching (0-100)",
        )

    def handle(self, *args, **kwargs):
        model_name = kwargs["model_name"].lower()
        threshold = max(0, min(kwargs["threshold"], 100))

        model_map = {
            "chapter": Chapter,
            "committee": Committee,
            "project": Project,
        }

        model_class = model_map.get(model_name)
        if not model_class:
            self.stdout.write(
                self.style.ERROR("Invalid model name! Choose from: chapter, committee, project")
            )
            return

        # Pre-fetch users
        all_users = User.objects.values("id", "login", "name")
        filtered_users = {
            u["id"]: u for u in all_users if self._is_valid_user(u["login"], u["name"])
        }

        instances = model_class.objects.prefetch_related("suggested_leaders")
        for instance in instances:
            self.stdout.write(f"Processing leaders for {model_name.capitalize()} {instance.id}...")
            exact_matches, fuzzy_matches, unmatched = self.process_leaders(
                instance.leaders_raw, threshold, filtered_users
            )

            suggested_leader_ids = {user["id"] for user in exact_matches + fuzzy_matches}
            instance.suggested_leaders.set(suggested_leader_ids)

            if unmatched:
                self.stdout.write(f"Unmatched leaders for {instance.name}: {unmatched}")

    def _is_valid_user(self, login, name):
        """Check if user meets minimum requirements."""
        return len(login) >= MIN_NO_OF_WORDS and name and len(name) >= MIN_NO_OF_WORDS

    def process_leaders(self, leaders_raw, threshold, filtered_users):
        """Process leaders with optimized matching."""
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
                exact_match = next(
                    (
                        u
                        for u in user_list
                        if u["login"].lower() == leader_lower
                        or (u["name"] and u["name"].lower() == leader_lower)
                    ),
                    None,
                )

                if exact_match:
                    exact_matches.append(exact_match)
                    self.stdout.write(f"Exact match found for {leader}: {exact_match['login']}")
                    continue

                matches = [
                    u
                    for u in user_list
                    if (fuzz.partial_ratio(leader_lower, u["login"].lower()) >= threshold)
                    or (
                        u["name"]
                        and fuzz.partial_ratio(leader_lower, u["name"].lower()) >= threshold
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
