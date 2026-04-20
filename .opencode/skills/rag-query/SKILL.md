---
name: rag-query
description: "Retrieves relevant knowledge from standards and memory to provide context for agent execution."
metadata:
  version: "1.0"
---
# RAG Query

Retrieve relevant knowledge for agent context.

## Input
- query

## Output
- top_k_results

## Rules
- Max 3 results
- Prioritize:
  1. Standards (from `validation/references/`)
  2. Recent memory (from `memory-store/assets/`)
