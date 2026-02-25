terraform {
  backend "s3" {
    encrypt = true
    key     = "staging/terraform.tfstate"
  }
}
