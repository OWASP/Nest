terraform {
  backend "s3" {
    encrypt      = true
    key          = "staging/bootstrap/terraform.tfstate"
    use_lockfile = true
  }
}
