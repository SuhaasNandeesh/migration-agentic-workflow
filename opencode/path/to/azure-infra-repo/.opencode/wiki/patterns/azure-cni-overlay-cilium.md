# Golden Pattern: AKS with Azure CNI Overlay and Cilium

Implementing high-performance, secure networking for Azure Kubernetes Service (AKS) uses **Azure CNI Overlay powered by Cilium**. This combines standard IPAM efficiency (Overlay) with eBPF-based high-throughput networking, network policy enforcement, and Hubble observability.

---

## 1. Core Terraform Blueprint

This module provisions an AKS cluster configured with CNI Overlay and Cilium. It pins network plugin details and enforces a custom pod CIDR block.

```hcl
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = "1.29.2"

  default_node_pool {
    name       = "systempool"
    node_count = var.system_node_count
    vm_size    = var.system_vm_size
    vnet_subnet_id = var.subnet_id
    
    # Enable automatic scaling
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 5
  }

  identity {
    type = "SystemAssigned"
  }

  # Enable OIDC and Workload Identity for security integrations
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    network_dataplane   = "cilium"
    dns_service_ip      = "10.0.0.10"
    service_cidr        = "10.0.0.0/16"
    pod_cidr            = "192.168.0.0/16" # Must not overlap with the host VNet
    
    # Enforce policy engine
    network_policy      = "cilium"
  }

  tags = var.tags
}
```

---

## 2. Kubernetes Cilium Network Policies (eBPF Layer 7 Rules)

By utilizing Cilium as the network dataplane, developers can restrict pod-to-pod traffic at Layer 3, Layer 4, and Layer 7 (e.g. HTTP methods and paths) rather than generic IP ranges.

### Example: L7 microsegmentation for a backend service

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "secure-api-ingress"
  namespace: "production"
spec:
  endpointSelector:
    matchLabels:
      app: backend-api
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend-web
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/public/.*"
        - method: "POST"
          path: "/api/v1/auth/login"
```

---

## 3. Production Rules & Gotchas

* **Host VNet Isolation:** The `pod_cidr` (`192.168.0.0/16`) must never overlap with the address prefixes of the target VNet or any peered virtual networks.
* **Kernel Observability:** Because Cilium uses eBPF in the host kernel, custom tools that monitor legacy `iptables` rules will no longer report AKS container network traffic. All telemetry should be gathered via the **Hubble API** or Azure Advanced Container Networking Services (ACNS).
* **Quota Limits:** Ensure that the host subscription has registered the `Microsoft.ContainerService` provider and there is sufficient IP space in the system node pool subnet for the bridge interfaces.
