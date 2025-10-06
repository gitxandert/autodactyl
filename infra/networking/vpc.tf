resource "aws_vpc" "main" {
  cidr_block            = var.vpc_cidr
  enable_dns_support    = true
  enable_dns_hostnames  = true
  tags = merge(local.tags, { Name = "main-vpc" })
}

resource "aws_internet_gateway" "igw" {
  vpc_id  = aws_vpc.main.id
  tags    = merge(local.tags, { Name = "main-igw" })
}

resource "aws_cloudwatch_log_group" "vpc_flow" {
  name              = "/aws/vpc/main"
  retention_in_days = 14
  tags              = local.tags
}

resource "aws_flow_log" "this" {
  log_destination_type  = "cloud-watch-logs"
  log_group_name        = aws_cloudwatch_log_group.vpc_flow.name
  traffic_type          = "ALL"
  vpc_id                = aws_vpc.main.id
  iam_role_arn          = aws_iam_role.vpc_flow_logs.arn
}
