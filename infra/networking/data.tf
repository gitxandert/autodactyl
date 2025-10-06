data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)

  derived_public  = length(var.public_subnet_cidrs) > 0 ? var.public_subnet_cidrs : [for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, i)]
  
  derived_private = length(var.private_subnet_cidrs) > 0 ? var.private_subnet_cidrs : [for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, i + 100)]

  tags = var.tags
}
