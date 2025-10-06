resource "aws_elasticache_subnet_group" "redis" {
  name        = "redis-subnets"
  subnet_ids  = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_elasticache_replication_group" "rg" {
  replication_group_id        = "autodactyl-redis"
  engine                      = "redis"
  engine_version              = "7.1"
  automatic_failover_enabled  = true
  node_type                   = "cache.t4g.micro"
  number_cache_clusters       = 2
  subnet_group_name           = aws_elasticache_subnet_group.redis.name
  security_group_ids          = [aws_security_group.redis.id]
}
