terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# 1. Create a Security Group (The Firewall)
resource "aws_security_group" "k8s_sg" {
  name        = "k8s-security-group"
  description = "Allow HTTP and SSH"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. GENERATE A NEW KEY (The missing part!)
resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "deployer" {
  key_name   = "devops-project-key-generated" # Changed name to avoid conflict
  public_key = tls_private_key.pk.public_key_openssh
}

# 3. Save the key to a file (Optional, but helpful)
resource "local_file" "ssh_key" {
  filename        = "${path.module}/id_rsa"
  content         = tls_private_key.pk.private_key_pem
  file_permission = "0400"
}

# 4. Create the Server
resource "aws_instance" "k8s_server" {
  ami           = "ami-0c7217cdde317cfec" # Ubuntu 22.04
  instance_type = "t3.small"

  key_name        = aws_key_pair.deployer.key_name
  security_groups = [aws_security_group.k8s_sg.name]

  user_data = <<-EOF
              #!/bin/bash
              curl -sfL https://get.k3s.io | sh -
              mkdir -p /home/ubuntu/.kube
              cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
              chown ubuntu:ubuntu /home/ubuntu/.kube/config
              chmod 600 /home/ubuntu/.kube/config
              apt-get update
              apt-get install -y docker.io
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "DevOps-K8s-Server"
  }
}

# 5. OUTPUTS (This is what you need!)
output "server_ip" {
  value = aws_instance.k8s_server.public_ip
}

output "ssh_private_key" {
  value     = tls_private_key.pk.private_key_pem
  sensitive = true
}