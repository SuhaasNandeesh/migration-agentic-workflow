# Infrastructure Migration Patterns (Examples)

> These are EXAMPLE patterns, not an exhaustive list. Agents should handle any resource using their training knowledge.

## Compute

| Source Pattern | Target Pattern (Azure) | Notes |
|---------------|----------------------|-------|
| Managed Kubernetes (EKS, GKE) | `azurerm_kubernetes_cluster` | Node pool configs differ per platform |
| Virtual Machines (EC2, Compute Engine) | `azurerm_linux_virtual_machine` | Map instance types to VM SKUs |
| Serverless Functions (Lambda, Cloud Functions) | `azurerm_linux_function_app` | Runtime/trigger mapping needed |
| Container Registry (ECR, GCR) | `azurerm_container_registry` | Single ACR vs multiple source repos |
| Container Instances (ECS, Cloud Run) | `azurerm_container_group` | Or use AKS for production |

## Storage

| Source Pattern | Target Pattern (Azure) | Notes |
|---------------|----------------------|-------|
| Object Storage (S3, GCS) | `azurerm_storage_account` + `azurerm_storage_container` | Different hierarchy model |
| Block Storage (EBS, Persistent Disk) | `azurerm_managed_disk` | Size/performance tier mapping |
| File Storage (EFS, Filestore) | `azurerm_storage_share` | Azure Files or Azure NetApp |
| Archive Storage (Glacier, Archive) | `azurerm_storage_blob` (Archive tier) | Lifecycle policies differ |

## Databases

| Source Pattern | Target Pattern (Azure) | Notes |
|---------------|----------------------|-------|
| Managed PostgreSQL (RDS, Cloud SQL) | `azurerm_postgresql_flexible_server` | Flexible Server is current gen |
| Managed MySQL (RDS, Cloud SQL) | `azurerm_mysql_flexible_server` | |
| Managed SQL Server (RDS) | `azurerm_mssql_server` + `azurerm_mssql_database` | |
| NoSQL Document (DynamoDB, Firestore) | `azurerm_cosmosdb_account` | Select appropriate API |
| Cache (ElastiCache, Memorystore) | `azurerm_redis_cache` | |
| Search (OpenSearch, Elasticsearch) | `azurerm_search_service` | Or self-hosted on AKS |

## Networking

| Source Pattern | Target Pattern (Azure) | Notes |
|---------------|----------------------|-------|
| Virtual Network (VPC, VPC) | `azurerm_virtual_network` | Subnets inline or separate |
| Subnets | `azurerm_subnet` | NSG association is separate |
| Security Groups | `azurerm_network_security_group` | Rule syntax differs |
| Load Balancer (ALB/NLB, HTTP LB) | `azurerm_lb` or `azurerm_application_gateway` | ALB≈AppGW, NLB≈Azure LB |
| CDN (CloudFront, Cloud CDN) | `azurerm_cdn_frontdoor_profile` | Azure Front Door |
| DNS (Route53, Cloud DNS) | `azurerm_dns_zone` + records | |
| VPN Gateway | `azurerm_virtual_network_gateway` | |
| NAT Gateway | `azurerm_nat_gateway` | |
| WAF | `azurerm_web_application_firewall_policy` | |

## Identity & Security

| Source Pattern | Target Pattern (Azure) | Notes |
|---------------|----------------------|-------|
| IAM Roles | `azurerm_role_definition` + `azurerm_role_assignment` | Or use built-in roles |
| IAM Policies | Built into `azurerm_role_definition` | Azure RBAC model differs |
| Service Accounts (IRSA, Workload Identity) | Managed Identity + Federated Credentials | `azurerm_user_assigned_identity` |
| Secrets Manager | `azurerm_key_vault` + `azurerm_key_vault_secret` | |
| KMS / Encryption Keys | `azurerm_key_vault_key` | |
| Certificate Manager | `azurerm_key_vault_certificate` | Or App Service Managed Certs |

## Messaging & Integration

| Source Pattern | Target Pattern (Azure) | Notes |
|---------------|----------------------|-------|
| Message Queue (SQS, Pub/Sub) | `azurerm_servicebus_queue` | |
| Message Topic (SNS, Pub/Sub) | `azurerm_servicebus_topic` | |
| Event Streaming (Kinesis, Dataflow) | `azurerm_eventhub_namespace` | |
| API Gateway | `azurerm_api_management` | |
| Step Functions / Workflows | `azurerm_logic_app_workflow` | |

## Handling Unknown Resources
When you encounter a source resource not in this list:
1. Identify the resource's **function** (what does it do?)
2. Search for an Azure equivalent that serves the same function
3. Set confidence to "low" and document your reasoning
4. The feedback agent will capture this for future reference updates
