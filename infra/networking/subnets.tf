# public
resource "aws_subnet" "public" {
  for_each = { for idx, az in local.azs : idx => {
    az    = az
    cidr  = local.dervied_public[idx]
  } }

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = true
  tags = merge(local.tags, { Name = "public-${each.value.az}" })
}

# private
resource "aws_subnet" "private" {
  for_each = { for idx, az in local.azs : idx => {
    az    = az
    cidr  = local.derived_private[idx]
  } }

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.az
  tags = merge(local.tags, { Name = "private-${each.value.az}" })
}

# route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.tags, { Name = "public-rt" })
}

resource "aws_route" "public_default" {
  route_table_id          = aws_route_table.public.id
  destination_cidr_block  = "0.0.0.0/0"
  gateway_id              = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_assoc" {
  for_each        = aws_subnet.public
  subnet_id       = each.value.id
  route_table_id  = aws_route_table.public.id
}
