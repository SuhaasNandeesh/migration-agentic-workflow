---
name: memory-store
description: "Provides persistent memory storage for the multi-agent system. Contains implementation docs, structured issue tracking, and execution traces in assets/."
metadata:
  version: "1.0"
---
# Memory Store

Central persistent memory for the CodeMigration multi-agent system.

## Purpose
Agents use this skill to read and write persistent knowledge across sessions.

## Asset Structure

### `assets/docs/`
Human-readable documentation and progress tracking:
- `implementation_index.md` — Index of implemented components, pipelines, and status
- `issues_and_fixes.md` — Log of issues encountered and their fixes
- `progress.md` — Current task status, completed items, and pending work

### `assets/structured/`
Machine-readable structured data:
- `issues.json` — JSON array of tracked issues

### `assets/traces/`
Execution trace records:
- `template.json` — Schema template for execution traces

## Usage
- **Reading:** Agents load memory via `rag-query` and `context-builder` skills
- **Writing:** The `memory-writer` agent stores new entries via `memory-write` skill
- **Cleanup:** The `memory-curator` agent prunes via `memory-cleanup` skill
