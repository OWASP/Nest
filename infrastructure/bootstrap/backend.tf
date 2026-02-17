terraform {
  backend "s3" {
    encrypt = true
    key     = "bootstrap/terraform.tfstate"
  }
}
