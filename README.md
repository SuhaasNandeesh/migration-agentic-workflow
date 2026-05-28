# Migration Agentic Workflow — Multi-CLI Orchestration Framework

This repository houses a unified, language-agnostic agentic framework designed to automate DevOps cloud migrations (e.g., AWS to Azure) across multiple enterprise repositories. It is built as a **master design system** where agents, skills, wikis, and configurations are defined once in a master directory (`opencode`) and translated into fully functional native structures for popular CLI agent tools:
* **Antigravity CLI** (Google's agent CLI using `.agents/`)
* **Claude Code** (Anthropic's agent CLI using `.claude/`)
* **Gemini CLI** (Google's classic developer CLI using `.gemini/`)
* **Pi CLI** (Pi's developer CLI using `.pi/`)

---

## 1. First-Time Quick Start & Order of Invocation

To achieve **100% expected results** on your first run, follow this precise order of configuration and execution. 

```mermaid
graph TD
    A["1. Install Local Prerequisites<br>(install-dev-tools.sh)"] --> B["2. Expose API Keys / LM Studio<br>(GEMINI_API_KEY, ANTHROPIC_API_KEY)"]
    B --> C["3. Edit Master Configuration<br>(opencode/migration-config.json)"]
    C --> D["4. Sync CLI Environments<br>(sync-cli-agents.py)"]
    D --> E["5. Coordinate Target Repos<br>(run-multi-repo-coordinator.py)"]
    E --> F["6. Launch Target Agent in Checkout<br>(cd /path/to/target && antigravity)"]
    F --> G["7. Run Post-Migration Verification<br>(Cross-Model Audit & AST Deltas)"]
```

### Step 1: Install Local Prerequisites
Our autonomous agents bypass slow, expensive LLM token requests by executing syntax, structure, and DevSecOps checks locally. Run the interactive setup script to prepare your system:
```bash
./install-dev-tools.sh
```
This script validates or configures Homebrew and installs essential binaries (`terraform`, `checkov`, `tflint`, `kubeconform`, `actionlint`, `hadolint`, `shellcheck`, `gitleaks`, `trufflehog`, `detect-secrets`).

### Step 2: Configure AI Model API Keys or Local Endpoints
Expose your API keys in your active terminal shell, or launch your offline model in **LM Studio** (see Section 4 for offline setup):
```bash
# Cloud-based API keys
export GEMINI_API_KEY="AIzaSyYourGeminiApiKeyHere..."
export ANTHROPIC_API_KEY="sk-ant-apYourClaudeApiKeyHere..."

# (Optional) Persist keys in your shell profile
echo 'export GEMINI_API_KEY="your-gemini-key"' >> ~/.zshrc
echo 'export ANTHROPIC_API_KEY="your-claude-key"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Configure the Master Migration Parameters
Before compiling target agents, customize your migration parameters in **`opencode/migration-config.json`**.
* **`multi_repo_migration.repositories`**: You **MUST** update the `source_dir` and `target_dir` paths to point to the actual directories of your local codebases:
  ```json
  "repositories": [
    {
      "id": "repo-01-infra",
      "source_dir": "/Users/username/Code/aws-infra-repo",
      "target_dir": "/Users/username/Code/azure-infra-repo",
      "environments": ["dev", "test", "prod"]
    }
  ]
  ```
* **`target_versions`**: Define precise compiler versions (e.g., Terraform `1.11.0`, azurerm provider `3.116.0`, Kubernetes `1.29.2`).
* **`finops_standards` & `security_compliance`**: Adjust tags, cost centers, and private egress rules.

> [!IMPORTANT]
> If you are customizing local LLMs, MCP servers, or specific agent tools permissions, you can also modify the master system configuration at `opencode/opencode.json`.

### Step 4: Run the Local Synchronization Script
Compile, translate, and sync the master prompts to the CLI-specific folders:
```bash
/usr/bin/python3 sync-cli-agents.py
```
> [!NOTE]
> If your environment suffers from virtual environment pathing conflicts or Conda codec errors (e.g., `ModuleNotFoundError: No module named 'encodings'`), bypass the local Python wrapper by calling the system binary directly: `/usr/bin/python3 sync-cli-agents.py` or `/usr/local/bin/python3 sync-cli-agents.py`.

### Step 5: Run the Multi-Repo Coordinator
Prepare, isolate, and seed your target repositories:
```bash
/usr/bin/python3 opencode/run-multi-repo-coordinator.py
```
This orchestrator automatically establishes workspace boundaries, injects target-specific orchestrator directories (`.agents/`, `.claude/`, etc.), replicates validation libraries, adds `.gitignore` blocks to prevent target repository pollution, and seeds the company-wide learning base.

### Step 6: Trigger the Migration Agent inside your Target Codebase
Navigate directly to your target codebase root directory and launch your chosen agent:
```bash
# Navigate to the target checkout folder defined in your config
cd /Users/username/Code/azure-infra-repo

# Launch the Antigravity CLI (Recommended)
antigravity

# OR launch Claude Code CLI
claude

# OR launch Gemini CLI
gemini
```
The injected **Supervisor** agent will boot up and execute the full DevOps wave-ordered migration loop autonomously without human intervention!

---

## 2. Master Sync Compiler Compilation Actions

The `sync-cli-agents.py` script ensures that you maintain a single point of truth in `opencode` while deploying flawless configurations across distinct CLI engines:

1. **Directory Lifecycle Management**: Cleans and recreates target platform folders (`.gemini/`, `.claude/`, `.pi/`, `.agents/`) to prevent context drift and stale assets.
2. **Recursive Syncing**: Copies global directories (`DocumentationFactory`, `knowledge`, `migration-mapping`, `validation`, `migration-config.json`, and `run-multi-repo-coordinator.py`) recursively to target roots.
3. **Dynamic Prompt Path Rewriting**: Automatically searches and translates custom paths inside agent instructions (e.g., rewriting `.opencode/skills/` and `.opencode/wiki/` to `.agents/skills/` or `.claude/wiki/`) so that the execution processes run flawlessly without referencing missing directories.
4. **Bi-directional Model Context Protocol (MCP) Translation**: Parses the standard master config `opencode/opencode.json` (which uses a unified local MCP schema) and translates it to standard split `mcpServers` format for `.agents/mcp_config.json` and `.claude/mcp_config.json`.
5. **Zero-Config Claude Bypasses**: Automatically compiles `.claude/settings.json` configuring `"defaultMode": "bypassPermissions"` to disable all interactive CLI permission prompts, enabling fully hands-off orchestration.

---

## 3. Production Codebase Directory Replication Guide

To run the agentic workflow on your actual codebases, copy the specific folders and files generated by the synchronizer into the root of your target checkout repository. (This replication step is performed **automatically** when you run the Multi-Repo Coordinator).

### For Antigravity CLI
Copy the following items from the `antigravity-cli/` directory to your target codebase root:
```
├── .agents/                        <-- Copied folder (includes agents, skills, configs, and wiki)
├── DocumentationFactory/           <-- Copied folder (documentation compiler & markdown templates)
├── knowledge/                      <-- Copied folder (architectural and DevOps patterns)
├── migration-mapping/              <-- Copied folder (platform schemas and mapping dictionary)
├── validation/                     <-- Copied folder (DevSecOps checking and policies)
├── migration-config.json           <-- Copied file (custom migration source, target, & versions)
└── run-multi-repo-coordinator.py   <-- Copied file (multi-repo workspace coordinator & sequential learning)
```
**To run:**
```bash
cd /path/to/your/target/codebase
antigravity
```

---

### For Claude Code
Copy the following items from the `claude-cli/` directory to your target codebase root:
```
├── .claude/                        <-- Copied folder (includes settings.json, agents, skills, configs, and wiki)
├── DocumentationFactory/           <-- Copied folder (documentation compiler & markdown templates)
├── knowledge/                      <-- Copied folder (architectural and DevOps patterns)
├── migration-mapping/              <-- Copied folder (platform schemas and mapping dictionary)
├── validation/                     <-- Copied folder (DevSecOps checking and policies)
├── migration-config.json           <-- Copied file (custom migration source, target, & versions)
└── run-multi-repo-coordinator.py   <-- Copied file (multi-repo workspace coordinator & sequential learning)
```
**To run:**
```bash
cd /path/to/your/target/codebase
claude
```

> [!TIP]
> **Primary vs. Secondary Agent Separation in Claude Code:**
> To prevent terminal autocomplete clutter and avoid the 15-item truncation ceiling in Claude Code's `@` search, the synchronization script automatically structures custom agents into two tiers:
> - **Primary Agents** (`supervisor.md`, `doc-supervisor.md`) are placed directly in `.claude/agents/` to remain easily discoverable in your top-level autocompletes and `/agents` command library.
> - **Secondary/Subagents** (the other 29 specialized agents) are nested neatly in `.claude/agents/subagents/`.
> Because Claude Code scans subagent directories recursively, all subagents remain fully registered and runnable natively (e.g. via background calls like `claude -p --dangerously-skip-permissions --agent <name>`) while keeping your primary interactive environment clean, elegant, and uncluttered!

---

### For Gemini CLI
Copy the following items from the `gemini-cli/` directory to your target codebase root:
```
├── .gemini/                        <-- Copied folder (includes agents, skills, and wiki)
├── gemini.json                     <-- Copied file (main gemini CLI config schema)
├── DocumentationFactory/           <-- Copied folder (documentation compiler & templates)
├── knowledge/                      <-- Copied folder (DevOps patterns & wikis)
├── migration-mapping/              <-- Copied folder (migration dictionary)
├── validation/                     <-- Copied folder (SecOps checking rules)
├── migration-config.json           <-- Copied file (custom migration settings)
└── run-multi-repo-coordinator.py   <-- Copied file (multi-repo orchestration executor)
```
**To run:**
```bash
cd /path/to/your/target/codebase
gemini
```

---

### For Pi CLI
Copy the following items from the `pi-cli/` directory to your target codebase root:
```
├── .pi/                            <-- Copied folder (includes prompts, skills, and wiki)
├── pi.config.ts                    <-- Copied file (TypeScript config entrypoint)
├── DocumentationFactory/           <-- Copied folder (documentation compiler & templates)
├── knowledge/                      <-- Copied folder (DevOps patterns & wikis)
├── migration-mapping/              <-- Copied folder (migration mapping dictionaries)
├── validation/                     <-- Copied folder (DevSecOps validation suite)
├── migration-config.json           <-- Copied file (custom migration configurations)
└── run-multi-repo-coordinator.py   <-- Copied file (multi-repo workspace runner)
```
**To run:**
```bash
cd /path/to/your/target/codebase
pi
```

---

## 4. Local Offline Execution via LM Studio

For strict air-gapped environments or local development, the framework natively integrates with local AI models (such as `Qwen` or `Gemma`) running in **LM Studio**.

To use offline models, the synchronizer maps `opencode/opencode.json` containing local server variables to the target platforms:
```json
"provider": {
  "lmstudio": {
    "name": "Local Qwen",
    "npm": "@ai-sdk/openai-compatible",
    "options": {
      "baseURL": "http://localhost:1234/v1"
    }
  }
}
```
1. Start LM Studio on your local machine.
2. Load your target instruction model (e.g. `gemma-4-e4b-it` or `Qwen 2.5 Coder`) and start the local inference server (running on `http://localhost:1234`).
3. Deploy target directories and execute command lines without cloud internet requirements!

---

## 5. Prerequisites & Developer Tooling Matrix

The automated agents bypass unnecessary LLM token calls by validating syntax, configuration, and security practices locally via sandbox CLI tools first. Downstream agents automatically fall back to direct LLM reviews if a tool is missing, but **installing these native dependencies is highly recommended for production-grade correctness.**

### Tooling Categories Required on Your Laptop

| Domain | Binary / Package | Purpose in Agentic Lifecycle |
|---|---|---|
| **Infrastructure as Code** | `terraform` | Local offline configuration compile gate (`terraform validate/fmt/test`). |
| | `tflint` | Static analysis checking for Cloud provider naming and SKU errors. |
| | `tfsec` | Fast offline checks for insecure cloud infrastructure configurations. |
| | `checkov` | Policy-as-code and configuration analyzer for multi-cloud deployments. |
| **Kubernetes & Helm** | `kubectl` | Validates generated YAML manifests via offline client-side dry runs. |
| | `kubeconform` | Lightning-fast schema checker for target API compliance. |
| | `helm` | Compiles and lints target Helm chart structure (`helm template/lint`). |
| | `kustomize` | Verifies overlays and YAML variants. |
| **CI/CD & Code Linting** | `actionlint` | Verifies GitHub Actions workflow syntax, triggers, permissions, and security. |
| | `yamllint` | Ensures valid, standard-compliant formatting on all configuration YAMLs. |
| | `shellcheck` | Scans helper utility scripts for shell leaks, errors, and standard compliance. |
| | `hadolint` | Standard-compliant lint engine for generated custom Dockerfiles. |
| **DevSecOps Secret Scanning** | `gitleaks` | (Preferred) Scans migration directory for accidental secret leakages. |
| | `trufflehog` | File system deep scanner for database credentials and tokens. |
| | `detect-secrets` | Yelp secret scanner to detect security baseline vulnerabilities. |
| **Workflow & Shell** | `gh` | Fetches live execution logs for self-healing loops if pipeline runs fail. |

---

## 6. Advanced Agentic Optimization & Safety Controls

This system incorporates state-of-the-art context optimizations, contract protections, and execution safeguards designed to prevent logic degradation, eliminate memory leaks, and maximize token efficiency:

### Elite Token-Saving & Quality Optimization Patterns
* **Dynamic JIT Knowledge Enrichment (Mode B JIT)**: Instead of compiling massive static wiki references (which consume vast context budgets), offline subagents write precise docs/gotchas query payloads to `mcp_request.json` and yield. The supervisor intercepts, compiles the target resource, updates the wiki, and wakes the subagent. This keeps local scopes small and highly relevant.
* **Semantic Prompt Assembly**: Subagents never spend read and directory-scanning tokens browsing wiki folders. The orchestrator parses wave parameters and explicitly injects *only* the absolute markdown paths of the matching wiki guidelines in the subagent's tool invocation arguments.
* **Progressive Context Compaction**: During multi-turn fix-and-gate-verify retry loops, context accumulates heavy traceback stdout logs. Compacting prior failure histories into structured single-line annotations (`[Attempt N Failed: {reason}]`) prevents model fatigue and logic degradation.
* **Surgical-Fix Dynamic MCP Escalation**: The sandboxed `surgical-fix` agent automatically requests dynamic web/API documentation searches when local wiki reference limits are reached, resulting in high patch success rates without manual human intervention.
* **Deterministic Script Delegation**: Shift heavy mock test generation and output processing from generative LLM blocks to parameterized local shell wrappers (`run-mock-tests.sh`). Deterministic validation layers prevent formatting bugs and save thousands of generative tokens.

### Robust Validation & JSON Generation
* **Natively Delegated Python JSON Exporters**: Directly embedding multi-line command stdout/stderr into double-quoted JSON strings triggers escape errors. The framework delegates formatting to inline Python scripts (`python3 -c 'import json, sys; ...; json.dump()'`), guaranteeing 100% syntactically valid JSON communication.
* **Bi-Level Schema Contract Enforcement**: Invoking schema contract checks (`validate_schemas.py`) recursively inside individual subagents and centrally inside the multi-repo coordinator ensures early detection and recovery from formatting drifts before any malformed outputs are committed.
* **Strict Provider Pinning**: Floating provider constraints (e.g. `>= 3.0`) represent a compliance risk. Pinning precise version constraints (e.g. `= 3.116.0`) prevents breaking upstream changes and is a core security requirement.
* **Declarative Imports (`imports.tf`)**: Generating declarative `import` blocks is much safer and more auditable than imperative CLI commands (`terraform import`), preserving IaC state history in code review cycles.

### Multi-Language AST Parsing & Resiliency
* **Twin-Track Resiliency (AST + Regex Fallbacks)**: Always pair high-precision AST traversers (e.g. Tree-sitter parsers) with structurally matching Regex-based fallbacks. This ensures absolute architectural safety: if a host system lacks compilers, native headers, or pre-compiled bindings, the agentic pipeline degrades gracefully without interruption, maintaining highly detailed dependency extraction.
* **Resilient Diagram Linting**: Direct regex matches like `\[.*[<>&].*\]` on diagram source lines contain hidden greedy bugs, spanning across connectors (like `-->`) and creating false positive compliance violations. Isolating node brackets and parsing label scopes individually ensures robust, comment-resilient syntax checking.
* **Case-Insensitive Filename Traversal**: Checking exclusively for uppercase `SKILL.md` skips skills using lowercase `skill.md` (e.g. `coverage-auditor`, `dep-graph-builder`, `mermaid-linter`). File-existence checks are case-insensitive.
* **Recursive Directory Sync**: The sync process recursively duplicates entire skill subdirectories rather than copying markdown documents in isolation, retaining crucial script runners (`run.py`), local variables, and asset templates.
* **Offline Sandboxed Validation Gates**: Enforcing compliance against SKU and Tag standards using local mock validation wrappers (`run-mock-tests.sh`) avoids sandbox network timeouts while maintaining rigorous compliance checks against corporate standards.

---

## 7. Premium Verification & Cross-Model Validation Pipeline

To obtain absolute confidence in the migrated infrastructure before deploying to production, we recommend invoking a **Cross-Model Validation Pipeline** where a secondary foundation model (e.g. Google Gemini via Antigravity) acts as an independent auditor to peer-review the output generated by a primary model (e.g. Anthropic Claude via Claude Code).

Follow this step-by-step process to perform a manual cross-model peer review and local verification:

### Step 1: Run the Primary Migration
1. Navigate to the primary CLI engine (e.g., `claude-cli/` to use **Claude 3.5 Sonnet**).
2. Execute the autonomous migration supervisor:
   ```bash
   cd claude-cli
   claude
   ```
3. Wait for the supervisor to complete the wave loops. The final Azure HCL code will be written to `claude-cli/output/target/`.

---

### Step 2: Trigger a Cross-Model Peer Review
By reviewing Claude's output with Gemini (or vice versa), you catch subtle API schema gotchas, naming limits, or security holes that the generating model might have hallucinated.

1. Navigate to the secondary CLI engine (e.g., `antigravity-cli/` to use **Gemini 3.5 Pro or Flash**):
   ```bash
   cd ../antigravity-cli
   ```
2. Copy the generated files and the source inventory metadata from the primary sandbox into the secondary review sandbox:
   ```bash
   # Create outputs folders
   mkdir -p output/target output/artifacts
   
   # Sync the generated code and source census
   cp -r ../claude-cli/output/target/* output/target/
   cp ../claude-cli/output/artifacts/source-inventory.json output/artifacts/source-inventory.json
   ```
3. Run the peer-review command:
   ```bash
   antigravity -p "Perform an independent, rigorous architectural and security code review on the Azure resource configurations generated under 'output/target/'. Check them against the source AWS inventory at 'output/artifacts/source-inventory.json'. Explicitly flag: 1. Hallucinations or missing dependencies, 2. SKU/sizing bounds violations, 3. Tagging or compliance drifts."
   ```
4. The Gemini/Antigravity review report will be output directly in your console and saved under `output/artifacts/code-review-results.json` for analysis.

---

### Step 3: Run Compiler-Grade AST Delta Audits
Instantly see exactly what resources and properties have changed without inspecting massive raw Git diff patches.

1. Generate a standardized Git diff patch of the active target workspace:
   ```bash
   git diff origin/main > output/artifacts/latest-diff.patch 2>/dev/null || git diff HEAD~1 > output/artifacts/latest-diff.patch || touch output/artifacts/latest-diff.patch
   ```
2. Run the AST-style resource change parsing script:
   ```bash
   python3 validation/resource_delta_analyzer.py output/artifacts/latest-diff.patch output/artifacts/ast-summary.md
   ```
3. Display the clean delta checklist:
   ```bash
   cat output/artifacts/ast-summary.md
   ```

---

### Step 4: Execute Local Compliance & Mock Testing
Run offline unit tests to check syntax, schemas, and FinOps standards using HCL mock providers.

1. Execute the mock test wrapper against the generated target:
   ```bash
   ./validation/run-mock-tests.sh output/target
   ```
2. Inspect the test-run scorecard:
   ```bash
   cat output/artifacts/test-results.json
   ```
   *This validates that all files format cleanly, compile natively under `terraform validate`, and conform to mandatory sizing limitations (burstable VMs) and tags (`CostCenter`, `Orchestrator`).*
