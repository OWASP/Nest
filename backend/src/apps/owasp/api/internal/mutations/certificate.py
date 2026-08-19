"""OWASP Certificate GraphQL Mutations."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction
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


@strawberry.type
class CertificateMutation:
    """GraphQL mutations related to certificates."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def issue_certificate(
        self, info: strawberry.Info, input_data: IssueCertificateInput
    ) -> list[CertificateNode]:
        """Issue generic certificates to one or multiple contributors (project/chapter leaders only)."""
        user = info.context.request.user

        if not user.github_user or (
            not user.github_user.is_project_leader and not user.github_user.chapters.exists()
        ):
            msg = "You must be a project leader or chapter leader to issue certificates."
            logger.warning(
                "Permission denied for user '%s' to issue a certificate.",
                user.username,
            )
            raise PermissionDenied(msg)

        logins = []
        if input_data.recipient_logins:
            logins = [l.strip() for l in input_data.recipient_logins if l and l.strip()]
        elif input_data.recipient_login and input_data.recipient_login.strip():
            logins = [input_data.recipient_login.strip()]

        if not logins:
            msg = "Recipient login cannot be empty."
            raise ValidationError(msg)

        if not input_data.title.strip():
            msg = "Certificate title cannot be empty."
            raise ValidationError(msg)

        if not (input_data.project_key and input_data.project_key.strip()) and not (
            input_data.chapter_key and input_data.chapter_key.strip()
        ):
            msg = "Either project or chapter must be provided."
            raise ValidationError(msg)

        project = None
        chapter = None

        if input_data.project_key:
            clean_p = input_data.project_key.strip()
            try:
                project = Project.objects.get(key=f"www-project-{clean_p.replace('www-project-', '')}")
            except Project.DoesNotExist:
                try:
                    project = Project.objects.get(key=clean_p)
                except Project.DoesNotExist as err:
                    msg = f"Project with key '{input_data.project_key}' not found."
                    raise GraphQLError(
                        msg,
                        extensions={"code": "NOT_FOUND", "field": "projectKey"},
                    ) from err

        if input_data.chapter_key:
            clean_c = input_data.chapter_key.strip()
            try:
                chapter = Chapter.objects.get(key=f"www-chapter-{clean_c.replace('www-chapter-', '')}")
            except Chapter.DoesNotExist:
                try:
                    chapter = Chapter.objects.get(key=clean_c)
                except Chapter.DoesNotExist as err:
                    msg = f"Chapter with key '{input_data.chapter_key}' not found."
                    raise GraphQLError(
                        msg,
                        extensions={"code": "NOT_FOUND", "field": "chapterKey"},
                    ) from err

        certificates = []
        for recipient_login in logins:
            try:
                recipient = GithubUser.objects.get(login__iexact=recipient_login)
            except GithubUser.DoesNotExist as err:
                msg = f"GitHub user '{recipient_login}' not found."
                logger.warning("GitHub user '%s' not found.", recipient_login, exc_info=True)
                raise ObjectDoesNotExist(msg) from err

            certificate = Certificate.objects.create(
                recipient=recipient,
                issuer=user.github_user,
                title=input_data.title.strip(),
                message=input_data.message.strip(),
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
