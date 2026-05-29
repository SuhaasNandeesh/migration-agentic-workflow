# Gotcha: Cosmos DB throughput is Request Units (RU/s), not capacity

Unlike DynamoDB's read/write capacity units, Cosmos DB bills and throttles on
**Request Units per second (RU/s)** shared by all operations:

- Under-provisioned RU/s → HTTP **429 "Request rate too large"** (throttling),
  which surfaces as intermittent app failures, not a deploy error.
- Throughput is set at the database or container level (`throughput` for manual,
  or `autoscale_settings { max_throughput }` for autoscale).

## Fix / guidance
- Prefer **autoscale** for migrated workloads with unknown patterns:
  `autoscale_settings { max_throughput = 4000 }` (scales 10%–100% of max).
- Don't map DynamoDB capacity numbers 1:1 — RU/s ≈ (item size × ops/s × factor);
  start with autoscale and tune from Azure Monitor metrics.
- Minimum is 400 RU/s (manual) / 1000 max (autoscale) per container.
- Choose the **partition key** for high cardinality and even distribution — a hot
  partition throttles even when total RU/s looks sufficient.
