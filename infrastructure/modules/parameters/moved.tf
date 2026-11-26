moved {
  from = aws_ssm_parameter.django_algolia_write_api_key
  to   = aws_ssm_parameter.django_algolia_write_api_key[0]
}

moved {
  from = aws_ssm_parameter.django_open_ai_secret_key
  to   = aws_ssm_parameter.django_open_ai_secret_key[0]
}

moved {
  from = aws_ssm_parameter.django_secret_key
  to   = aws_ssm_parameter.django_secret_key[0]
}

moved {
  from = aws_ssm_parameter.django_sentry_dsn
  to   = aws_ssm_parameter.django_sentry_dsn[0]
}

moved {
  from = aws_ssm_parameter.django_slack_bot_token
  to   = aws_ssm_parameter.django_slack_bot_token[0]
}

moved {
  from = aws_ssm_parameter.django_slack_signing_secret
  to   = aws_ssm_parameter.django_slack_signing_secret[0]
}

moved {
  from = aws_ssm_parameter.github_token
  to   = aws_ssm_parameter.github_token[0]
}

moved {
  from = aws_ssm_parameter.next_server_github_client_secret
  to   = aws_ssm_parameter.next_server_github_client_secret[0]
}

moved {
  from = aws_ssm_parameter.nextauth_secret
  to   = aws_ssm_parameter.nextauth_secret[0]
}
