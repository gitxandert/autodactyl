resource "aws_cloudfront_vpc_origin" "api" {
  vpc_origin_endpoint_config {
    name                    = "autodactyl-api"
    arn                     = aws_lb.api.arn
    https_port              = 443
    origin_protocol_policy  = "https-only"
    origin_ssl_protocols    = ["TLSv1.2"]
  }

  tags = {
    Name = "autodactyl-api-vpc-origin"
  }
}
