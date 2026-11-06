moved {
  from = aws_ssm_parameter.django_redis_password
  to   = aws_ssm_parameter.django_redis_password[0]
}
