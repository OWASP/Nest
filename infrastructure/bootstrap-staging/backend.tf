terraform {
  backend "s3" {
    key          = "staging/bootstrap/terraform.tfstate"
    use_lockfile = true
  }
}
