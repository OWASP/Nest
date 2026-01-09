"""Strawberry extensions."""

import hashlib
import json
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from strawberry.extensions import SchemaExtension
from strawberry.permission import PermissionExtension
from strawberry.schema import Schema
from strawberry.utils.str_converters import to_camel_case


@lru_cache(maxsize=1)
def get_protected_fields(schema: Schema) -> tuple[str, ...]:
    """Get protected field names.

    Args:
        schema (Schema): The GraphQL schema.

    Returns:
        tuple[str, ...]: Tuple of protected field names in camelCase.

    """
    query_type = schema.schema_converter.type_map.get("Query")
    fields = getattr(getattr(query_type, "definition", None), "fields", ())
    return tuple(
        to_camel_case(field.name)
        for field in fields
        if any(isinstance(ext, PermissionExtension) for ext in field.extensions)
    )


class CacheExtension(SchemaExtension):
    """CacheExtension class with role-aware caching."""

    ROLE_AWARE_FIELDS = ("getProgram", "getProgramModules")

    def _get_user_role(self, info, field_args: dict) -> str:
        """Determine user role.

        Args:
            info: GraphQL resolver info.
            field_args: Query arguments (may contain programKey).

        Returns:
            str: 'admin' or 'public'

        """
        user = getattr(info.context.request, "user", None)
        program_key = field_args.get("programKey")

        if not user or not user.is_authenticated or not program_key:
            return "public"

        from apps.mentorship.models import Program
        from apps.mentorship.models.mentor import Mentor

        try:
            mentor = Mentor.objects.get(github_user=user.github_user)
            program = Program.objects.prefetch_related("admins", "modules__mentors").get(
                key=program_key
            )
        except (Mentor.DoesNotExist, Program.DoesNotExist):
            return "public"

        if program.admins.filter(id=mentor.id).exists():
            return "admin"

        is_mentor = any(
            module.mentors.filter(id=mentor.id).exists() for module in program.modules.all()
        )
        return "admin" if is_mentor else "public"

    def generate_key(self, field_name: str, field_args: dict, role: str | None = None) -> str:
        """Generate a unique cache key for a query.

        Args:
            field_name (str): The GraphQL field name.
            field_args (dict): The field's arguments.
            role (str | None): User role ('admin' or 'public') for role-aware fields.

        Returns:
            str: The unique cache key.

        """
        cache_data = {"field": field_name, "args": field_args}
        if role:
            cache_data["role"] = role

        key = json.dumps(cache_data, sort_keys=True)
        return (
            f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-{hashlib.sha256(key.encode()).hexdigest()}"
        )

    def resolve(self, _next, root, info, *args, **kwargs):
        """Wrap the resolver to provide role-aware caching."""
        if (
            info.field_name.startswith("__")
            or info.parent_type.name != "Query"
            or info.field_name in get_protected_fields(self.execution_context.schema)
        ):
            return _next(root, info, *args, **kwargs)

        role = None
        if info.field_name in self.ROLE_AWARE_FIELDS:
            role = self._get_user_role(info, kwargs)

        cache_key = self.generate_key(info.field_name, kwargs, role)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        result = _next(root, info, *args, **kwargs)
        cache.set(cache_key, result, settings.GRAPHQL_RESOLVER_CACHE_TIME_SECONDS)
        return result
