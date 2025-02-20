"""Project health requirements model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.project import Project

class ProjectHealthRequirements(TimestampedModel):
  """Project health requirements model."""
  class Meta:
    db_table = "owasp_project_health_requirements"
    verbose_name_plural = "Project Health Requirements"
    ordering = ['level']

  level = models.CharField(
    max_length=20,
    choices=Project.ProjectLevel.choices,
    unique=True,
    verbose_name="Project Level"
  )

  contributors_count = models.PositiveIntegerField(verbose_name="Minimum Contributors",default=0)
  creation_days = models.PositiveIntegerField(verbose_name="Minimum Project Age (days)",default=0)
  forks_count = models.PositiveIntegerField(verbose_name="Minimum Forks",default=0)
  last_release_days = models.PositiveIntegerField(verbose_name="Max Days Since Last Release",default=0)
  last_commit_days = models.PositiveIntegerField(verbose_name="Max Days Since Last Commit",default=0)
  open_issues_count = models.PositiveIntegerField(verbose_name="Max Open Issues",default=0)
  open_pull_requests_count = models.PositiveIntegerField(verbose_name="Max Open PRs",default=0)
  owasp_page_update_days = models.PositiveIntegerField(verbose_name="Max Days Since OWASP Update",default=0)
  last_pull_request_days = models.PositiveIntegerField(verbose_name="Max Days Since Last PR",default=0)
  recent_releases_count = models.PositiveIntegerField(verbose_name="Min Recent Releases",default=0)
  recent_releases_window = models.PositiveIntegerField(verbose_name="Recent Releases Window",default=0)
  stars_count = models.PositiveIntegerField(verbose_name="Minimum Stars",default=0)
  total_pull_requests_count = models.PositiveIntegerField(verbose_name="Min Total PRs",default=0)
  total_releases_count = models.PositiveIntegerField(verbose_name="Min Total Releases",default=0)
  unanswered_issues_count = models.PositiveIntegerField(verbose_name="Max Unanswered Issues",default=0)
  unassigned_issues_count = models.PositiveIntegerField(verbose_name="Max Unassigned Issues",default=0)

  def __str__(self):
    """Project health requirements human readable representation."""
    return f"Health Requirements for {self.get_level_display()} Projects"
