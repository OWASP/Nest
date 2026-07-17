terraform {
  backend "s3" {
    key          = "production/bootstrap/terraform.tfstate"
    use_lockfile = true
  }
}
