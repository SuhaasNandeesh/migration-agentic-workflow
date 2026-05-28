# System Common Guidelines for Agents

## [CORE] 1. Disk-Based I/O Protocol (Context Preservation)
*   **Do NOT return raw files or massive datasets as conversational text.**
*   Write your FULL, detailed output files exclusively under `output/artifacts/`.
*   Always verify that target parent directories exist, or create them recursively before writing.
*   Return ONLY a 1-2 line summary to the supervisor with the exact path (e.g., `Completed. Wrote 15 rules to output/artifacts/migration-mapping.json`).

## [CORE] 2. Structured Output Enforcement (JSON Boundary)
*   For analytical/validator steps, respond with a valid, parsable JSON block ONLY.
*   Do NOT include any preamble, conversation, or markdown code fences (no ```json).
*   Start your response exactly with `{` and end exactly with `}`.

## [CORE] 3. Anti-Sycophancy Mandate (Quantitative Verification)
*   State findings with precise metrics: `passed`, `failed`, `skipped`, and `pass_rate` (as percentage).
*   Always check results against quantitative thresholds defined in `validation/gate-thresholds.json`.
*   If a tool or linter is missing, report it as a warning/skip and count as skipped rather than passing.

## [CORE] 4. Token Budget Guardrails
*   Process data in small, discrete categories or waves (never load more than 8 files per invocation).
*   If stuck or retrying the same loop 3 times without making progress, gracefully abort and log the state.

## [CORE] 5. Path Robustness Rule (Nested Source Repositories)
*   If a source file path is not found directly relative to workspace root, perform recursive search (glob/find) to resolve the actual nested file path instead of failing.

## [DEVOPS] 6. Terraform Chdir Rule (CLI Execution Boundary)
*   Terraform commands do NOT accept a directory path as a direct trailing argument. Do NOT run `terraform init <path>`. You MUST use the global `-chdir=<path>` flag or change directories first (e.g., `terraform -chdir=<path> init -backend=false` or `cd <path> && terraform init -backend=false`).

## [DEVOPS] 7. Graceful Optional File Reading Rule (No Blind Reads)
*   No file is guaranteed to exist. Do NOT assume `main.tf` or any configuration files are present. Always verify file existence via listing/glob tools before calling a read tool.
*   For mandatory pipeline files (e.g., `generated-files.json`), if missing, do NOT run empty scans. Abort immediately with a structured JSON response: `{"status": "fail", "error": "Prerequisite step has not completed"}`.

## [CORE] 8. No System-Level /tmp Rule (Sandbox Preservation)
*   Do NOT write to, read from, or execute commands inside system directories like `/tmp/`, `/var/tmp/`, or outside the workspace. The secure sandbox blocks these paths. Create and use a subdirectory within the workspace instead (e.g., `output/artifacts/tmp/`).

## [CORE] 9. Relative Path Resolution Protocol (Workspace Renames/Moves)
*   **Do NOT hardcode absolute paths** (e.g., `/Users/...`). Pass relative paths to all tools.
*   If you read absolute paths from historical logs or cached JSONs referencing a different folder, dynamically replace the old prefix with your current workspace root.

## [CORE] 10. Strict Tool Spelling Rule
*   You MUST use exact tool names. The wildcard file search tool is strictly named `glob`. Do NOT write `globe` (with an 'e') — that spelling hallucination will crash the execution.

## [AST] 11. Just-in-Time Context Hydration Protocol (AST Code Folding)
*   To prevent context bloat on large files (>= 1,000 lines), do NOT read them raw. First run the `ast-stubber` skill to generate a structural stub:
    `python3 .agents/skills/ast-stubber/run.py --file <path> --stub --output output/artifacts/stubs/<path>`
    Read only the lightweight stub to map out signatures.
*   If you need to read/edit folded blocks (e.g. `// ... [Folded Block: aws_instance.web]`), first run `ast-stubber` in hydration mode to extract the exact code snippet:
    `python3 .agents/skills/ast-stubber/run.py --file <path> --hydrate --block-name <symbol>` or `--line-range <start>-<end>`
*   This JIT expansion prevents context pollution while maintaining compiler-grade accuracy.

## [DEVOPS] 12. Canonical Intermediate Artifact Filenames (Zero Mismatches)
*   You MUST write/read from the exact canonical filenames below (never use `doc-plan.json` or `discovery-scan.json`):
    *   Dependency Graph: `DocumentationFactory/output/artifacts/dependency-graph.json`
    *   Wave Execution Plan: `DocumentationFactory/output/artifacts/doc-execution-plan.json`
    *   Infrastructure Specs: `DocumentationFactory/output/artifacts/infrastructure-specs.json`
    *   Control Flow Specs: `DocumentationFactory/output/artifacts/pipeline-flows.json`
    *   Global Data Dictionary: `DocumentationFactory/output/artifacts/global-data-dictionary.json`
    *   Doc Review Results: `DocumentationFactory/output/artifacts/doc-review-results.json`
    *   Architecture Diagrams: `DocumentationFactory/output/artifacts/architecture-diagrams.json`

## [DEVOPS] 13. Dynamic Script Generalization & Data-Contract Compliance
*   Autonomously generated scanner scripts MUST output JSON conforming to schemas (e.g., `validation/schemas/source-inventory-schema.json`).
*   The `statistics` object in output JSON must contain `"total_files"` and `"total_resources"` directly.
*   Make all script lookups completely key-error safe by using `.get()` to prevent script crashes.
