resource "aws_instance" "ollama" {
  ami                     = data.aws_ami.ubuntu.id
  instance_type           = "g5.xlarge"
  subnet_id               = aws_subnet.private_a.id
  vpc_security_group_ids  = [aws_security_group.ollama.id]
  iam_instance_profile    = aws_iam_instance_profile.ssm.name
  user_data = <<'EOF'
#!/bin/bash
set -eux
apt-get update
apt-get install -y docker.io
systemctl enable --now docker
docker run -d --restart=always -p 11434:11434 -v /models:/root/.ollama ghcr.io/ollama/ollama:latest
docker exec $(docker ps -qf name=ollama) ollama pull qwen2:7b-instruct
EOF
  root_block_device { volume_size = 200 }
}
