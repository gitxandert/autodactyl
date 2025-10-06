# Elastic IPs for NAT(s)
resource "aws_eip" "nat" {
  for_each  = var.single_nat_gateway ? { "0" = local.azs[0] } : { for idx, az in local.azs : tostring(idx) => az }
  domain    = "vpc"
  tags      = merge(local.tags, { Name = "nat-eip-${each.value}" })
}

# NAT Gateways live in PUBLIC subnets
resource "aws_nat_gateway" "this" {
  for_each      = aws_eip.nat
  allocation_id = each.value.id
  subnet_id     = aws_subnet.public[tonumber(each.key)].id
  tags          = merge(local.tags, { Name = "nat-${local.azs[tonumber(each.key)]}" })
  depends_on    = [aws_internet_gateway.igw]
}

# one private route table per AZ
resource "aws_route_table" "private" {
  for_each  = aws_subnet.private
  vpc_id    = aws_vpc.main.id
  tags      = merge(local.tags, { Name = "private-rt-${local.azs[tonumber(each.key)]}" })
}

# 0.0.0.0/0 -> NAT for each private RT
resource "aws_route" "private_default" {
  for_each                = aws_route_table.private
  route_table_id          = each.value.id
  destination_cidr_block  = "0.0.0.0/0"
  
  # if single NAT: always use 0; else match per AZ
  nat_gateway_id = var.single_nat_gateway
    ? aws_nat_gateway.this["0"].id
    : aws_nat_gateway.this[tostring(tonumber(each.key))].id
}

resource "aws_route_table_association" "private_assoc" {
  for_each        = aws_subnet.private
  subnet_id       = each.value.id
  route_table_id  = aws_route_table.private[each.key].id
}
