resource "aws_db_subnet_group" "db" {
  name        = "db-subnets"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_db_instance" "pg" {
  identifier              = "pg-main"
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = "db.t4g.micro"
  allocated_storage       = 20
  db_name                 = "autodactyl-db"
  username                = "autodactyl-user"
  password                = random_password.db.result
  db_subnet_group_name    = aws_db_subnet_group.db.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  backup_retention_period = 7
  multi_az                = false
  publicly_accessible     = false
  skip_final_snapshot     = true
}
