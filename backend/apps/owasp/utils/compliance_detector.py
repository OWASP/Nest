"""Service for detecting project level compliance issues."""

from __future__ import annotations

import logging

from django.db import transaction

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

logger: logging.Logger = logging.getLogger(__name__)


def detect_and_update_compliance(official_levels: dict[str, str]) -> None:
    """Compare official levels with local levels and update compliance status.
    Args:
        official_levels (dict[str, str]): Dict of project names to official levels.
    """
    logger.info("Starting project level compliance detection")
    # Normalize official levels by stripping whitespace from keys
    normalized_official_levels = {k.strip(): v for k, v in official_levels.items()}
    # Get all active projects
    # Latest metrics already filter to active projects (see get_latest_health_metrics)
    with transaction.atomic():
        # Get latest health metrics for all projects
        latest_metrics = ProjectHealthMetrics.get_latest_health_metrics().select_related("project")
        metrics_to_update = []
        for metric in latest_metrics:
            project = metric.project
            project_name = project.name
            local_level = str(project.level)
            # Compare official level with local level
            # Compare official level with local level
            lookup_name = project_name.strip()
            if lookup_name in normalized_official_levels:
                official_level = normalized_official_levels[lookup_name]
                is_compliant = local_level == official_level

                # Update compliance status if it has changed
                if metric.is_level_compliant != is_compliant:
                    metric.is_level_compliant = is_compliant
                    metrics_to_update.append(metric)
                    logger.info(
                        "Project compliance status changed",
                        extra={
                            "project": project_name,
                            "local_level": local_level,
                            "official_level": official_level,
                            "is_compliant": is_compliant,
                        },
                    )
            # Project not found in official data - mark as non-compliant
            elif metric.is_level_compliant:
                metric.is_level_compliant = False
                metrics_to_update.append(metric)
                logger.warning(
                    "Project not found in official data, marking as non-compliant",
                    extra={"project": project_name, "local_level": local_level},
                )
        # Bulk update compliance status
        if metrics_to_update:
            ProjectHealthMetrics.objects.bulk_update(
                metrics_to_update, ["is_level_compliant"], batch_size=100
            )
            logger.info(
                "Updated compliance status for projects",
                extra={"updated_count": len(metrics_to_update)},
            )
        else:
            logger.info("No compliance status changes needed")