"""GraphQL mutations for mentorship modules in the mentorship app."""

import logging
from datetime import datetime

import strawberry
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from graphql import GraphQLError

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.nodes.module import (
    CreateModuleInput,
    ModuleNode,
    ReorderModulesInput,
    UpdateModuleInput,
)
from apps.mentorship.models import Mentor, Module, Program
from apps.mentorship.models.issue_user_interest import IssueUserInterest
from apps.mentorship.models.task import Task
from apps.nest.api.internal.permissions import IsAuthenticatedAsync
from apps.owasp.models import Project

ASSIGNEE_NOT_FOUND_MSG = "Assignee not found."
DEADLINE_OUT_OF_RANGE_MSG = "Deadline must be within the module's start and end dates."
ISSUE_NOT_FOUND_MSG = "Issue not found in this module."
MODULE_NOT_FOUND_MSG = "Module not found."
NOT_MENTOR_ASSIGN_MSG = "Only mentors of this module can assign issues."
NOT_MENTOR_CLEAR_DEADLINE_MSG = "Only mentors of this module can clear deadlines."
NOT_MENTOR_SET_DEADLINE_MSG = "Only mentors of this module can set deadlines."
NOT_MENTOR_UNASSIGN_MSG = "Only mentors of this module can unassign issues."
NOT_MENTEE_ASSIGNEE_SET_DEADLINE_MSG = "You can only set deadlines for issues assigned to you."

logger = logging.getLogger(__name__)


async def resolve_mentors_from_logins(logins: list[str]) -> set[Mentor]:
    """Resolve a list of GitHub logins to a set of Mentor objects."""
    mentors = set()
    for login in logins:
        try:
            github_user = await GithubUser.objects.aget(login__iexact=login.lower())
            mentor, _ = await Mentor.objects.aget_or_create(github_user=github_user)
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


def _handle_module_save_integrity_error(exc: IntegrityError) -> None:
    """Translate module save IntegrityError to GraphQLError for known constraints."""
    error_message = str(exc)
    if "unique_module_key_in_program" in error_message:
        msg = "This module name already exists in this program."
        raise GraphQLError(
            msg,
            extensions={"code": "VALIDATION_ERROR", "field": "name"},
        ) from exc
    raise exc


@strawberry.type
class ModuleMutation:
    """GraphQL mutations related to the mentorship Module model."""

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def create_module(
        self, info: strawberry.Info, input_data: CreateModuleInput
    ) -> ModuleNode:
        """Create a new mentorship module. User must be an admin of the program."""
        user = await info.context.request.auser()

        try:
            program = await Program.objects.aget(key=input_data.program_key)
            project = await Project.objects.aget(id=input_data.project_id)
        except (Program.DoesNotExist, Project.DoesNotExist) as e:
            msg = f"{e.__class__.__name__} matching query does not exist."
            raise ObjectDoesNotExist(msg) from e

        if not await sync_to_async(program.has_admin)(user):
            raise PermissionDenied

        started_at, ended_at = _validate_module_dates(
            input_data.started_at,
            input_data.ended_at,
            program.started_at,
            program.ended_at,
        )

        try:
            module = await Module.objects.acreate(
                name=input_data.name,
                description=input_data.description,
                experience_level=input_data.experience_level.value,
                started_at=started_at,
                ended_at=ended_at,
                domains=input_data.domains,
                labels=input_data.labels,
                tags=input_data.tags,
                mentee_can_manage_deadlines=input_data.mentee_can_manage_deadlines,
                program=program,
                project=project,
            )
        except IntegrityError as e:
            _handle_module_save_integrity_error(e)

        if module.experience_level not in program.experience_levels:
            program.experience_levels.append(module.experience_level)
            await program.asave(update_fields=["experience_levels"])

        mentors_to_set = await resolve_mentors_from_logins(input_data.mentor_logins or [])
        await module.mentors.aset(list(mentors_to_set))

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def assign_issue_to_user(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
        user_login: str,
    ) -> ModuleNode:
        """Assign an issue to a user by updating Issue.assignees within the module scope."""
        user = await info.context.request.auser()

        module = await (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .afirst()
        )
        if module is None:
            raise ObjectDoesNotExist(MODULE_NOT_FOUND_MSG)

        if not await sync_to_async(module.has_mentor)(user):
            raise PermissionDenied(NOT_MENTOR_ASSIGN_MSG)

        gh_user = await GithubUser.objects.filter(login=user_login).afirst()
        if gh_user is None:
            raise ObjectDoesNotExist(ASSIGNEE_NOT_FOUND_MSG)

        issue = await module.issues.filter(number=issue_number).afirst()
        if issue is None:
            raise ObjectDoesNotExist(ISSUE_NOT_FOUND_MSG)

        await issue.assignees.aadd(gh_user)
        await IssueUserInterest.objects.filter(
            module=module, issue_id=issue.id, user=gh_user
        ).adelete()

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def unassign_issue_from_user(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
        user_login: str,
    ) -> ModuleNode:
        """Unassign an issue from a user by updating Issue.assignees within the module scope."""
        user = await info.context.request.auser()

        module = await (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .afirst()
        )
        if module is None:
            raise ObjectDoesNotExist(MODULE_NOT_FOUND_MSG)

        if not await sync_to_async(module.has_mentor)(user):
            raise PermissionDenied(NOT_MENTOR_UNASSIGN_MSG)

        gh_user = await GithubUser.objects.filter(login=user_login).afirst()
        if gh_user is None:
            raise ObjectDoesNotExist(ASSIGNEE_NOT_FOUND_MSG)

        issue = await module.issues.filter(number=issue_number).afirst()
        if issue is None:
            msg = f"Issue {issue_number} not found in this module."
            raise ObjectDoesNotExist(msg)

        await issue.assignees.aremove(gh_user)

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def set_task_deadline(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
        deadline_at: datetime,
    ) -> ModuleNode:
        """Set a deadline for a task. The user must be a mentor of the module."""
        user = await info.context.request.auser()

        module = await (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .afirst()
        )
        if module is None:
            raise ObjectDoesNotExist(MODULE_NOT_FOUND_MSG)

        is_admin = module.program and await sync_to_async(module.program.has_admin)(user)
        is_mentor = await sync_to_async(module.has_mentor)(user)
        is_mentee = await sync_to_async(module.has_mentee)(user)

        if (
            not is_admin
            and not is_mentor
            and not (is_mentee and module.mentee_can_manage_deadlines)
        ):
            raise PermissionDenied(NOT_MENTOR_SET_DEADLINE_MSG)

        issue = await (
            module.issues.select_related("repository")
            .prefetch_related("assignees")
            .filter(number=issue_number)
            .afirst()
        )
        if issue is None:
            raise ObjectDoesNotExist(ISSUE_NOT_FOUND_MSG)

        assignees = issue.assignees.all()
        if not assignees:
            raise ValidationError(message="Cannot set deadline: issue has no assignees.")

        if is_mentee and not is_mentor and not is_admin:
            github_user = await sync_to_async(getattr)(user, "github_user", None)  # type: ignore[call-arg]
            if github_user is None or not await assignees.filter(id=github_user.id).aexists():
                raise PermissionDenied(NOT_MENTEE_ASSIGNEE_SET_DEADLINE_MSG)

        normalized_deadline = deadline_at
        if timezone.is_naive(normalized_deadline):
            normalized_deadline = timezone.make_aware(normalized_deadline)

        if not module.started_at.date() <= normalized_deadline.date() <= module.ended_at.date():
            raise ValidationError(message=DEADLINE_OUT_OF_RANGE_MSG)

        now = timezone.now()
        tasks_to_update: list[Task] = []
        for assignee in assignees:
            task, _created = await Task.objects.aget_or_create(
                module=module, issue=issue, assignee=assignee
            )
            if task.assigned_at is None:
                task.assigned_at = now
            task.deadline_at = normalized_deadline
            tasks_to_update.append(task)

        await sync_to_async(Task.objects.bulk_update)(
            tasks_to_update, ["assigned_at", "deadline_at"]
        )

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def clear_task_deadline(
        self,
        info: strawberry.Info,
        *,
        module_key: str,
        program_key: str,
        issue_number: int,
    ) -> ModuleNode:
        """Clear the deadline for a task. The user must be a mentor of the module."""
        user = await info.context.request.auser()

        module = await (
            Module.objects.select_related("program")
            .filter(key=module_key, program__key=program_key)
            .afirst()
        )
        if module is None:
            raise ObjectDoesNotExist(MODULE_NOT_FOUND_MSG)

        if not await sync_to_async(module.has_mentor)(user):
            raise PermissionDenied(NOT_MENTOR_CLEAR_DEADLINE_MSG)

        issue = await (
            module.issues.select_related("repository")
            .prefetch_related("assignees")
            .filter(number=issue_number)
            .afirst()
        )
        if issue is None:
            raise ObjectDoesNotExist(ISSUE_NOT_FOUND_MSG)

        assignees = issue.assignees.all()
        if not assignees:
            raise ValidationError(message="Cannot clear deadline: issue has no assignees.")

        tasks_to_update: list[Task] = []
        for assignee in assignees:
            task = await Task.objects.filter(
                module=module, issue=issue, assignee=assignee
            ).afirst()
            if task and task.deadline_at is not None:
                task.deadline_at = None
                tasks_to_update.append(task)

        if len(tasks_to_update) == 1:
            await tasks_to_update[0].asave(update_fields=["deadline_at"])
        elif len(tasks_to_update) > 1:
            await sync_to_async(Task.objects.bulk_update)(tasks_to_update, ["deadline_at"])

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def update_module(
        self, info: strawberry.Info, input_data: UpdateModuleInput
    ) -> ModuleNode:
        """Update an existing mentorship module.

        User must either be:
        - An admin of the program, or
        - A mentor explicitly assigned to this module

        Admins and module mentors can edit any field and manage mentor assignments.
        """
        user = await info.context.request.auser()

        try:
            module = await Module.objects.select_related("program").aget(
                key=input_data.key, program__key=input_data.program_key
            )
        except Module.DoesNotExist as e:
            raise ObjectDoesNotExist(MODULE_NOT_FOUND_MSG) from e

        if not await sync_to_async(module.program.has_admin)(user) and not await sync_to_async(
            module.has_mentor
        )(user):
            msg = "Only admins of the program or mentors of this module can edit modules."
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
            **(
                {"mentee_can_manage_deadlines": input_data.mentee_can_manage_deadlines}
                if input_data.mentee_can_manage_deadlines is not None
                else {}
            ),
        }

        for field, value in field_mapping.items():
            setattr(module, field, value)

        try:
            module.project = await Project.objects.aget(id=input_data.project_id)
        except Project.DoesNotExist as err:
            msg = f"Project with id '{input_data.project_id}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err

        if input_data.mentor_logins is not None:
            mentors_to_set = await resolve_mentors_from_logins(input_data.mentor_logins)
            await module.mentors.aset(mentors_to_set)

        try:
            await module.asave()
        except IntegrityError as e:
            _handle_module_save_integrity_error(e)

        if module.experience_level not in module.program.experience_levels:
            module.program.experience_levels.append(module.experience_level)

        if (
            old_experience_level != module.experience_level
            and old_experience_level in module.program.experience_levels
            and not await Module.objects.filter(
                program=module.program, experience_level=old_experience_level
            )
            .exclude(id=module.id)
            .aexists()
        ):
            module.program.experience_levels.remove(old_experience_level)

        await module.program.asave(update_fields=["experience_levels"])

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def delete_module(
        self,
        info: strawberry.Info,
        program_key: str,
        module_key: str,
    ) -> str:
        """Delete a mentorship module. User must be an admin of the program."""
        user = await info.context.request.auser()

        try:
            module = await Module.objects.select_related("program").aget(
                key=module_key, program__key=program_key
            )
        except Module.DoesNotExist as e:
            raise ObjectDoesNotExist(MODULE_NOT_FOUND_MSG) from e

        if not await sync_to_async(module.program.has_admin)(user):
            msg = "Only program admins can delete modules."
            raise PermissionDenied(msg)

        program = module.program
        module_name = module.name

        experience_level_to_remove = module.experience_level
        if (
            experience_level_to_remove in program.experience_levels
            and not await Module.objects.filter(
                program=program, experience_level=experience_level_to_remove
            )
            .exclude(id=module.id)
            .aexists()
        ):
            program.experience_levels.remove(experience_level_to_remove)
            await program.asave(update_fields=["experience_levels"])

        await module.adelete()

        return f"Module '{module_name}' has been deleted successfully."

    @strawberry.mutation(permission_classes=[IsAuthenticatedAsync])
    async def reorder_modules(
        self, info: strawberry.Info, input_data: ReorderModulesInput
    ) -> list[ModuleNode]:
        """Reorder modules within a program. User must be a program admin."""
        user = await info.context.request.auser()

        try:
            program = await Program.objects.aget(key=input_data.program_key)
        except Program.DoesNotExist as e:
            msg = f"Program with key '{input_data.program_key}' not found."
            raise ObjectDoesNotExist(msg) from e

        if not await sync_to_async(program.has_admin)(user):
            raise PermissionDenied

        if len(set(input_data.module_keys)) != len(input_data.module_keys):
            msg = "Duplicate module keys are not allowed."
            raise ValidationError(msg)

        modules = [
            module
            async for module in Module.objects.filter(
                program=program, key__in=input_data.module_keys
            )
        ]

        if len(modules) != len(input_data.module_keys):
            msg = "Provided module keys do not match the program's modules."
            raise ValidationError(msg)

        key_to_order = {key: idx for idx, key in enumerate(input_data.module_keys)}

        for module in modules:
            module.order = key_to_order[module.key]

        await sync_to_async(Module.objects.bulk_update)(modules, ["order"])

        return [
            module
            async for module in Module.objects.filter(program=program)
            .select_related("program", "project")
            .prefetch_related("mentors__github_user")
            .order_by("order", "started_at")
        ]
