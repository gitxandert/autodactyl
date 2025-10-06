resource "aws_lb" "api" {
  name                = "autodactyl-api-alb"
  internal            = true
  load_balancer_type  = "application"
  subnets             = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_groups     = [aws_security_group.alb.id]
}

resource "aws_lb_target_group" "api" {
  name     = "autodactyl-api-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  health_check { path = "/healthz" }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.api.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.cert.arn
  default_action { 
    type = "forward" 
    target_group_arn = aws_lb_target_group.api.arn 
  }
}

