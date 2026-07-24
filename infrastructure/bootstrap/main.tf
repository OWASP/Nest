terraform {
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.53.0"
    }
  }
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "part_one" {
  statement {
    sid    = "GlobalDiscovery"
    effect = "Allow"
    actions = [
      "acm:DescribeCertificate",
      "acm:ListCertificates",
      "application-autoscaling:DescribeScalableTargets",
      "application-autoscaling:DescribeScalingActivities",
      "application-autoscaling:DescribeScalingPolicies",
      "ec2:Describe*",
      "ecr:DescribeRepositories",
      "ecr:GetAuthorizationToken",
      "ecs:DescribeTaskDefinition",
      "elasticache:DescribeCacheClusters",
      "elasticache:DescribeCacheSubnetGroups",
      "elasticache:DescribeReplicationGroups",
      "elasticloadbalancing:Describe*",
      "events:ListRuleNamesByTarget",
      "kms:DescribeKey",
      "logs:DescribeLogGroups",
      "rds:DescribeDBInstances",
      "rds:DescribeDBProxies",
      "rds:DescribeDBProxyTargetGroups",
      "rds:DescribeDBProxyTargets",
      "rds:DescribeDBSubnetGroups",
      "secretsmanager:DescribeSecret",
      "ssm:DescribeParameters",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "ACMManagement"
    effect = "Allow"
    actions = [
      "acm:AddTagsToCertificate",
      "acm:DeleteCertificate",
      "acm:ListTagsForCertificate",
      "acm:RemoveTagsFromCertificate",
      "acm:RequestCertificate",
      "acm:ResendValidationEmail",
      "acm:UpdateCertificateOptions",
    ]
    resources = ["arn:aws:acm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:certificate/*"]
  }

  statement {
    sid    = "CWLogsMgmt"
    effect = "Allow"
    actions = [
      "logs:AssociateKmsKey",
      "logs:CreateLogGroup",
      "logs:DeleteLogGroup",
      "logs:DescribeLogStreams",
      "logs:FilterLogEvents",
      "logs:ListTagsForResource",
      "logs:ListTagsLogGroup",
      "logs:PutRetentionPolicy",
      "logs:TagLogGroup",
      "logs:TagResource",
      "logs:UntagLogGroup",
      "logs:UntagResource",
    ]
    resources = ["arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    sid    = "DynamoDBStateLocking"
    effect = "Allow"
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
    ]
    resources = [
      "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/${var.project_name}-${var.environment}-terraform-state-lock",
    ]
  }

  statement {
    sid    = "ElastiCacheMgmt"
    effect = "Allow"
    actions = [
      "elasticache:AddTagsToResource",
      "elasticache:CreateCacheSubnetGroup",
      "elasticache:CreateReplicationGroup",
      "elasticache:DeleteCacheSubnetGroup",
      "elasticache:DeleteReplicationGroup",
      "elasticache:ListTagsForResource",
      "elasticache:ModifyCacheSubnetGroup",
      "elasticache:ModifyReplicationGroup",
      "elasticache:RemoveTagsFromResource",
    ]
    resources = [
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster:${var.project_name}-${var.environment}-*",
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parametergroup:${var.project_name}-${var.environment}-*",
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:replicationgroup:${var.project_name}-${var.environment}-*",
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:subnetgroup:${var.project_name}-${var.environment}-*",
    ]
  }

  statement {
    sid    = "EC2Management"
    effect = "Allow"
    actions = [
      "ec2:AllocateAddress",
      "ec2:AssociateRouteTable",
      "ec2:AttachInternetGateway",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CreateFlowLogs",
      "ec2:CreateInternetGateway",
      "ec2:CreateNatGateway",
      "ec2:CreateNetworkAcl",
      "ec2:CreateNetworkAclEntry",
      "ec2:CreateRoute",
      "ec2:CreateRouteTable",
      "ec2:CreateSecurityGroup",
      "ec2:CreateSubnet",
      "ec2:CreateTags",
      "ec2:CreateVpc",
      "ec2:CreateVpcEndpoint",
      "ec2:DeleteFlowLogs",
      "ec2:DeleteInternetGateway",
      "ec2:DeleteNatGateway",
      "ec2:DeleteNetworkAcl",
      "ec2:DeleteNetworkAclEntry",
      "ec2:DeleteNetworkInterface",
      "ec2:DeleteRoute",
      "ec2:DeleteRouteTable",
      "ec2:DeleteSecurityGroup",
      "ec2:DeleteSubnet",
      "ec2:DeleteTags",
      "ec2:DeleteVpc",
      "ec2:DeleteVpcEndpoints",
      "ec2:DetachInternetGateway",
      "ec2:DisassociateAddress",
      "ec2:DisassociateRouteTable",
      "ec2:ModifySubnetAttribute",
      "ec2:ModifyVpcAttribute",
      "ec2:ModifyVpcEndpoint",
      "ec2:ReleaseAddress",
      "ec2:ReplaceNetworkAclAssociation",
      "ec2:ReplaceNetworkAclEntry",
      "ec2:ReplaceRoute",
      "ec2:ReplaceRouteTableAssociation",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress",
    ]
    resources = ["*"]
  }



  statement {
    sid    = "ECRManagement"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:CreateRepository",
      "ecr:DeleteLifecyclePolicy",
      "ecr:DeleteRepository",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetLifecyclePolicy",
      "ecr:GetRepositoryPolicy",
      "ecr:InitiateLayerUpload",
      "ecr:ListImages",
      "ecr:ListTagsForResource",
      "ecr:PutImage",
      "ecr:PutImageScanningConfiguration",
      "ecr:PutImageTagMutability",
      "ecr:PutLifecyclePolicy",
      "ecr:SetRepositoryPolicy",
      "ecr:TagResource",
      "ecr:UntagResource",
      "ecr:UploadLayerPart",
    ]
    resources = [
      "arn:aws:ecr:*:${data.aws_caller_identity.current.account_id}:repository/${var.project_name}-${var.environment}-*",
    ]
  }

  statement {
    sid    = "ECSClusterManagement"
    effect = "Allow"
    actions = [
      "ecs:CreateCluster",
      "ecs:DeleteCluster",
      "ecs:DescribeClusters",
      "ecs:ListTagsForResource",
      "ecs:PutClusterCapacityProviders",
      "ecs:TagResource",
      "ecs:UntagResource",
      "ecs:UpdateCluster",
    ]
    resources = ["arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${var.project_name}-${var.environment}-*"]
  }

  statement {
    sid    = "ECSOrchestration"
    effect = "Allow"
    actions = [
      "ecs:RunTask",
      "ecs:DescribeTasks",
      "ecs:StopTask",
      "ecs:DescribeServices",
      "ecs:UpdateService"
    ]
    resources = [
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-${var.environment}-*:*",
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:service/${var.project_name}-${var.environment}-*/*",
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${var.project_name}-${var.environment}-*",
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task/${var.project_name}-${var.environment}-*/*"
    ]
  }

  statement {
    sid    = "ECSServiceMgmt"
    effect = "Allow"
    actions = [
      "ecs:CreateService",
      "ecs:DeleteService",
      "ecs:DescribeServices",
      "ecs:UpdateService",
    ]
    resources = ["arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:service/${var.project_name}-${var.environment}-*/*"]
  }

  statement {
    sid    = "ECSTaskDef"
    effect = "Allow"
    actions = [
      "ecs:DescribeTaskDefinition",
      "ecs:TagResource",
    ]
    resources = ["arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-${var.environment}-*:*"]
  }

  statement {
    sid    = "RDSManagement"
    effect = "Allow"
    actions = [
      "rds:AddTagsToResource",
      "rds:CreateDBInstance",
      "rds:CreateDBProxy",
      "rds:CreateDBProxyTargetGroup",
      "rds:CreateDBSubnetGroup",
      "rds:DeleteDBInstance",
      "rds:DeleteDBProxy",
      "rds:DeleteDBProxyTargetGroup",
      "rds:DeleteDBSubnetGroup",
      "rds:DeregisterDBProxyTargets",
      "rds:ListTagsForResource",
      "rds:ModifyDBInstance",
      "rds:ModifyDBProxy",
      "rds:ModifyDBProxyTargetGroup",
      "rds:ModifyDBSubnetGroup",
      "rds:RegisterDBProxyTargets",
      "rds:RemoveTagsFromResource",
    ]
    resources = [
      "arn:aws:rds:${var.aws_region}:${data.aws_caller_identity.current.account_id}:db-proxy:*",
      "arn:aws:rds:${var.aws_region}:${data.aws_caller_identity.current.account_id}:db:${var.project_name}-${var.environment}-*",
      "arn:aws:rds:${var.aws_region}:${data.aws_caller_identity.current.account_id}:subgrp:${var.project_name}-${var.environment}-*",
      "arn:aws:rds:${var.aws_region}:${data.aws_caller_identity.current.account_id}:target-group:${var.project_name}-${var.environment}-*",
    ]
  }
}

data "aws_iam_policy_document" "part_two" {
  statement {
    sid    = "AppAutoscalingMgmt"
    effect = "Allow"
    actions = [
      "application-autoscaling:DeleteScalingPolicy",
      "application-autoscaling:DeregisterScalableTarget",
      "application-autoscaling:ListTagsForResource",
      "application-autoscaling:PutScalingPolicy",
      "application-autoscaling:RegisterScalableTarget",
      "application-autoscaling:TagResource",
      "application-autoscaling:UntagResource",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "IAMCreateECSAutoScalingSLR"
    effect = "Allow"
    actions = [
      "iam:CreateServiceLinkedRole",
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService",
    ]

    condition {
      test     = "StringEquals"
      variable = "iam:AWSServiceName"
      values   = ["ecs.application-autoscaling.amazonaws.com"]
    }
  }

  statement {
    sid    = "CWAutoscalingAlarms"
    effect = "Allow"
    actions = [
      "cloudwatch:DeleteAlarms",
      "cloudwatch:DescribeAlarms",
      "cloudwatch:PutMetricAlarm",
    ]
    resources = [
      "arn:aws:cloudwatch:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alarm:TargetTracking-service/${var.project_name}-${var.environment}-*",
    ]
  }

  statement {
    sid    = "ECSGlobal"
    effect = "Allow"
    actions = [
      "ecs:DeregisterTaskDefinition",
      "ecs:ListClusters",
      "ecs:ListTaskDefinitions",
      "ecs:RegisterTaskDefinition",
    ]
    resources = ["*"]
  }

  statement {
    sid       = "ECSTaskDefinitionTagging"
    effect    = "Allow"
    actions   = ["ecs:TagResource"]
    resources = ["arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-${var.environment}-*:*"]
  }

  statement {
    sid    = "ELBMgmt"
    effect = "Allow"
    actions = [
      "elasticloadbalancing:AddTags",
      "elasticloadbalancing:CreateListener",
      "elasticloadbalancing:CreateLoadBalancer",
      "elasticloadbalancing:CreateRule",
      "elasticloadbalancing:CreateTargetGroup",
      "elasticloadbalancing:DeleteListener",
      "elasticloadbalancing:DeleteLoadBalancer",
      "elasticloadbalancing:DeleteRule",
      "elasticloadbalancing:DeleteTargetGroup",
      "elasticloadbalancing:DeregisterTargets",
      "elasticloadbalancing:ModifyListener",
      "elasticloadbalancing:ModifyListenerAttributes",
      "elasticloadbalancing:ModifyLoadBalancerAttributes",
      "elasticloadbalancing:ModifyRule",
      "elasticloadbalancing:ModifyTargetGroup",
      "elasticloadbalancing:ModifyTargetGroupAttributes",
      "elasticloadbalancing:RegisterTargets",
      "elasticloadbalancing:RemoveTags",
      "elasticloadbalancing:SetRulePriorities",
      "elasticloadbalancing:SetSecurityGroups",
    ]
    resources = [
      "arn:aws:elasticloadbalancing:${var.aws_region}:${data.aws_caller_identity.current.account_id}:loadbalancer/app/${var.project_name}-${var.environment}-*/*",
      "arn:aws:elasticloadbalancing:${var.aws_region}:${data.aws_caller_identity.current.account_id}:targetgroup/${var.project_name}-${var.environment}-*/*",
      "arn:aws:elasticloadbalancing:${var.aws_region}:${data.aws_caller_identity.current.account_id}:listener/app/${var.project_name}-${var.environment}-*/*/*",
      "arn:aws:elasticloadbalancing:${var.aws_region}:${data.aws_caller_identity.current.account_id}:listener-rule/app/${var.project_name}-${var.environment}-*/*/*",
    ]
  }

  statement {
    sid    = "EventBridgeMgmt"
    effect = "Allow"
    actions = [
      "events:DeleteRule",
      "events:DescribeRule",
      "events:ListTagsForResource",
      "events:ListTargetsByRule",
      "events:PutRule",
      "events:PutTargets",
      "events:RemoveTargets",
      "events:TagResource",
      "events:UntagResource",
    ]
    resources = [
      "arn:aws:events:*:${data.aws_caller_identity.current.account_id}:rule/${var.project_name}-${var.environment}-*",
    ]
  }

  statement {
    sid    = "IAMMgmt"
    effect = "Allow"
    actions = [
      "iam:AttachRolePolicy",
      "iam:CreatePolicy",
      "iam:CreatePolicyVersion",
      "iam:CreateRole",
      "iam:DeletePolicy",
      "iam:DeletePolicyVersion",
      "iam:DeleteRole",
      "iam:DeleteRolePolicy",
      "iam:DetachRolePolicy",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAttachedRolePolicies",
      "iam:ListInstanceProfilesForRole",
      "iam:ListPolicyVersions",
      "iam:ListRolePolicies",
      "iam:PutRolePolicy",
      "iam:TagPolicy",
      "iam:TagRole",
      "iam:UntagPolicy",
      "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy",
      "iam:UpdateRole",
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${var.project_name}-${var.environment}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${var.project_name}-*-${var.environment}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-${var.environment}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-*-${var.environment}-*",
    ]
  }

  statement {
    sid    = "IAMPassRole"
    effect = "Allow"
    actions = [
      "iam:PassRole",
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-${var.environment}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-*-${var.environment}-*",
    ]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values = [
        "ecs-tasks.amazonaws.com",
        "events.amazonaws.com",
        "rds.amazonaws.com",
        "vpc-flow-logs.amazonaws.com"
      ]
    }
  }

  statement {
    sid    = "KMSMgmt"
    effect = "Allow"
    actions = [
      "kms:CreateKey",
      "kms:DescribeKey",
      "kms:DisableKeyRotation",
      "kms:EnableKeyRotation",
      "kms:GetKeyPolicy",
      "kms:GetKeyRotationStatus",
      "kms:ListAliases",
      "kms:ListResourceTags",
      "kms:PutKeyPolicy",
      "kms:ScheduleKeyDeletion",
      "kms:TagResource",
      "kms:UntagResource"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "KMSKeyUsageAndPolicy"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey",
      "kms:UpdateKeyDescription",
    ]
    resources = ["*"]

    condition {
      test     = "ForAnyValue:StringEquals"
      variable = "kms:ResourceAliases"
      values = [
        "alias/${var.project_name}-state",
        "alias/${var.project_name}-${var.environment}-state",
        "alias/${var.project_name}-${var.environment}"
      ]
    }
  }

  statement {
    sid    = "KMSAliasManagement"
    effect = "Allow"
    actions = [
      "kms:CreateAlias",
      "kms:DeleteAlias",
      "kms:UpdateAlias"
    ]
    resources = [
      "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alias/${var.project_name}-*",
      "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key/*"
    ]
  }

  statement {
    sid    = "S3Mgmt"
    effect = "Allow"
    actions = [
      "s3:CreateBucket",
      "s3:DeleteBucket",
      "s3:DeleteBucketPolicy",
      "s3:DeleteObject",
      "s3:GetAccelerateConfiguration",
      "s3:GetBucketAcl",
      "s3:GetBucketCors",
      "s3:GetBucketLogging",
      "s3:GetBucketObjectLockConfiguration",
      "s3:GetBucketPolicy",
      "s3:GetBucketPublicAccessBlock",
      "s3:GetBucketRequestPayment",
      "s3:GetBucketTagging",
      "s3:GetBucketVersioning",
      "s3:GetBucketWebsite",
      "s3:GetEncryptionConfiguration",
      "s3:GetLifecycleConfiguration",
      "s3:GetObject",
      "s3:GetReplicationConfiguration",
      "s3:ListBucket",
      "s3:PutBucketLogging",
      "s3:PutBucketObjectLockConfiguration",
      "s3:PutBucketPolicy",
      "s3:PutBucketPublicAccessBlock",
      "s3:PutBucketTagging",
      "s3:PutBucketVersioning",
      "s3:PutEncryptionConfiguration",
      "s3:PutLifecycleConfiguration",
      "s3:PutObject",
    ]
    resources = concat(
      [
        "arn:aws:s3:::${var.project_name}-${var.environment}-*",
        "arn:aws:s3:::${var.project_name}-${var.environment}-*/*",
      ],
      var.environment == "production" ? [
        "arn:aws:s3:::${var.shared_data_bucket_name}",
        "arn:aws:s3:::${var.shared_data_bucket_name}/*",
      ] : []
    )
  }

  dynamic "statement" {
    for_each = var.environment != "production" ? [1] : []
    content {
      sid    = "S3SharedBucketRestricted"
      effect = "Allow"
      actions = [
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket",
      ]
      resources = [
        "arn:aws:s3:::${var.shared_data_bucket_name}",
        "arn:aws:s3:::${var.shared_data_bucket_name}/*",
      ]
    }
  }

  statement {
    sid    = "SecretsManagerMgmt"
    effect = "Allow"
    actions = [
      "secretsmanager:CreateSecret",
      "secretsmanager:DeleteSecret",
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:GetSecretValue",
      "secretsmanager:PutSecretValue",
      "secretsmanager:RestoreSecret",
      "secretsmanager:RotateSecret",
      "secretsmanager:TagResource",
      "secretsmanager:UntagResource",
      "secretsmanager:UpdateSecret",
    ]
    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}-${var.environment}-*",
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:/${var.project_name}/${var.environment}/*",
    ]
  }

  statement {
    sid    = "SSMMgmt"
    effect = "Allow"
    actions = [
      "ssm:AddTagsToResource",
      "ssm:DeleteParameter",
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:ListTagsForResource",
      "ssm:PutParameter",
      "ssm:RemoveTagsFromResource",
    ]
    resources = ["arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/${var.environment}/*"]
  }
}

locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }

  # IAM managed policy size limit in characters
  iam_policy_size_limit = 6144
}

resource "aws_iam_role" "terraform" {
  name = "${var.project_name}-${var.environment}-terraform"
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-terraform"
  })

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = ["sts:AssumeRole"]
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.aws_role_external_id
          }
        }
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${var.project_name}-${var.environment}"
        }
      },
    ]
  })
}

resource "aws_iam_policy" "part_one" {
  name   = "${var.project_name}-${var.environment}-part-one-terraform"
  policy = data.aws_iam_policy_document.part_one.minified_json

  lifecycle {
    precondition {
      condition     = length(data.aws_iam_policy_document.part_one.minified_json) <= local.iam_policy_size_limit
      error_message = "part_one exceeds the IAM managed policy size limit of ${local.iam_policy_size_limit} characters."
    }
  }
}

resource "aws_iam_policy" "part_two" {
  name   = "${var.project_name}-${var.environment}-part-two-terraform"
  policy = data.aws_iam_policy_document.part_two.minified_json

  lifecycle {
    precondition {
      condition     = length(data.aws_iam_policy_document.part_two.minified_json) <= local.iam_policy_size_limit
      error_message = "part_two exceeds the IAM managed policy size limit of ${local.iam_policy_size_limit} characters."
    }
  }
}

resource "aws_iam_role_policy_attachment" "attach_part_one" {
  role       = aws_iam_role.terraform.name
  policy_arn = aws_iam_policy.part_one.arn
}

resource "aws_iam_role_policy_attachment" "attach_part_two" {
  role       = aws_iam_role.terraform.name
  policy_arn = aws_iam_policy.part_two.arn
}
