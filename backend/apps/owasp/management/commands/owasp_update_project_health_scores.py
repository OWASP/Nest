"""A command to update OWASP project health metrics scores."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Update OWASP project health scores."

    def handle(self, *args, **options):
        forward_fields = {
            "age_days": 6.0,
            "contributors_count": 6.0,
            "forks_count": 6.0,
            "is_funding_requirements_compliant": 5.0,
            "is_leader_requirements_compliant": 5.0,
            "open_pull_requests_count": 6.0,
            "recent_releases_count": 6.0,
            "stars_count": 6.0,
            "total_pull_requests_count": 6.0,
            "total_releases_count": 6.0,
        }
        backward_fields = {
            "last_commit_days": 6.0,
            "last_pull_request_days": 6.0,
            "last_release_days": 6.0,
            "open_issues_count": 6.0,
            "owasp_page_last_update_days": 6.0,
            "unanswered_issues_count": 6.0,
            "unassigned_issues_count": 6.0,
        }

        project_health_metrics = []
        project_health_requirements = {
            phr.level: phr for phr in ProjectHealthRequirements.objects.all()
        }
        for metric in ProjectHealthMetrics.objects.filter(
            score__isnull=True,
        ).select_related(
            "project",
        ):
            # Calculate the score based on requirements.
            self.stdout.write(
                self.style.NOTICE(f"Updating score for project: {metric.project.name}")
            )

            requirements = project_health_requirements[metric.project.level]

            score = 0.0
            for field, weight in forward_fields.items():
                if int(getattr(metric, field)) >= int(getattr(requirements, field)):
                    score += weight

            for field, weight in backward_fields.items():
                if int(getattr(metric, field)) <= int(getattr(requirements, field)):
                    score += weight

            # Apply compliance penalty if project is not level compliant
            if not metric.is_level_compliant:
                penalty_percentage = requirements.compliance_penalty_weight
                penalty_amount = score * (penalty_percentage / 100.0)
                score = max(0.0, score - penalty_amount)
                self.stdout.write(
                    self.style.WARNING(
                        f"Applied {penalty_percentage}% compliance penalty to {metric.project.name} "
                        f"(penalty: {penalty_amount:.2f}, final score: {score:.2f})"
                    )
                )

            # Ensure score stays within bounds (0-100)
            metric.score = max(0.0, min(100.0, score))
            project_health_metrics.append(metric)

        ProjectHealthMetrics.bulk_save(
            project_health_metrics,
            fields=[
                "score",
            ],
        )
        self.stdout.write(self.style.SUCCESS("Updated project health scores successfully."))
