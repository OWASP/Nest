"""A command to update OWASP project health metrics scores."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Update OWASP project health scores."

    def _get_field_weights(self):
        """Return the field weights for scoring calculations."""
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
        return forward_fields, backward_fields

    def _calculate_base_score(self, metric, requirements, forward_fields, backward_fields):
        """Calculate base score before applying any penalties."""
        score = 0.0

        # Forward fields (higher values are better)
        for field, weight in forward_fields.items():
            if int(getattr(metric, field)) >= int(getattr(requirements, field)):
                score += weight

        # Backward fields (lower values are better)
        for field, weight in backward_fields.items():
            if int(getattr(metric, field)) <= int(getattr(requirements, field)):
                score += weight

        return score

    def _apply_compliance_penalty(self, score, metric, requirements):
        """Apply compliance penalty if project is not level compliant."""
        if not metric.project.is_level_compliant:
            penalty_percentage = float(getattr(requirements, "compliance_penalty_weight", 0.0))
            # Clamp to [0, 100]
            penalty_percentage = max(0.0, min(100.0, penalty_percentage))
            penalty_amount = score * (penalty_percentage / 100.0)
            final_score = max(0.0, score - penalty_amount)

            self._log_penalty_applied(
                metric.project.name,
                penalty_percentage,
                penalty_amount,
                final_score,
                metric.project.level,
                metric.project.project_level_official,
            )
            return final_score, True

        return score, False

    def _log_penalty_applied(
        self,
        project_name,
        penalty_percentage,
        penalty_amount,
        final_score,
        local_level,
        official_level,
    ):
        """Log penalty application details."""
        self.stdout.write(
            self.style.WARNING(
                f"Applied {penalty_percentage}% compliance penalty to "
                f"{project_name} (penalty: {penalty_amount:.2f}, "
                f"final score: {final_score:.2f}) [Local: {local_level}, "
                f"Official: {official_level}]"
            )
        )

    def _log_compliance_summary(self, penalties_applied, total_projects_scored):
        """Log final compliance summary."""
        if penalties_applied > 0:
            compliance_rate = (
                (total_projects_scored - penalties_applied) / total_projects_scored * 100
                if total_projects_scored
                else 0
            )
            self.stdout.write(
                self.style.NOTICE(
                    f"Compliance Summary: {penalties_applied}/{total_projects_scored} projects "
                    f"received penalties ({compliance_rate:.1f}% compliant)"
                )
            )

    def handle(self, *args, **options):
        forward_fields, backward_fields = self._get_field_weights()

        project_health_metrics = []
        project_health_requirements = {
            phr.level: phr for phr in ProjectHealthRequirements.objects.all()
        }

        # Compliance tracking
        penalties_applied = 0
        total_projects_scored = 0

        for metric in ProjectHealthMetrics.objects.filter(
            score__isnull=True,
        ).select_related(
            "project",
        ):
            # Calculate the score based on requirements.
            self.stdout.write(
                self.style.NOTICE(f"Updating score for project: {metric.project.name}")
            )

            requirements = project_health_requirements.get(metric.project.level)
            if requirements is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"Missing ProjectHealthRequirements for level '{metric.project.level}' — "
                        f"skipping scoring for {metric.project.name}"
                    )
                )
                continue

            total_projects_scored += 1

            # Calculate base score
            score = self._calculate_base_score(
                metric, requirements, forward_fields, backward_fields
            )

            # Apply compliance penalty if needed
            score, penalty_applied = self._apply_compliance_penalty(score, metric, requirements)
            if penalty_applied:
                penalties_applied += 1

            # Ensure score stays within bounds (0-100)
            metric.score = max(0.0, min(100.0, score))
            project_health_metrics.append(metric)

        ProjectHealthMetrics.bulk_save(
            project_health_metrics,
            fields=[
                "score",
            ],
        )

        # Summary with compliance impact
        self.stdout.write(self.style.SUCCESS("Updated project health scores successfully."))
        self._log_compliance_summary(penalties_applied, total_projects_scored)
