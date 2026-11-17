variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "eu-north-1"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance (Ubuntu 24.04/22.04 LTS for eu-north-1)"
  type        = string
  default     = "ami-0705384c0b33c194c"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of the AWS EC2 Key Pair for SSH access"
  type        = string
  default     = "devops-key"
}

variable "app_name" {
  description = "Application name for tagging and resource naming"
  type        = string
  default     = "optima-practice"
}

variable "app_port" {
  description = "Application HTTP listening port"
  type        = number
  default     = 8000
}
