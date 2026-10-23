output "credential_names" {
  description = "Secret names provisioned by the PR1 fixture."
  value = merge(
    { for name, secret in aws_secretsmanager_secret.external_runtime : name => secret.name },
    {
      DJANGO_SECRET_KEY = aws_secretsmanager_secret.django_secret_key.name
      NEXTAUTH_SECRET   = aws_secretsmanager_secret.nextauth_secret.name
    }
  )
}

output "credential_versions" {
  description = "PR1 version identities and fake values for the handoff comparison."
  sensitive   = true
  value = merge(
    { for name, version in aws_secretsmanager_secret_version.external_runtime : name => {
      version_id = version.version_id
      value      = version.secret_string
    } },
    {
      DJANGO_SECRET_KEY = {
        version_id = aws_secretsmanager_secret_version.django_secret_key.version_id
        value      = aws_secretsmanager_secret_version.django_secret_key.secret_string
      }
      NEXTAUTH_SECRET = {
        version_id = aws_secretsmanager_secret_version.nextauth_secret.version_id
        value      = aws_secretsmanager_secret_version.nextauth_secret.secret_string
      }
    }
  )
}
