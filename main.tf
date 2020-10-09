provider "aws" {
  region = "eu-central-1"
}
resource "aws_instance" "rest_api_prod" {
  ami = "ami-0c960b947cbb2dd16"
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.security_group.id]
  key_name = var.key_pair_name
  associate_public_ip_address = true
  iam_instance_profile = aws_iam_instance_profile.profile.name

  tags = {
    Name = "klarna-task-rest-api"
  }

  connection {
    type = "ssh"
    user = "ubuntu"
    private_key = file("~/.ssh/${var.key_pair_name}.pem")
    host = aws_instance.rest_api_prod.public_ip
  }

  provisioner "file" {
    source = "docker-compose.yaml"
    destination = "/home/ubuntu/docker-compose.yaml"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt update",
      "sudo snap install docker",
      "sudo apt install -y awscli",
      "sudo curl -L \"https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
      "sudo chmod +x /usr/local/bin/docker-compose",
      "sudo $(aws ecr get-login --no-include-email --region eu-central-1)",
      "sudo docker pull 424261332927.dkr.ecr.eu-central-1.amazonaws.com/klarna-task",
      "sudo docker-compose up rest-api-prod &",
    ]
  }
}
resource "aws_security_group" "security_group" {
  name = "klarna-task-security-group"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = "80"
    to_port = "80"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "role" {
  name = "klarna-role"
  assume_role_policy = file("ops/role-policy.json")
}

resource "aws_iam_policy" "policy" {
  name = "klarna-policy"
  policy = file("ops/policy.json")
}

resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}
resource "aws_iam_instance_profile" "profile" {
  name = "klarna-profile"
  role = aws_iam_role.role.name
}
