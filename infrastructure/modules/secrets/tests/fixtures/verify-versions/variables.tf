variable "credential_names" {
  description = "Names of the PR1 secrets to read back after cutover."
  type        = map(string)
}
