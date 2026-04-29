# Migration Knowledge Wiki

This wiki is a **compounding knowledge base** maintained by agents. It grows smarter with every migration run.

## Structure

- **resources/** — Entity pages for Azure resources (how they work, gotchas, best practices)
- **patterns/** — Migration patterns (AWS resource → Azure equivalent, step-by-step)
- **gotchas/** — Known issues discovered during migrations
- **improvements/** — Code quality checklists and improvement rules

## How Agents Use This Wiki

| Agent | Reads | Writes |
|-------|-------|--------|
| developer | patterns/, improvements/ | — |
| code-reviewer | improvements/ | — |
| source-analyzer | resources/ | — |
| memory-writer | — | resources/, patterns/, gotchas/ |
| knowledge-compiler | raw references | resources/, patterns/ |
| feedback | gotchas/, resources/ | gotchas/ (flags stale pages) |

## Conventions

- Files are markdown with YAML front matter
- Use `[[links]]` to cross-reference pages: `[[azurerm_virtual_network]]`
- Every page has `last_updated` and `source_runs` in front matter
- Memory-writer updates pages after every run — knowledge compounds
