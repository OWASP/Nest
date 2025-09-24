#  VPC and Core Networking 

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-vpc"
    }
  )
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-igw"
    }
  )
}

#  Subnets 

# Deploys a public and private subnet into each specified Availability Zone.

resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-public-subnet-${var.availability_zones[count.index]}"
    }
  )
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-private-subnet-${var.availability_zones[count.index]}"
    }
  )
}

#  Routing and NAT Gateway for Private Subnets 

#  We create a SINGLE NAT Gateway and a SINGLE private route table. This is more
# resilient, cost-effective, and simpler to manage than a per-AZ NAT Gateway.

resource "aws_eip" "nat" {
  # Only one EIP is needed for the single NAT Gateway.
  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-nat-eip"
    }
  )
}

resource "aws_nat_gateway" "main" {
  # Only one NAT Gateway, placed in the first public subnet for simplicity.
  # As AWS automatically handles failover at the infrastructure level.
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-nat-gw"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# A single route table for all public subnets.
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-public-rt"
    }
  )
}

# Associating the single public route table with all public subnets.
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# A single route table for ALL private subnets, pointing to the single NAT Gateway.
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-private-rt"
    }
  )
}

# Associate the single private route table with all private subnets.
resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

#  Application Load Balancer 

resource "aws_security_group" "alb" {
  name        = "${var.project_prefix}-${var.environment}-alb-sg"
  description = "Controls access to the ALB"
  vpc_id      = aws_vpc.main.id


  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic from anywhere for HTTPS redirection"
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS traffic from anywhere"
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-alb-sg"
    }
  )
}

resource "aws_lb" "main" {
  name               = "${var.project_prefix}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  # Deletion protection should be enabled via a variable for production.
  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = merge(
    var.tags,
    {
      Name = "${var.project_prefix}-${var.environment}-alb"
    }
  )
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "404: Not Found. No listener rule configured for this path."
      status_code  = "404"
    }
  }
}