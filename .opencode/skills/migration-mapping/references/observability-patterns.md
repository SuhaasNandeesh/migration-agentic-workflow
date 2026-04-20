# Observability Migration Patterns (Examples)

> These patterns cover monitoring, logging, alerting, and tracing tools. Most observability tools are cloud-agnostic.

## Tool Portability Classification

| Tool | Portability | Migration Action |
|------|:-----------:|-----------------|
| Grafana | ✅ Portable | Retain dashboards. Update datasource endpoints. |
| Prometheus | ✅ Portable | Retain rules/alerts. Update scrape targets. |
| Alertmanager | ✅ Portable | Retain configs. Update notification endpoints. |
| Datadog | ✅ Portable | Update cloud integration configs. |
| New Relic | ✅ Portable | Update cloud integration configs. |
| PagerDuty | ✅ Portable | No changes needed. |
| AWS CloudWatch | ❌ Not portable | Replace with Prometheus + Grafana or Azure Monitor |
| AWS X-Ray | ❌ Not portable | Replace with Jaeger, Tempo, or Azure Application Insights |
| GCP Cloud Monitoring | ❌ Not portable | Replace with Prometheus + Grafana or Azure Monitor |

## Grafana Migration
- **Dashboards (JSON):** Export and import — fully portable
- **Datasources:** Update endpoints:
  - AWS datasources → Azure equivalents or Prometheus endpoints
  - CloudWatch datasource → Azure Monitor datasource (if switching)
  - Prometheus → same Prometheus (just update service URL)
- **Alerts:** Grafana alerts are portable. Update notification channels if needed.

## Prometheus Migration
- **Scrape configs:** Update target endpoints to new service addresses
- **Recording rules:** Fully portable — no changes needed
- **Alerting rules:** Fully portable — no changes needed
- **Service discovery:** Update from source platform SD to target:
  - `ec2_sd_configs` → `azure_sd_configs`
  - `gce_sd_configs` → `azure_sd_configs`
  - `kubernetes_sd_configs` → Same (if using K8s SD)
- **Remote write/read:** Update endpoints if using managed Prometheus

## Logging

| Source Tool | Target Options |
|------------|---------------|
| AWS CloudWatch Logs | Azure Log Analytics, Loki, or keep ELK/EFK |
| Fluentd/Fluent Bit | Retain — update output plugin for target |
| ELK Stack (self-hosted) | Retain — just redeploy on target platform |
| Loki | Retain — fully portable |

## General Rules
- Portable tools (Grafana, Prometheus, ELK) → retain and redeploy
- Cloud-specific tools (CloudWatch, X-Ray) → replace with portable or target-native
- Always update service endpoints/addresses
- Always update cloud-specific datasource configs
- Preserve all dashboards, alerts, and rules — they represent operational knowledge
