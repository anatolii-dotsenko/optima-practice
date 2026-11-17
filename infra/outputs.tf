output "ec2_instance_id" {
  description = "ID of the provisioned EC2 instance"
  value       = aws_instance.app_server.id
}

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.app_server.public_dns
}

output "app_url" {
  description = "Web and API application URL"
  value       = "http://${aws_instance.app_server.public_ip}:${var.app_port}"
}

output "healthcheck_url" {
  description = "Application healthcheck probe URL"
  value       = "http://${aws_instance.app_server.public_ip}:${var.app_port}/health"
}
