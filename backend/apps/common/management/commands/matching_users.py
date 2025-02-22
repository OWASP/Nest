"""A command to perform fuzzy and exact matching of leaders with GitHub users models."""

from django.core.management.base import BaseCommand
from django.db import models
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
            help="Model name to process leaders for (e.g., Chapter, Committee, Project)",
        )
        parser.add_argument(
            "--threshold", type=int, default=95, help="Threshold for fuzzy matching"
        )

    def handle(self, *args, **kwargs):
        model_name = kwargs["model_name"]
        threshold = kwargs["threshold"]

        model_map = {
            "chapter": Chapter,
            "committee": Committee,
            "project": Project,
        }

        model_class = model_map.get(model_name.lower())

        if not model_class:
            self.stdout.write(
                self.style.ERROR("Invalid model name! Choose from: chapter, committee, project")
            )
            return

        all_users = User.objects.all()
        filtered_users = [
            u
            for u in all_users
            if len(u.login) >= MIN_NO_OF_WORDS and (u.name and len(u.name) >= MIN_NO_OF_WORDS)
        ]

        instances = model_class.objects.all()
        for instance in instances:
            self.stdout.write(f"Processing leaders for {model_name.capitalize()} {instance.id}...")
            exact_matches, fuzzy_matches, unmatched_leaders = self.process_leaders(
                instance.leaders_raw, threshold, filtered_users
            )
            instance.suggested_leaders.set(list(set(exact_matches + fuzzy_matches)))
            instance.save()

            if unmatched_leaders:
                self.stdout.write(f"Unmatched leaders for {instance.name}: {unmatched_leaders}")

    def process_leaders(self, leaders_raw, threshold, filtered_users):
        """Process leaders and return the suggested leaders with exact and fuzzy matching."""
        if not leaders_raw:
            return [], [], []

        exact_matches = []
        fuzzy_matches = []
        unmatched_leaders = []

        for leader in leaders_raw:
            try:
                leaderdata = User.objects.filter(
                    models.Q(login__iexact=leader) | models.Q(name__iexact=leader)
                ).first()
                if leaderdata:
                    exact_matches.append(leaderdata)
                    self.stdout.write(f"Exact match found for {leader}: {leaderdata}")
                    continue

                matches = [
                    u
                    for u in filtered_users
                    if (fuzz.partial_ratio(leader, u.login) >= threshold)
                    or (fuzz.partial_ratio(leader, u.name if u.name else "") >= threshold)
                ]

                new_fuzzy_matches = [m for m in matches if m not in exact_matches]
                fuzzy_matches.extend(new_fuzzy_matches)

                if matches:
                    for match in new_fuzzy_matches:
                        self.stdout.write(f"Fuzzy match found for {leader}: {match}")
                else:
                    unmatched_leaders.append(leader)

            except DatabaseError as e:
                unmatched_leaders.append(leader)
                self.stdout.write(self.style.ERROR(f"Error processing leader {leader}: {e}"))

        return exact_matches, fuzzy_matches, unmatched_leaders
