"""Shared handlers for Slack bot commands and app home functionality."""
import logging

from typing import Optional
from dataclasses import dataclass

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.utils.text import Truncator

from apps.common.constants import NL
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.common.constants import COMMAND_HELP, COMMAND_START
from apps.common.utils import get_absolute_url, natural_date, natural_number
from apps.slack.blocks import markdown
from apps.slack.utils import escape

@dataclass
class EntityPresentation:
    """Configuration for entities presentation"""
    name_truncation: int = 80
    summary_truncation: int = 300
    include_feedback: bool = True
    include_timestamps: bool = True
    include_metadata: bool = True

def chapters_blocks(
    search_query: str = "", 
    limit: int = 10,
    presentation: Optional[EntityPresentation] = None
):
    """chapter block for both commands and app home."""
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.models.chapter import Chapter
    
    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)
    
    attributes = [
        "idx_leaders",
        "idx_name",
        "idx_suggested_location",
        "idx_summary",
        "idx_region",
        "idx_country",
        "idx_updated_at",
        "idx_url",
    ]

    chapters = get_chapters(search_query, attributes=attributes, limit=limit)["hits"]
    if not chapters:
        return [markdown(f"*No chapters found for `{search_query_escaped}`*{NL}" if search_query else "*No chapters found*{NL}")]

    blocks = [
        markdown(
            f"{NL}*OWASP chapters that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP chapters:*{NL}"
        ),
    ]

    for idx, chapter in enumerate(chapters):
        location = chapter["idx_suggested_location"] or chapter["idx_country"]
        leaders = chapter.get("idx_leaders", [])
        leaders_text = (
            f"_Leader{'' if len(leaders) == 1 else 's'}: {', '.join(leaders)}_{NL}"
            if leaders and presentation.include_metadata
            else ""
        )
        
        name = Truncator(escape(chapter["idx_name"])).chars(
            presentation.name_truncation, truncate="..."
        )
        summary = Truncator(chapter["idx_summary"]).chars(
            presentation.summary_truncation, truncate="..."
        )
        
        blocks.append(
            markdown(
                f"{idx + 1}. <{chapter['idx_url']}|*{name}*>{NL}"
                f"_{location}_{NL}"
                f"{leaders_text}"
                f"{escape(summary)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Chapter.active_chapters_count()} OWASP chapters "
                f"is available at <{get_absolute_url('chapters')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )

    return blocks

def projects_blocks(
    search_query: str = "",
    limit: int = 10,
    presentation: Optional[EntityPresentation] = None
):
    """project block for both commands and app home."""
    from apps.owasp.api.search.project import get_projects
    from apps.owasp.models.project import Project
    
    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_contributors_count",
        "idx_forks_count",
        "idx_leaders",
        "idx_level",
        "idx_name",
        "idx_stars_count",
        "idx_summary",
        "idx_updated_at",
        "idx_url",
    ]

    projects = get_projects(search_query, attributes=attributes, limit=limit)["hits"]
    if not projects:
        return [markdown(f"*No projects found for `{search_query_escaped}`*{NL}" if search_query else "*No projects found*{NL}")]

    blocks = [
        markdown(
            f"{NL}*OWASP projects that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP projects:*{NL}"
        ),
    ]

    for idx, project in enumerate(projects):
        name = Truncator(escape(project["idx_name"])).chars(
            presentation.name_truncation, truncate="..."
        )
        summary = Truncator(project["idx_summary"]).chars(
            presentation.summary_truncation, truncate="..."
        )

        metadata = []
        if presentation.include_metadata:
            if project["idx_contributors_count"]:
                metadata.append(f"Contributors: {project['idx_contributors_count']} ")
            if project["idx_forks_count"]:
                metadata.append(f"Forks: {project['idx_forks_count']}")
            if project["idx_stars_count"]:
                metadata.append(f"Stars: {project['idx_stars_count']} ")
        
        metadata_text = f"_{' | '.join(metadata)}_{NL}" if metadata else ""
        
        leaders = project["idx_leaders"]
        leader_text = (
            f"_Leaders: {', '.join(leaders)}_{NL}"
            if leaders and presentation.include_metadata
            else ""
        )

        updated_text = (
            f"_Updated {natural_date(project['idx_updated_at'])}_{NL}"
            if presentation.include_timestamps
            else ""
        )

        blocks.append(
            markdown(
                f"{idx + 1}. <{project['idx_url']}|*{name}*>{NL}"
                f"{updated_text}"
                f"{metadata_text}"
                f"{leader_text}"
                f"{escape(summary)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Project.active_projects_count()} OWASP projects "
                f"is available at <{get_absolute_url('projects')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )

    return blocks

def committees_blocks(
    search_query: str = "",
    limit: int = 10, 
    presentation: Optional[EntityPresentation] = None
):
    """committee block for both commands and app home."""
    from apps.owasp.api.search.committee import get_committees
    from apps.owasp.models.committee import Committee
    
    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = ["idx_leaders", "idx_name", "idx_summary", "idx_url"]
    
    committees = get_committees(search_query, attributes=attributes, limit=limit)["hits"]
    if not committees:
        return [markdown(f"*No committees found for `{search_query_escaped}`*{NL}" if search_query else "*No committees found*{NL}")]

    blocks = [
        markdown(
            f"{NL}*OWASP committees that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP committees:*{NL}"
        ),
    ]

    for idx, committee in enumerate(committees):
        name = Truncator(escape(committee["idx_name"])).chars(
            presentation.name_truncation, truncate="..."
        )
        summary = Truncator(committee["idx_summary"]).chars(
            presentation.summary_truncation, truncate="..."
        )
        
        leaders = committee.get("idx_leaders", [])
        leaders_text = (
            f"_Leader{'' if len(leaders) == 1 else 's'}: {', '.join(leaders)}_{NL}"
            if leaders and presentation.include_metadata
            else ""
        )

        blocks.append(
            markdown(
                f"{idx + 1}. <{committee['idx_url']}|*{name}*>{NL}"
                f"{leaders_text}"
                f"{escape(summary)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Committee.active_committees_count()} OWASP committees "
                f"is available at <{get_absolute_url('committees')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )

    return blocks