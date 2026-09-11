"""OWASP Certificate GraphQL Mutations."""

import logging
from typing import Annotated

import strawberry
from django.db import transaction
from django.db.models import Q
from graphql import GraphQLError
from pydantic import BaseModel, StringConstraints, ValidationError, model_validator

from apps.github.models.user import User as GithubUser
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.certificate import CertificateNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.crp.certificate import Certificate
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 280
MAX_TITLE_LENGTH = 50


class IssueCertificateSchema(BaseModel):
    """Pydantic schema for validating certificate issuance input."""

    recipient_login: str | None = None
    recipient_logins: list[str] | None = None
    title: Annotated[
        str, StringConstraints(min_length=1, max_length=MAX_TITLE_LENGTH, strip_whitespace=True)
    ]
    message: Annotated[
        str, StringConstraints(max_length=MAX_MESSAGE_LENGTH, strip_whitespace=True)
    ] = ""
    project_key: str | None = None
    chapter_key: str | None = None

    @model_validator(mode="after")
    def validate_recipients_and_keys(self) -> "IssueCertificateSchema":
        """Deduplicate logins and validate project/chapter keys."""
        logins: list[str] = []
        if self.recipient_logins:
            seen: set[str] = set()
            for raw in self.recipient_logins:
                clean = (raw or "").strip()
                if clean and clean.lower() not in seen:
                    seen.add(clean.lower())
                    logins.append(clean)
        elif self.recipient_login and self.recipient_login.strip():
            logins = [self.recipient_login.strip()]

        if not logins:
            msg = "Recipient login cannot be empty."
            raise ValueError(msg)
        self.recipient_logins = logins

        self.project_key = (
            self.project_key.strip().removeprefix("www-project-")
            if self.project_key and self.project_key.strip()
            else None
        )
        self.chapter_key = (
            self.chapter_key.strip().removeprefix("www-chapter-")
            if self.chapter_key and self.chapter_key.strip()
            else None
        )

        if self.project_key and self.chapter_key:
            msg = "Provide either project or chapter, not both."
            raise ValueError(msg)
        if not self.project_key and not self.chapter_key:
            msg = "Either project or chapter must be provided."
            raise ValueError(msg)

        return self


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
        """Issue generic certificates to contributors (project or chapter leaders only)."""
        user = info.context.request.user
        github_user = getattr(user, "github_user", None)

        if not github_user or (
            not github_user.is_project_leader and not github_user.chapters.exists()
        ):
            msg = "You must be a project leader or chapter leader to issue certificates."
            raise GraphQLError(msg, extensions={"code": "FORBIDDEN"})

        try:
            validated = IssueCertificateSchema(
                chapter_key=input_data.chapter_key,
                message=input_data.message,
                project_key=input_data.project_key,
                recipient_login=input_data.recipient_login,
                recipient_logins=input_data.recipient_logins,
                title=input_data.title,
            )
        except ValidationError as exc:
            first_error = exc.errors()[0]
            raise GraphQLError(
                first_error["msg"],
                extensions={"code": "VALIDATION_ERROR"},
            ) from exc

        project = None
        chapter = None

        if validated.project_key:
            try:
                project = Project.objects.get(key=f"www-project-{validated.project_key}")
            except Project.DoesNotExist as err:
                msg = f"Project with key '{input_data.project_key}' not found."
                raise GraphQLError(
                    msg,
                    extensions={"code": "NOT_FOUND", "field": "projectKey"},
                ) from err

        if validated.chapter_key:
            try:
                chapter = Chapter.objects.get(key=f"www-chapter-{validated.chapter_key}")
            except Chapter.DoesNotExist as err:
                msg = f"Chapter with key '{input_data.chapter_key}' not found."
                raise GraphQLError(
                    msg,
                    extensions={"code": "NOT_FOUND", "field": "chapterKey"},
                ) from err

        logins = validated.recipient_logins or []
        filter_q = Q()
        for login_name in logins:
            filter_q |= Q(login__iexact=login_name)

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
                title=validated.title,
                message=validated.message,
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
