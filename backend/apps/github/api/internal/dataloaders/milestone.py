"""DataLoaders for milestones."""

from collections import defaultdict

from django.db.models import Prefetch
from strawberry.dataloader import DataLoader

from apps.github.models.milestone import Milestone
from apps.mentorship.models.program import Program

RECENT_MILESTONES_BY_PROGRAM_ID = "recent_milestones_by_program_id"


async def load_recent_milestones_by_program_id(program_ids: list[int]) -> list[list[Milestone]]:
    """Batch-load interested users for the given issue IDs in a single query."""
    milestones = (
        Milestone.open_milestones.filter(
            repository__project__in=Program.objects.filter(pk__in=program_ids).values_list(
                "modules__project_id", flat=True
            )
        )
        .select_related(
            "repository__organization",
            "author",
        )
        .prefetch_related(
            Prefetch(
                "repository__project_set__module_set__program",
                queryset=Program.objects.only("pk"),
                to_attr="prefetched_program",
            ),
        )
        .order_by("-created_at")
        .distinct()
    )

    mapping: dict[int, list[Milestone]] = defaultdict(list)
    async for milestone in milestones:
        seen_program_ids = set()
        for project in milestone.repository.project_set.all():
            for module in project.module_set.all():
                if module.prefetched_program.pk not in seen_program_ids:
                    mapping[module.prefetched_program.pk].append(milestone)
                    seen_program_ids.add(module.prefetched_program.pk)

    return [mapping.get(program_id, []) for program_id in program_ids]


def get_milestone_loaders() -> dict[str, DataLoader[int, list[Milestone]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        RECENT_MILESTONES_BY_PROGRAM_ID: DataLoader[int, list[Milestone]](
            load_fn=load_recent_milestones_by_program_id,
        ),
    }
