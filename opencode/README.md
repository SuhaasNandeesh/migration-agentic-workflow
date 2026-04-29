# Migration Factory — Autonomous Agentic Code Migration

An autonomous, multi-agent pipeline that migrates infrastructure-as-code from one cloud platform to another. Designed for enterprise-scale codebases (20 to 300+ files) running on local LLMs.

## What It Does

Point it at a source codebase (Terraform, Kubernetes, CI/CD pipelines, Dockerfiles, shell scripts) and a target platform. It autonomously:

1. **Discovers** every resource, dependency, and configuration (using deterministic Python skills).
2. **Maps** each resource to its target platform equivalent, optionally utilizing the **Documentation Factory's** pre-computed `global-data-dictionary.json` for perfectly secure secret mapping.
3. **Plans** a dependency-ordered migration in waves.
4. **Generates** production-grade target code with best practices.
5. **Reviews** for accuracy, security, and compliance.
6. **Validates** with deterministic DevSecOps CLI tools (`checkov`, `tflint`, and Terraform 1.6+ `mock_provider` blocks).
7. **Packages** a deployment-ready bundle with documentation.
8. **Publishes** the final verified code directly to a Git feature branch via the `git-publisher` agent.

No human intervention required during execution. Fully resumable if interrupted.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      SUPERVISOR                              │
│              (orchestrates all agents)                        │
│                                                              │
│  Step 0          Step 0.5        Step 1         Step 1.5     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │Knowledge │   │Bash Pre- │   │ Source   │   │Migration │  │
│  │Compiler  │   │Scan (find│   │Analyzer  │   │ Mapper   │  │
│  │(+MCP)    │   │+grep)    │   │(+verify) │   │          │  │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘  │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  wiki pages    file-census.txt  source-inv.json  mapping.json│
│  on disk       (ground truth)   (cross-checked)              │
│                                                              │
│  Step 2: PLANNER → execution-plan.json (waves + categories)  │
│                                                              │
│  ┌─────────── WAVE LOOP (per category, max 8 files) ───────┐│
│  │                                                          ││
│  │  Developer ──→ Code Reviewer ──→ QA Tester ──→ ✓        ││
│  │      │              │                │                   ││
│  │      │         (fail)│           (fail)│                  ││
│  │      │              ▼                ▼                   ││
│  │      │        Surgical Fix ←── git diff                  ││
│  │      │         (retry 1-2)                               ││
│  │      │              │                                    ││
│  │      ◄──────────────┘ (escalate on 3rd failure)          ││
│  │                                                          ││
│  │  checkpoint → pipeline-state.json → git commit           ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  Post-Wave: Validator (all files) → Security (all files)     │
│                                                              │
│  Finalization: Documentation → Evaluator → Packager          │
│               → Memory Writer → Feedback                     │
└──────────────────────────────────────────────────────────────┘
```

## Agents

| # | Agent | Role | Invoked |
|:-:|-------|------|---------|
| 1 | **knowledge-compiler** | Compiles references → wiki pages. Auto-discovers LTS versions. Only agent with internet access (MCP/fetch) | Step 0 |
| 2 | **source-analyzer** | Scans source codebase, inventories all resources by category | Step 1 |
| 3 | **migration-mapper** | Maps each source resource to target platform equivalent | Step 1.5 |
| 4 | **planner** | Creates wave-ordered execution plan with categories (max 8 files each) | Step 2 |
| 5 | **developer** | Generates target code for ONE category per invocation | Per category |
| 6 | **code-reviewer** | Reviews code accuracy (dual-mode: full scan or retry-only) | Per category |
| 7 | **qa-tester** | Runs validation tools: terraform, kubectl, linters (dual-mode) | Per category |
| 8 | **surgical-fix** | Fixes specific issues during retries (graduated: Level 1/2) | On gate failure |
| 9 | **validator** | Enforces standards compliance across ALL generated files | Post-wave |
| 10 | **security** | DevSecOps + secret scanning (gitleaks/truffleHog) + compliance policies | Post-wave |
| 11 | **cost-estimator** | Estimates infra cost, source vs target comparison, anomaly flagging | Post-wave |
| 12 | **documentation** | Runbooks, ADRs, state migration guide, env validation, cost/security reports | Finalization |
| 13 | **evaluator** | Measures migration completeness and quality metrics | Finalization |
| 14 | **packager** | Assembles deployment-ready bundle + PR metadata + git branch | Finalization |
| 15 | **memory-writer** | Persists learnings to wiki for future runs | Finalization |
| 16 | **shared-memory-writer**| Implements *Categorized Knowledge Routing* to share lessons learned globally without context bloat | Finalization |
| 17 | **git-publisher** | Commits and conditionally pushes the final code to a Git feature branch | Finalization |
| 18 | **feedback** | Improvements, wiki linting, pruning, deduplication | Finalization |

## Key Design Decisions

### Scale-Invariant Processing
Every agent invocation sees **max ~12K tokens** regardless of codebase size. A 300-file codebase processes identically to a 20-file one — just more invocations, same quality each time.

### File-Based Handover (No Context Bloat)
Agents write full output to `output/artifacts/*.json` and return only a 1-2 line summary. The supervisor's context grows by ~30 tokens per step, not thousands.

### Surgical Retries (Not Bulk Regeneration)
When a gate fails, the `surgical-fix` agent patches only the broken file using `git diff`. The gate re-evaluates only the patch (~500 tokens) instead of all files (~20K tokens).

### Internet Safety Boundary
Only the knowledge-compiler (Step 0) touches the internet via MCP/fetch. All other agents read from local wiki pages. Source code never leaves the machine.

### Deterministic Accuracy & Security
A bash `find + grep` pre-scan establishes ground truth file counts before the LLM scans anything. Security agents execute hard CLI commands (`checkov`, `tflint`) and the QA Tester dynamically generates Terraform 1.6 `.tftest.hcl` files to use `mock_provider` blocks, allowing 100% logic validation without touching real Azure/AWS credentials.

### Training Data Weight Override (SLM Bypass)
Local models suffer from a "Training Data Cutoff" trap. To force the LLM/SLM to generate code for modern target versions (e.g., Terraform 1.11), the `knowledge-compiler` fetches complete "Golden Examples." The `developer` and `surgical-fix` agents receive a strict **Weight Override Directive** in their system prompts, forcing them to suppress pre-trained habits and exclusively mimic the fetched examples.

### Categorized Knowledge Routing
To solve the memory context bloat of multi-repo enterprise architectures, the `shared-memory-writer` distills lessons learned into highly specific domain files (e.g., `knowledge/networking.md`, `knowledge/auth.md`). Agents dynamically load *only* the specific domain knowledge they need for their current wave, guaranteeing 0% information loss with maximum token efficiency.

## Supported Tools & Services

| Tool | Discovery | Migration | Validation |
|------|:---------:|:---------:|:----------:|
| Terraform (`.tf`) | ✅ | ✅ Full mapping + code gen | `terraform fmt/validate/plan` |
| Kubernetes (`.yaml`) | ✅ | ✅ Annotation/image/storage mapping | `kubeconform`, `kubectl dry-run` |
| Helm Charts | ✅ | ✅ Values + template migration | `helm lint`, `helm template` |
| Kustomize | ✅ | ✅ Overlay adaptation | `kustomize build` |
| GitHub Actions | ✅ | ✅ From GitLab CI / Jenkins | `actionlint`, `yamllint` |
| GitLab CI | ✅ | ✅ → GitHub Actions | `yamllint` |
| Jenkins | ✅ | ✅ → GitHub Actions | Syntax check |
| Docker / Compose | ✅ | ✅ Registry + base image updates | `hadolint` |
| Shell scripts | ✅ | ✅ AWS CLI → Azure CLI | `shellcheck` |
| Grafana / Prometheus | ✅ | ✅ Retain + config updates | JSON/YAML lint |
| Unknown tools | ✅ Auto-discover | ⚠️ LLM knowledge + fetch | Generic lint |

## Configuration

### `migration-config.json`
```json
{
  "source_platform": "aws",
  "target_platform": "azure",
  "source_paths": {
    "terraform": "path/to/tf",
    "kubernetes": "path/to/k8s",
    "pipelines": "",
    "monitoring": "",
    "other": ""
  },
  "target_versions": {
    "terraform": "<placeholder_or_leave_empty_for_auto_lts>",
    "azurerm": "<placeholder_or_leave_empty_for_auto_lts>",
    "kubernetes": "<placeholder_or_leave_empty_for_auto_lts>"
  }
}
```

### MCP Servers (in `opencode.json`)
Two MCP servers provide latest documentation without exposing code:
- **terraform-docs** — HashiCorp official, queries Terraform Registry API
- **web-fetch** — Generic URL-to-markdown for any other tool's docs

## Knowledge Wiki

Pre-compiled knowledge at `.opencode/wiki/` with 28 pages across 4 categories:

```
.opencode/wiki/
├── index.md                              ← Wiki index
├── improvements/
│   ├── code-improvement-checklist.md     ← Quality standards
│   └── naming-conventions.md            ← File/resource naming rules
├── resources/                            ← 9 entity pages
│   ├── azurerm_virtual_network.md
│   ├── kubernetes_deployment.md
│   ├── github_actions_workflow.md
│   └── ...
├── patterns/                             ← 10 migration patterns
│   ├── aws-vpc-to-azure-vnet.md
│   ├── eks-to-aks-manifests.md
│   ├── gitlab-ci-to-github-actions.md
│   └── ...
└── gotchas/                              ← 6 known issues
    ├── aks-workload-identity.md
    ├── ecr-to-acr.md
    └── ...
```

## Output Structure

```
output/
├── artifacts/                    ← Agent artifacts (JSON)
│   ├── file-census.txt          ← Deterministic pre-scan
│   ├── source-inventory.json    ← Full resource inventory
│   ├── migration-mapping.json   ← Resource mapping
│   ├── execution-plan.json      ← Wave-ordered plan
│   ├── generated-files.json     ← File manifest
│   └── ...
├── pipeline-state.json           ← Resume checkpoint
├── pipeline-log.md               ← Human-readable execution log

## Prerequisites
To get the most out of the determinism in this factory, install the following CLI tools. If they are not installed, the agents will **gracefully degrade** to LLM-based reasoning:
- **Migration Factory:** `terraform` (1.6+), `checkov`, `tflint`
- **Documentation Factory:** `mkdocs`, `markdownlint-cli2`, `lychee`
- **Python Skills:** `python3` (run `pip install -r .opencode/skills/requirements.txt`)

## Execution Workflow
├── Terraform_Modules-Azure/      ← Generated target code
│   ├── environments/
│   │   ├── development/
│   │   ├── staging/
│   │   └── production/
│   └── modules/
│       ├── resource_group/
│       ├── networking/
│       ├── compute/
│       └── ...
└── docs/                         ← Generated documentation
    ├── migration-runbook.md
    ├── architecture-decisions/
    └── deployment-guide.md
```

## Running

### With OpenCode CLI (Local LLM via LMStudio)
```bash
cd CodeMigration
opencode  # starts the supervisor automatically
```

### With Gemini CLI
```bash
cd CodeMigration
gemini  # uses .gemini/ agent configs
```

### With Claude Code CLI
```bash
cd CodeMigration
claude  # uses .claude/ agent configs
```

## Resumability

If the pipeline is interrupted (Ctrl+C, crash, timeout), it resumes from the last completed category:
```
On restart:
  1. Reads output/pipeline-state.json
  2. Finds last completed wave/category
  3. Resumes from the next category
  4. All completed artifacts are on disk
```

## Gate Thresholds

Quality gates enforce quantitative pass/fail criteria (not subjective LLM judgment):

| Gate | Pass Condition |
|------|---------------|
| Code Review | critical_issues == 0, major_issues ≤ 2 |
| QA Testing | pass_rate ≥ 95%, syntax_errors == 0 |
| Validation | compliance ≥ 90%, blocking_violations == 0 |
| Security | security_score ≥ 80, critical_findings == 0 |
| Completeness | resource_coverage ≥ 90% |

## Cost & Token Optimization

| Optimization | Token Savings |
|-------------|:------------:|
| Wiki externalization | ~40% per agent prompt |
| File-based handover | ~90% on supervisor context |
| Category batching (max 8 files) | ~75% per developer call |
| Dual-mode retry (diff only) | ~95% on retry evaluations |
| Surgical-fix vs full developer retry | ~80% on retry fixes |
| Category-to-wiki mapping | ~60% on wiki loading |
| Structured JSON output | ~200-500 tokens per agent |

## License

Internal use.
