"""A command to generate project metadata YAML files."""

from apps.owasp.management.commands.common.entity_metadata import (
    EntityMetadataBase,
)
from apps.owasp.models.project import Project, ProjectLevel, ProjectType

MIN_PROJECT_TAGS = 3


class Command(EntityMetadataBase):
    help = "Generates and validates project metadata for a given project key."
    model = Project

    def get_metadata(self, project: Project) -> dict:
        """Map the Project model data to a dictionary that matches the schema."""
        level_mapping = {
            ProjectLevel.INCUBATOR: 2,
            ProjectLevel.LAB: 3,
            ProjectLevel.PRODUCTION: 3.5,
            ProjectLevel.FLAGSHIP: 4,
        }
        type_mapping = {
            ProjectType.CODE: "code",
            ProjectType.DOCUMENTATION: "documentation",
            ProjectType.TOOL: "tool",
        }

        data = {
            "audience": project.audience,
            "leaders": [],
            "level": level_mapping.get(project.level),
            "name": project.name,
            "pitch": project.description,
            "type": type_mapping.get(project.type),
        }

        for leader in project.leaders.all():
            person = {}
            if leader.login:
                person["github"] = leader.login
            if leader.name:
                person["name"] = leader.name
            if leader.email:
                person["email"] = leader.email
            data["leaders"].append(person)

        if project.licenses:
            valid_licenses = [
                project_license
                for project_license in project.licenses
                if project_license != "NOASSERTION"
            ]
            if valid_licenses:
                data["license"] = valid_licenses

        if project.repositories.exists():
            data["repositories"] = []
            for repository in project.repositories.all():
                repository_data = {}
                if repository.description:
                    repository_data["description"] = repository.description
                if repository.name:
                    repository_data["name"] = repository.name
                if repository.url:
                    repository_data["url"] = repository.url

                if repository_data:
                    data["repositories"].append(repository_data)

        if project.tags and len(project.tags) >= MIN_PROJECT_TAGS:
            data["tags"] = project.tags

        if project.owasp_url:
            data["website"] = project.owasp_url

        return data
