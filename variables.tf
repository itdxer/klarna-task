variable "key_pair_name" {
  description = "The EC2 Key Pair to associate with the EC2 Instance for SSH access."
  type = string
  default = "klarna-task-key"
}
variable "docker_registry" {
  description = "Docker registry (AWS server that stores docker images). The registry should contain the `klarna-task` image"
  type = string
  default = "424261332927.dkr.ecr.eu-central-1.amazonaws.com"
}
