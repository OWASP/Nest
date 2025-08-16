"""OWASP admin module initialization."""

from django.contrib import admin

from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

from .award import AwardAdmin
from .chapter import ChapterAdmin
from .committee import CommitteeAdmin
from .event import EventAdmin
from .post import PostAdmin
from .project import ProjectAdmin
from .project_health_metrics import ProjectHealthMetricsAdmin
from .snapshot import SnapshotAdmin
from .sponsor import SponsorAdmin

admin.site.register(ProjectHealthRequirements)
