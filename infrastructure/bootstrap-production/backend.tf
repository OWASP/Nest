terraform {
  backend "s3" {
    encrypt      = true
    key          = "production/bootstrap/terraform.tfstate"
    use_lockfile = true
  }
}
