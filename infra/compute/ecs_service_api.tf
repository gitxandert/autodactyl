resource "aws_iam_role" "task_exec" {
  name = "ecsTaskExecutionRole"
  assume_role_policty = data.aws_iam_policy_document.ecs_trust.json
}
resource "aws_iam_role_policy_attachment" "exec_attach" {
  role        = aws_iam_role.task_exec.name
  policy_arn  = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "api" {
  family                    = "api"
  network_mode              = "awsvpc"
  requires_compatibilities  = ["FARGATE"]
  cpu                       = 512
  memory                    = 1024
  execution_role_arn        = aws_iam_role.task_exec.arn
  task_role_arn             = aws_iam_role.task_exec.arn

  container_definitions = jsonencode([
    {
      name          = "api"
      image         = "${aws_ecr_repository.api.repository_url}:latest"
      portMappings  = [{ containerPort = 8000, hostPort = 8000 }]
      environment   = [
        { name = "DATABASE_URL",  value = "postgresql://..." },
        { name = "REDIS_URL",     value = "redis://..." },
        { name = "OLLAMA_URL",    value = "http://ollama.internal:11434" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/api"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "api" {
  name            = "api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuratio {
    subnets         = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups = [aws_security_group.api.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn  = aws_lb_target_group.api.arn
    container_name    = "api"
    container_port    = 8000
  }
}
