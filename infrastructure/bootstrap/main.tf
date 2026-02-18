terraform {
  required_version = "1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.22.0"
    }
  }
}

locals {
  common_tags = {
    Environment = "bootstrap"
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }
  environments = toset(var.environments)
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "part_one" {
  for_each = local.environments

  statement {
    sid    = "GlobalDiscovery"
    effect = "Allow"
    actions = [
      "acm:DescribeCertificate",
      "application-autoscaling:DescribeScalableTargets",
      "application-autoscaling:DescribeScalingPolicies",
      "ec2:Describe*",
      "ec2:DescribeFlowLogs",
      "ec2:DescribeNetworkAcls",
      "ecr:DescribeRepositories",
      "ecs:DescribeTaskDefinition",
      "elasticache:DescribeCacheClusters",
      "elasticache:DescribeCacheSubnetGroups",
      "elasticache:DescribeReplicationGroups",
      "elasticloadbalancing:Describe*",
      "events:ListRuleNamesByTarget",
      "kms:DescribeKey",
      "lambda:ListFunctions",
      "lambda:ListVersionsByFunction",
      "logs:DescribeLogGroups",
      "rds:DescribeDBInstances",
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
      "acm:ListCertificates",
      "acm:ListTagsForCertificate",
      "acm:RemoveTagsFromCertificate",
      "acm:RequestCertificate",
      "acm:ResendValidationEmail",
      "acm:UpdateCertificateOptions",
    ]
    resources = ["arn:aws:acm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:certificate/*"]
  }

  statement {
    sid    = "AppAutoscalingManagement"
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
    sid    = "CloudWatchLogsManagement"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:DeleteLogGroup",
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
      "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/${var.project_name}-${each.key}-terraform-state-lock",
    ]
  }

  statement {
    sid    = "ElastiCacheManagement"
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
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster:${var.project_name}-${each.key}-*",
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parametergroup:*",
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:replicationgroup:${var.project_name}-${each.key}-*",
      "arn:aws:elasticache:${var.aws_region}:${data.aws_caller_identity.current.account_id}:subnetgroup:${var.project_name}-${each.key}-*",
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
    sid    = "ECRAuth"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
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
      "ecr:PutLifecyclePolicy",
      "ecr:SetRepositoryPolicy",
      "ecr:TagResource",
      "ecr:UntagResource",
      "ecr:UploadLayerPart",
    ]
    resources = [
      "arn:aws:ecr:*:${data.aws_caller_identity.current.account_id}:repository/${var.project_name}-${each.key}-*",
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
    resources = ["arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${var.project_name}-${each.key}-*"]
  }

  statement {
    sid    = "ECSGlobal"
    effect = "Allow"
    actions = [
      "ecs:DeregisterTaskDefinition",
      "ecs:ListClusters",
      "ecs:ListTaskDefinitions",
      "ecs:RegisterTaskDefinition",
      "ecs:TagResource",
    ]
    resources = ["*"]
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
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-*:*",
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:service/${var.project_name}-*/*",
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${var.project_name}-*",
      "arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task/${var.project_name}-*/*"
    ]
  }

  statement {
    sid    = "ECSServiceManagement"
    effect = "Allow"
    actions = [
      "ecs:CreateService",
      "ecs:DeleteService",
      "ecs:DescribeServices",
      "ecs:UpdateService",
    ]
    resources = ["arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:service/${var.project_name}-${each.key}-*/*"]
  }

  statement {
    sid    = "ECSTaskDefinition"
    effect = "Allow"
    actions = [
      "ecs:DescribeTaskDefinition",
      "ecs:TagResource",
    ]
    resources = ["arn:aws:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:task-definition/${var.project_name}-${each.key}-*:*"]
  }
}

data "aws_iam_policy_document" "part_two" {
  for_each = local.environments

  statement {
    sid    = "ELBManagement"
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
      "elasticloadbalancing:ModifyLoadBalancerAttributes",
      "elasticloadbalancing:ModifyRule",
      "elasticloadbalancing:ModifyTargetGroup",
      "elasticloadbalancing:ModifyTargetGroupAttributes",
      "elasticloadbalancing:RegisterTargets",
      "elasticloadbalancing:RemoveTags",
      "elasticloadbalancing:SetRulePriorities",
      "elasticloadbalancing:SetSecurityGroups",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "EventBridgeManagement"
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
      "arn:aws:events:*:${data.aws_caller_identity.current.account_id}:rule/${var.project_name}-${each.key}-*",
    ]
  }

  statement {
    sid    = "IAMManagement"
    effect = "Allow"
    actions = [
      "iam:AttachRolePolicy",
      "iam:CreatePolicy",
      "iam:CreatePolicyVersion",
      "iam:CreateRole",
      "iam:DeletePolicy",
      "iam:DeletePolicyVersion",
      "iam:DeleteRole",
      "iam:DetachRolePolicy",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
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
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${var.project_name}-${each.key}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${var.project_name}-*-${each.key}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-${each.key}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-*-${each.key}-*",
    ]
  }

  statement {
    sid    = "IAMPassRole"
    effect = "Allow"
    actions = [
      "iam:PassRole",
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-${each.key}-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-*-${each.key}-*",
    ]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values = [
        "ecs-tasks.amazonaws.com",
        "events.amazonaws.com",
        "lambda.amazonaws.com",
        "rds.amazonaws.com",
        "vpc-flow-logs.amazonaws.com"
      ]
    }
  }

  statement {
    sid    = "KMSManagement"
    effect = "Allow"
    actions = [
      "kms:CreateKey",
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
      "kms:GenerateDataKey",
      "kms:UpdateKeyDescription",
    ]
    resources = ["*"]

    condition {
      test     = "ForAnyValue:StringEquals"
      variable = "kms:ResourceAliases"
      values = [
        "alias/${var.project_name}-backend",
        "alias/${var.project_name}-${each.key}"
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
    sid    = "LambdaManagement"
    effect = "Allow"
    actions = [
      "lambda:AddPermission",
      "lambda:CreateAlias",
      "lambda:CreateFunction",
      "lambda:DeleteAlias",
      "lambda:DeleteFunction",
      "lambda:DeleteFunctionConcurrency",
      "lambda:GetAlias",
      "lambda:GetFunction",
      "lambda:GetFunctionCodeSigningConfig",
      "lambda:GetFunctionConcurrency",
      "lambda:GetFunctionConfiguration",
      "lambda:GetFunctionUrlConfig",
      "lambda:GetPolicy",
      "lambda:InvokeFunction",
      "lambda:ListFunctionUrlConfigs",
      "lambda:ListTags",
      "lambda:ListVersionsByFunction",
      "lambda:PublishVersion",
      "lambda:PutFunctionConcurrency",
      "lambda:RemovePermission",
      "lambda:TagResource",
      "lambda:UntagResource",
      "lambda:UpdateAlias",
      "lambda:UpdateFunctionCode",
      "lambda:UpdateFunctionConfiguration",
    ]
    resources = [
      "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-${each.key}",
      "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-${each.key}:*",
    ]
  }

  statement {
    sid    = "RDSManagement"
    effect = "Allow"
    actions = [
      "rds:AddTagsToResource",
      "rds:CreateDBInstance",
      "rds:CreateDBSubnetGroup",
      "rds:DeleteDBInstance",
      "rds:DeleteDBSubnetGroup",
      "rds:ListTagsForResource",
      "rds:ModifyDBInstance",
      "rds:ModifyDBSubnetGroup",
      "rds:RemoveTagsFromResource",
    ]
    resources = [
      "arn:aws:rds:${var.aws_region}:${data.aws_caller_identity.current.account_id}:db:${var.project_name}-${each.key}-*",
      "arn:aws:rds:${var.aws_region}:${data.aws_caller_identity.current.account_id}:subgrp:${var.project_name}-${each.key}-*"
    ]
  }

  statement {
    sid    = "S3Management"
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
      "s3:GetBucketOwnershipControls",
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
      "s3:ListBucketVersions",
      "s3:PutBucketAcl",
      "s3:PutBucketLogging",
      "s3:PutBucketObjectLockConfiguration",
      "s3:PutBucketOwnershipControls",
      "s3:PutBucketPolicy",
      "s3:PutBucketPublicAccessBlock",
      "s3:PutBucketTagging",
      "s3:PutBucketVersioning",
      "s3:PutEncryptionConfiguration",
      "s3:PutLifecycleConfiguration",
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${var.project_name}-${each.key}-*",
      "arn:aws:s3:::${var.project_name}-${each.key}*/*",
    ]
  }

  statement {
    sid    = "SecretsManagerManagement"
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
    resources = ["arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}-${each.key}-*"]
  }

  statement {
    sid    = "SSMManagement"
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
    resources = ["arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/${each.key}/*"]
  }
}

resource "aws_iam_role" "terraform" {
  for_each = local.environments

  name = "${var.project_name}-${each.key}-terraform"
  tags = merge(local.common_tags, {
    Environment = each.key
    Name        = "${var.project_name}-${each.key}-terraform"
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
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${var.project_name}-${each.key}"
        }
      },
    ]
  })
}

resource "aws_iam_policy" "part_one" {
  for_each = local.environments
  name     = "${var.project_name}-${each.key}-part-one-terraform"
  policy   = data.aws_iam_policy_document.part_one[each.key].json
}

resource "aws_iam_policy" "part_two" {
  for_each = local.environments
  name     = "${var.project_name}-${each.key}-part-two-terraform"
  policy   = data.aws_iam_policy_document.part_two[each.key].json
}

resource "aws_iam_role_policy_attachment" "attach_part_one" {
  for_each   = local.environments
  role       = aws_iam_role.terraform[each.key].name
  policy_arn = aws_iam_policy.part_one[each.key].arn
}

resource "aws_iam_role_policy_attachment" "attach_part_two" {
  for_each   = local.environments
  role       = aws_iam_role.terraform[each.key].name
  policy_arn = aws_iam_policy.part_two[each.key].arn
}
