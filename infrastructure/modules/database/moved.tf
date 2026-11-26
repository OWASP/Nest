moved {
  from = aws_ssm_parameter.django_db_password
  to   = aws_ssm_parameter.django_db_password[0]
}
