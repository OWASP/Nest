"""Github app."""

from apps.github.models.organization import Organization
from apps.github.models.release import Release
from apps.github.models.repository import Repository
from apps.github.models.user import User
from apps.github.utils import check_owasp_site_repository, get_node_id


def fetch_repository_data(gh_repository, organization=None, user=None):
    """Fetch GitHub repository data."""
    entity_key = gh_repository.name.lower()
    is_owasp_site_repository = check_owasp_site_repository(entity_key)

    # GitHub repository organization.
    if organization is None:
        gh_organization = gh_repository.organization
        if gh_organization is not None:
            organization_node_id = get_node_id(gh_organization)
            try:
                organization = Organization.objects.get(node_id=organization_node_id)
            except Organization.DoesNotExist:
                organization = Organization(node_id=organization_node_id)
            organization.from_github(gh_organization)

    # GitHub repository owner.
    if user is None:
        gh_user = gh_repository.owner
        # if gh_user is not None:
        user_node_id = get_node_id(gh_user)
        try:
            user = User.objects.get(node_id=user_node_id)
        except User.DoesNotExist:
            user = User(node_id=user_node_id)
        user.from_github(gh_user)
        user.save()

    # GitHub repository.
    commits = gh_repository.get_commits()
    contributors = gh_repository.get_contributors()
    languages = None if is_owasp_site_repository else gh_repository.get_languages()

    repository_node_id = get_node_id(gh_repository)
    try:
        repository = Repository.objects.get(node_id=repository_node_id)
    except Repository.DoesNotExist:
        repository = Repository(node_id=repository_node_id)
    repository.from_github(
        gh_repository,
        commits=commits,
        contributors=contributors,
        languages=languages,
        organization=organization,
        user=user,
    )

    # GitHub repository releases.
    releases = []
    if not is_owasp_site_repository:
        existing_release_node_ids = set(
            Release.objects.filter(repository=repository).values_list("node_id", flat=True)
            if repository.id
            else ()
        )
        for gh_release in gh_repository.get_releases():
            release_node_id = get_node_id(gh_release)
            if release_node_id in existing_release_node_ids:
                break

            # GitHub release author.
            gh_user = gh_release.author
            if gh_user is not None:
                author_node_id = get_node_id(gh_user)
                try:
                    author = User.objects.get(node_id=author_node_id)
                except User.DoesNotExist:
                    author = User(node_id=author_node_id)
                author.from_github(gh_user)
                author.save()

                # if author_node_id not in updated_users:
                #     updated_users.add(author_node_id)
                #     author.from_github(gh_user)
                #     author.save()

            # GitHub release.
            try:
                release = Release.objects.get(node_id=release_node_id)
            except Release.DoesNotExist:
                release = Release(node_id=release_node_id)
            release.from_github(gh_release, author=author, repository=repository)
            releases.append(release)

    return organization, repository, releases
