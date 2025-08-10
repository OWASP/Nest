"""A command to generate project metadata YAML files."""

from apps.owasp.management.commands.base_generate_metadata import BaseGenerateMetadataCommand
from apps.owasp.models.project import Project, ProjectLevel, ProjectType

MIN_PROJECT_TAGS = 3


class Command(BaseGenerateMetadataCommand):
    help = "Generates and validates project metadata for a given project key."
    model = Project
    schema_name = "project"

    def map_data_to_schema(self, project: Project) -> dict:
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
            for repo in project.repositories.all():
                repo_data = {}
                if repo.description:
                    repo_data["description"] = repo.description
                if repo.name:
                    repo_data["name"] = repo.name
                if repo.url:
                    repo_data["url"] = repo.url
                if repo_data:
                    data["repositories"].append(repo_data)

        if project.tags and len(project.tags) >= MIN_PROJECT_TAGS:
            data["tags"] = project.tags

        if project.owasp_url:
            data["website"] = project.owasp_url

        return data
