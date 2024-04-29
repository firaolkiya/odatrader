# OdaTrade AWS Infrastructure (ECS Fargate + RDS + ElastiCache)

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "production"
}

# VPC
resource "aws_vpc" "odatrade" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "odatrade-vpc", Environment = var.environment }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.odatrade.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "odatrade-public-${count.index}" }
}

data "aws_availability_zones" "available" {}

# RDS PostgreSQL
resource "aws_db_instance" "odatrade" {
  identifier        = "odatrade-db"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  db_name           = "odatrade"
  username          = "odatrade"
  password          = var.db_password
  skip_final_snapshot = true
  tags = { Name = "odatrade-postgres", Environment = var.environment }
}

variable "db_password" {
  type      = string
  sensitive = true
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "odatrade" {
  cluster_id           = "odatrade-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  tags = { Name = "odatrade-redis", Environment = var.environment }
}

# ECS Cluster
resource "aws_ecs_cluster" "odatrade" {
  name = "odatrade-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECR Repositories
resource "aws_ecr_repository" "api" {
  name = "odatrade-api"
}

resource "aws_ecr_repository" "bot" {
  name = "odatrade-bot"
}

output "rds_endpoint" {
  value = aws_db_instance.odatrade.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.odatrade.cache_nodes[0].address
}

output "ecs_cluster" {
  value = aws_ecs_cluster.odatrade.name
}
