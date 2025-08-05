"""A commnad to generate project metadata from project_key."""

from pathlib import Path

import yaml
from django.core.management.base import BaseCommand
from owasp_schema import get_schema
from owasp_schema.utils.schema_validators import validate_data

from apps.owasp.models.project import Project, ProjectLevel, ProjectType


class Command(BaseCommand):
    help = "Generates and validates project metadata for a given project key."

    def add_arguments(self, parser):
        parser.add_argument(
            "project_key",
            type=str,
            help="The key of the project to generate the metadata file.",
        )

    def handle(self, *args, **options):
        project_key = options["project_key"]
        self.stdout.write(f"Attempting to process project: {project_key}")

        project = Project.objects.get(key=project_key)
        if not project:
            self.stderr.write(self.style.ERROR("Project not found."))
            return

        metadata_dict = self.map_data_to_schema(project)

        project_schema = get_schema("project")
        error_message = validate_data(schema=project_schema, data=metadata_dict)

        if error_message:
            self.stderr.write(self.style.ERROR("Validation FAILED!"))
            self.stderr.write(f"Reason: {error_message}")
            return
        self.stdout.write(self.style.SUCCESS("Validation successful!"))

        self.stdout.write("Writing validated data to file...")
        output_dir = Path("schema/data")
        output_file_path = output_dir / "project.owasp.yaml"
        output_dir.mkdir(parents=True, exist_ok=True)

        with Path.open(output_file_path, "w") as f:
            yaml.dump(metadata_dict, f, sort_keys=False, default_flow_style=False, indent=2)
        self.stdout.write(self.style.SUCCESS(f"Successfully generated file: {output_file_path}"))

    def map_data_to_schema(self, project: Project) -> dict:
        """Map the Project model data to a dictionary."""
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
            "name": project.name,
            "pitch": project.description,
            "level": level_mapping.get(project.level),
            "type": type_mapping.get(project.type),
            "audience": "builder",  # Required field with a default value for the PoC.
            "leaders": [],
            "tags": project.tags,
        }

        for leader in project.leaders.all():
            person = {"github": leader.login}
            if leader.name:
                person["name"] = leader.name
            if leader.email:
                person["email"] = leader.email
            data["leaders"].append(person)

        if project.owasp_url:
            data["website"] = project.owasp_url

        if project.repositories.exists():
            data["repositories"] = []
            for repo in project.repositories.all():
                repo_data = {}
                if repo.url:
                    repo_data["url"] = repo.url
                if repo.name:
                    repo_data["name"] = repo.name
                if repo.description:
                    repo_data["description"] = repo.description
                if repo_data:
                    data["repositories"].append(repo_data)

        if project.licenses:
            valid_licenses = [
                project_license
                for project_license in project.licenses
                if project_license != "NOASSERTION"
            ]
            if valid_licenses:
                data["license"] = valid_licenses

        return data
