terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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

  # Allow SSH (to connect)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP (for the website)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow NodePort (for testing)
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. Create the Server (EC2)
resource "aws_instance" "k8s_server" {
  # Ubuntu 22.04 AMI (Free Tier Eligible)
  ami           = "ami-0c7217cdde317cfec" 
  
  # t3.small is safer for K8s ($0.02/hr). 
  # If you are strictly Free Tier, change to "t2.micro" (but it might crash).
  instance_type = "t3.small" 

  key_name      = aws_key_pair.deployer.key_name
  security_groups = [aws_security_group.k8s_sg.name]

  # This script runs when the server starts (Installs Kubernetes!)
  user_data = <<-EOF
              #!/bin/bash
              # Install K3s (Lightweight Kubernetes)
              curl -sfL https://get.k3s.io | sh -
              
              # Allow the default user to use kubectl
              mkdir -p /home/ubuntu/.kube
              cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
              chown ubuntu:ubuntu /home/ubuntu/.kube/config
              chmod 600 /home/ubuntu/.kube/config
              
              # Install Docker
              apt-get update
              apt-get install -y docker.io
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "DevOps-K8s-Server"
  }
}

# 3. Create a Key Pair (So you can login)
resource "aws_key_pair" "deployer" {
  key_name   = "devops-project-key"
  public_key = file("~/.ssh/id_rsa.pub") # We need to generate this on your laptop first!
}

output "server_ip" {
  value = aws_instance.k8s_server.public_ip
}