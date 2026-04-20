---
name: memory-cleanup
description: "Cleans the memory store by removing duplicates and merging similar entries. Operates on memory-store skill assets."
metadata:
  version: "1.0"
---
# Memory Cleanup

Clean and optimize the memory store.

## Rules
- Remove duplicates from `memory-store/assets/structured/`
- Merge similar entries in `memory-store/assets/docs/`
- Preserve high-confidence and recent data
