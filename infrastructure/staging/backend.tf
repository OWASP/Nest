terraform {
  backend "s3" {
    bucket         = "owasp-nest-terraform-state"
    dynamodb_table = "owasp-nest-terraform-state-lock"
    encrypt        = true
    key            = "staging/terraform.tfstate"
    region         = "us-east-2"
  }
}
