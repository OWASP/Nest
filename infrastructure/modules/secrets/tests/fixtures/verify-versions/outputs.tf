output "credential_versions" {
  description = "Actual AWSCURRENT version identities and fake values after handoff."
  sensitive   = true
  value = { for name, version in data.aws_secretsmanager_secret_version.current : name => {
    version_id = version.version_id
    value      = version.secret_string
  } }
}
