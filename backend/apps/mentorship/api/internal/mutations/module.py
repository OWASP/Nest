"""GraphQL mutations for mentorship modules in the mentorship app."""

import logging
from datetime import datetime

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.nodes.module import (
    CreateModuleInput,
    ModuleNode,
    UpdateModuleInput,
)
from apps.mentorship.models import Mentor, Module, Program
from apps.mentorship.models.issue_user_interest import IssueUserInterest
from apps.mentorship.models.task import Task
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.models import Project

ISSUE_NOT_FOUND_MSG = "Issue not found in this module."
MODULE_NOT_FOUND_MSG = "Module not found."

logger = logging.getLogger(__name__)


def resolve_mentors_from_logins(logins: list[str]) -> set[Mentor]:
    """Resolve a list of GitHub logins to a set of Mentor objects."""
    mentors = set()
    for login in logins:
        try:
            github_user = GithubUser.objects.get(login__iexact=login.lower())
            mentor, _ = Mentor.objects.get_or_create(github_user=github_user)
            mentors.add(mentor)
        except GithubUser.DoesNotExist as e:
            msg = f"GitHub user '{login}' not found."
            logger.warning(msg, exc_info=True)
            raise ValueError(msg) from e
    return mentors


def _validate_module_dates(started_at, ended_at, program_started_at, program_ended_at) -> tuple:
    """Validate and normalize module start/end dates against program constraints."""
    if started_at is None or ended_at is None:
        msg = "Both start and end dates are required."
        raise ValidationError(message=msg)

    if timezone.is_naive(started_at):
        started_at = timezone.make_aware(started_at)
    if timezone.is_naive(ended_at):
        ended_at = timezone.make_aware(ended_at)

    if ended_at <= started_at:
        msg = "End date must be after start date."
        raise ValidationError(message=msg)

    if started_at < program_started_at:
        msg = "Module start date cannot be before program start date."
        raise ValidationError(message=msg)

    if ended_at > program_ended_at:
        msg = "Module end date cannot be after program end date."
        raise ValidationError(message=msg)

    return started_at, ended_at


@strawberry.type
class ModuleMutation:
    """GraphQL mutations related to the mentorship Module model."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_module(self, info: strawberry.Info, input_data: CreateModuleInput) -> ModuleNode:
        """Create a new mentorship module. User must be an admin of the program."""
        user = info.context.request.user

        try:
            program = Program.objects.get(key=input_data.program_key)
            project = Project.objects.get(id=input_data.project_id)
            creator_as_mentor = Mentor.objects.get(nest_user=user)
        except (Program.DoesNotExist, Project.DoesNotExist) as e:
            msg = f"{e.__class__.__name__} matching query does not exist."
            raise ObjectDoesNotExist(msg) from e
        except Mentor.DoesNotExist as e:
            msg = "Only mentors can create modules."
            raise PermissionDenied(msg) from e

        if not program.admins.filter(id=creator_as_mentor.id).exists():
            raise PermissionDenied

        started_at, ended_at = _validate_module_dates(
            input_data.started_at,
            input_data.ended_at,
            program.started_at,
            program.ended_at,
        )

        module = Module.objects.create(
            name=input_data.name,
            description=input_data.description,
            experience_level=input_data.experience_level.value,
            started_at=started_at,
            ended_at=ended_at,
            domains=input_data.domains,
            labels=input_data.labels,
            tags=input_data.tags,
            program=program,
            project=project,
        )

        if module.experience_level not in program.experience_levels:
            program.experience_levels.append(module.experience_level)
            program.save(update_fields=["experience_levels"])

        mentors_to_set = resolve_mentors_from_logins(input_data.mentor_logins or [])
        mentors_to_set.add(creator_as_mentor)
        module.mentors.set(list(mentors_to_set))

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def assign_issue_to_user(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
        user_login: str,
    ) -> ModuleNode:
        """Assign an issue to a user by updating Issue.assignees within the module scope."""
        user = info.context.request.user

        module = (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .first()
        )
        if module is None:
            raise ObjectDoesNotExist(msg=MODULE_NOT_FOUND_MSG)

        mentor = Mentor.objects.filter(nest_user=user).first()
        if mentor is None:
            raise PermissionDenied(msg="Only mentors can assign issues.")
        if not module.program.admins.filter(id=mentor.id).exists():
            raise PermissionDenied

        gh_user = GithubUser.objects.filter(login=user_login).first()
        if gh_user is None:
            raise ObjectDoesNotExist(msg="Assignee not found.")

        issue = module.issues.filter(number=issue_number).first()
        if issue is None:
            raise ObjectDoesNotExist(msg=ISSUE_NOT_FOUND_MSG)

        issue.assignees.add(gh_user)

        IssueUserInterest.objects.filter(module=module, issue_id=issue.id, user=gh_user).delete()

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def unassign_issue_from_user(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
        user_login: str,
    ) -> ModuleNode:
        """Unassign an issue from a user by updating Issue.assignees within the module scope."""
        user = info.context.request.user

        module = (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .first()
        )
        if module is None:
            raise ObjectDoesNotExist(msg=MODULE_NOT_FOUND_MSG)

        mentor = Mentor.objects.filter(nest_user=user).first()
        if mentor is None:
            raise PermissionDenied
        if not module.program.admins.filter(id=mentor.id).exists():
            raise PermissionDenied

        gh_user = GithubUser.objects.filter(login=user_login).first()
        if gh_user is None:
            raise ObjectDoesNotExist(msg="Assignee not found.")

        issue = module.issues.filter(number=issue_number).first()
        if issue is None:
            raise ObjectDoesNotExist(msg=f"Issue {issue_number} not found in this module.")

        issue.assignees.remove(gh_user)

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def set_task_deadline(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
        deadline_at: datetime,
    ) -> ModuleNode:
        """Set a deadline for a task. User must be a mentor and an admin of the program."""
        user = info.context.request.user

        module = (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .first()
        )
        if module is None:
            raise ObjectDoesNotExist(msg=MODULE_NOT_FOUND_MSG)

        mentor = Mentor.objects.filter(nest_user=user).first()
        if mentor is None:
            raise PermissionDenied(msg="Only mentors can set deadlines.")
        if not module.program.admins.filter(id=mentor.id).exists():
            raise PermissionDenied

        issue = (
            module.issues.select_related("repository")
            .prefetch_related("assignees")
            .filter(number=issue_number)
            .first()
        )
        if issue is None:
            raise ObjectDoesNotExist(msg=ISSUE_NOT_FOUND_MSG)

        assignees = issue.assignees.all()
        if not assignees.exists():
            raise ValidationError(message="Cannot set deadline: issue has no assignees.")

        normalized_deadline = deadline_at
        if timezone.is_naive(normalized_deadline):
            normalized_deadline = timezone.make_aware(normalized_deadline)

        if normalized_deadline.date() < timezone.now().date():
            raise ValidationError(message="Deadline cannot be in the past.")

        now = timezone.now()
        tasks_to_update: list[Task] = []
        for assignee in assignees:
            task, _created = Task.objects.get_or_create(
                module=module, issue=issue, assignee=assignee
            )
            if task.assigned_at is None:
                task.assigned_at = now
            task.deadline_at = normalized_deadline
            tasks_to_update.append(task)

        Task.objects.bulk_update(tasks_to_update, ["assigned_at", "deadline_at"])

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def clear_task_deadline(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
    ) -> ModuleNode:
        """Clear the deadline for a task. User must be a mentor and an admin of the program."""
        user = info.context.request.user

        module = (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .first()
        )
        if module is None:
            raise ObjectDoesNotExist(msg=MODULE_NOT_FOUND_MSG)

        mentor = Mentor.objects.filter(nest_user=user).first()
        if mentor is None:
            raise PermissionDenied(msg="Only mentors can clear deadlines.")
        if not module.program.admins.filter(id=mentor.id).exists():
            raise PermissionDenied

        issue = (
            module.issues.select_related("repository")
            .prefetch_related("assignees")
            .filter(number=issue_number)
            .first()
        )
        if issue is None:
            raise ObjectDoesNotExist(msg=ISSUE_NOT_FOUND_MSG)

        assignees = issue.assignees.all()
        if not assignees.exists():
            raise ValidationError(message="Cannot clear deadline: issue has no assignees.")

        tasks_to_update: list[Task] = []
        for assignee in assignees:
            task = Task.objects.filter(module=module, issue=issue, assignee=assignee).first()
            if task and task.deadline_at is not None:
                task.deadline_at = None
                tasks_to_update.append(task)

        if len(tasks_to_update) == 1:
            tasks_to_update[0].save(update_fields=["deadline_at"])
        elif len(tasks_to_update) > 1:
            Task.objects.bulk_update(tasks_to_update, ["deadline_at"])

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def update_module(self, info: strawberry.Info, input_data: UpdateModuleInput) -> ModuleNode:
        """Update an existing mentorship module.

        User must either be:
        - An admin of the program, or
        - A mentor explicitly assigned to this module

        Admins can edit any field and manage mentor assignments.
        Module mentors can edit module details but cannot modify mentor assignments.
        """
        user = info.context.request.user

        try:
            module = Module.objects.select_related("program").get(
                key=input_data.key, program__key=input_data.program_key
            )
        except Module.DoesNotExist as e:
            raise ObjectDoesNotExist(msg=MODULE_NOT_FOUND_MSG) from e

        try:
            editor_as_mentor = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist:
            try:
                github_user = user.github_user
                editor_as_mentor, _ = Mentor.objects.get_or_create(
                    github_user=github_user, defaults={"nest_user": user}
                )
            except Exception as err:
                msg = (
                    f"User '{user.username}' is not registered as a mentor. "
                    "Only mentors can edit modules."
                )
                logger.warning(
                    "Failed to find or create mentor for user '%s' (ID: %s): %s",
                    user.username,
                    user.id,
                    str(err),
                    exc_info=True,
                )
                raise PermissionDenied(msg) from err

        is_program_admin = module.program.admins.filter(id=editor_as_mentor.id).exists()
        is_module_mentor = module.mentors.filter(id=editor_as_mentor.id).exists()

        if not (is_program_admin or is_module_mentor):
            msg = (
                "You do not have permission to edit this module. "
                "Only program admins and module mentors can edit modules."
            )
            logger.warning(
                "Unauthorized edit attempt: User '%s' is neither a program admin "
                "nor a module mentor for module '%s'.",
                user.username,
                module.name,
            )
            raise PermissionDenied(msg)

        started_at, ended_at = _validate_module_dates(
            input_data.started_at,
            input_data.ended_at,
            module.program.started_at,
            module.program.ended_at,
        )

        old_experience_level = module.experience_level

        field_mapping = {
            "name": input_data.name,
            "description": input_data.description,
            "experience_level": input_data.experience_level.value,
            "started_at": started_at,
            "ended_at": ended_at,
            "domains": input_data.domains,
            "labels": input_data.labels,
            "tags": input_data.tags,
        }

        for field, value in field_mapping.items():
            setattr(module, field, value)

        try:
            module.project = Project.objects.get(id=input_data.project_id)
        except Project.DoesNotExist as err:
            msg = f"Project with id '{input_data.project_id}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err

        if input_data.mentor_logins is not None:
            if not is_program_admin:
                msg = "Only program admins can modify mentor assignments."
                logger.warning(
                    "Unauthorized mentor assignment attempt: Non-admin mentor '%s' "
                    "tried to modify mentors for module '%s'.",
                    user.username,
                    module.name,
                )
                raise PermissionDenied(msg)
            mentors_to_set = resolve_mentors_from_logins(input_data.mentor_logins)
            module.mentors.set(mentors_to_set)

        module.save()

        if module.experience_level not in module.program.experience_levels:
            module.program.experience_levels.append(module.experience_level)

        # Remove old experience level if no other module is using it
        if (
            old_experience_level != module.experience_level
            and old_experience_level in module.program.experience_levels
            and not Module.objects.filter(
                program=module.program, experience_level=old_experience_level
            )
            .exclude(id=module.id)
            .exists()
        ):
            module.program.experience_levels.remove(old_experience_level)

        module.program.save(update_fields=["experience_levels"])

        logger.info(
            "User '%s' successfully updated module '%s' in program '%s'.",
            user.username,
            module.name,
            module.program.key,
        )

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def delete_module(
        self,
        info: strawberry.Info,
        program_key: str,
        module_key: str,
    ) -> str:
        """Delete a mentorship module. User must be an admin of the program."""
        user = info.context.request.user

        try:
            module = Module.objects.select_related("program").get(
                key=module_key, program__key=program_key
            )
        except Module.DoesNotExist as e:
            msg = "Module not found."
            raise ObjectDoesNotExist(msg) from e

        try:
            admin_as_mentor = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as err:
            msg = "Only mentors can delete modules."
            logger.warning(
                "User '%s' is not a mentor and cannot delete modules.",
                user.username,
                exc_info=True,
            )
            raise PermissionDenied(msg) from err

        if not module.program.admins.filter(id=admin_as_mentor.id).exists():
            msg = "Only program admins can delete modules."
            raise PermissionDenied(msg)

        program = module.program
        module_name = module.name

        # Clean up experience levels if this module is the only one using it
        experience_level_to_remove = module.experience_level
        if (
            experience_level_to_remove in program.experience_levels
            and not Module.objects.filter(
                program=program, experience_level=experience_level_to_remove
            )
            .exclude(id=module.id)
            .exists()
        ):
            program.experience_levels.remove(experience_level_to_remove)
            program.save(update_fields=["experience_levels"])

        # Delete the module
        module.delete()

        logger.info(
            "User '%s' deleted module '%s' from program '%s'.",
            user.username,
            module_name,
            program_key,
        )

        return f"Module '{module_name}' has been deleted successfully."
