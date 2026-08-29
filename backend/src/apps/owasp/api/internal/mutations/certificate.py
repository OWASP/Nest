"""OWASP Certificate GraphQL Mutations."""

import logging
import operator
from functools import reduce

import strawberry
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from graphql import GraphQLError

from apps.github.models.user import User as GithubUser
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.certificate import CertificateNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.crp.certificate import Certificate
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)


@strawberry.input
class IssueCertificateInput:
    """Input type for issuing a certificate."""

    recipient_login: str | None = None
    recipient_logins: list[str] | None = None
    title: str
    message: str = ""
    project_key: str | None = None
    chapter_key: str | None = None


MAX_TITLE_LENGTH = 50
MAX_MESSAGE_LENGTH = 280


@strawberry.type
class CertificateMutation:
    """GraphQL mutations related to certificates."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def issue_certificate(
        self, info: strawberry.Info, input_data: IssueCertificateInput
    ) -> list[CertificateNode]:
        """Issue generic certificates to contributors (project or chapter leaders only)."""
        user = info.context.request.user
        github_user = getattr(user, "github_user", None)

        if not github_user or (
            not github_user.is_project_leader and not github_user.chapters.exists()
        ):
            msg = "You must be a project leader or chapter leader to issue certificates."
            logger.warning(
                "Permission denied for user '%s' to issue a certificate.",
                user.username,
            )
            raise PermissionDenied(msg)

        logins = []
        if input_data.recipient_logins:
            seen_logins = set()
            for raw_login in input_data.recipient_logins:
                if raw_login and (clean_login := raw_login.strip()):
                    lower_login = clean_login.lower()
                    if lower_login not in seen_logins:
                        seen_logins.add(lower_login)
                        logins.append(clean_login)
        elif input_data.recipient_login and input_data.recipient_login.strip():
            logins = [input_data.recipient_login.strip()]

        if not logins:
            msg = "Recipient login cannot be empty."
            raise ValidationError(msg)

        title = input_data.title.strip()
        if not title:
            msg = "Certificate title cannot be empty."
            raise ValidationError(msg)

        if len(title) > MAX_TITLE_LENGTH:
            msg = f"Certificate title cannot exceed {MAX_TITLE_LENGTH} characters."
            raise ValidationError(msg)

        message = input_data.message.strip()
        if len(message) > MAX_MESSAGE_LENGTH:
            msg = f"Certificate body message cannot exceed {MAX_MESSAGE_LENGTH} characters."
            raise ValidationError(msg)

        clean_project_key = (
            input_data.project_key.strip().removeprefix("www-project-")
            if input_data.project_key and input_data.project_key.strip()
            else None
        )
        clean_chapter_key = (
            input_data.chapter_key.strip().removeprefix("www-chapter-")
            if input_data.chapter_key and input_data.chapter_key.strip()
            else None
        )

        if clean_project_key and clean_chapter_key:
            msg = "Provide either project or chapter, not both."
            raise ValidationError(msg)

        if not clean_project_key and not clean_chapter_key:
            msg = "Either project or chapter must be provided."
            raise ValidationError(msg)

        project = None
        chapter = None

        if clean_project_key:
            try:
                project = Project.objects.get(key=f"www-project-{clean_project_key}")
            except Project.DoesNotExist as err:
                msg = f"Project with key '{input_data.project_key}' not found."
                raise GraphQLError(
                    msg,
                    extensions={"code": "NOT_FOUND", "field": "projectKey"},
                ) from err

        if clean_chapter_key:
            try:
                chapter = Chapter.objects.get(key=f"www-chapter-{clean_chapter_key}")
            except Chapter.DoesNotExist as err:
                msg = f"Chapter with key '{input_data.chapter_key}' not found."
                raise GraphQLError(
                    msg,
                    extensions={"code": "NOT_FOUND", "field": "chapterKey"},
                ) from err

        filter_q = reduce(operator.or_, (Q(login__iexact=login_name) for login_name in logins))
        recipients = GithubUser.objects.filter(filter_q)
        found = {r.login.lower(): r for r in recipients}

        missing = [login_name for login_name in logins if login_name.lower() not in found]
        if missing:
            msg = (
                f"GitHub user '{missing[0]}' not found."
                if len(missing) == 1
                else f"GitHub users not found: {', '.join(missing)}."
            )
            logger.warning("GitHub user(s) not found: %s", ", ".join(missing))
            raise GraphQLError(
                msg,
                extensions={"code": "NOT_FOUND", "field": "recipientLogins"},
            )

        certificates = []
        for recipient_login in logins:
            recipient = found[recipient_login.lower()]
            certificate = Certificate.objects.create(
                recipient=recipient,
                issuer=github_user,
                title=title,
                message=message,
                project=project,
                chapter=chapter,
            )
            certificates.append(certificate)

            logger.info(
                "User '%s' issued certificate '%s' to '%s'.",
                user.username,
                certificate.title,
                recipient.login,
            )

        return certificates
