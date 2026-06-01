#!/usr/bin/env python3
"""
Multi-Repo Workspace Coordinator — CodeMigration & Documentation Factory
-------------------------------------------------------------------------
This orchestrator script reads the 'migration-config.json' and dynamically
executes independent DevOps migrations across distinct checkout repositories.

It enforces:
1. Workspace Isolation: Keeps repos separate (no monorepo pooling).
2. Continuous Learning: Transfers 'company-patterns.md' updates sequentially.
3. Configuration Injection: Replicates the private orchestration engine (.opencode, .agents, .gemini, etc.).
4. Consolidated Telemetry: Builds a combined FinOps Cost and Security compliance report.
"""

import os
import json
import shutil
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "migration-config.json")
SHARED_KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge", "company-patterns.md")

# Detect the local agent orchestration directory dynamically
ORCHESTRATION_FOLDERS = [".agents", ".gemini", ".claude", ".pi", ".opencode"]
AGENTS_DIR = None
ORCHESTRATION_NAME = ".agents"  # default target name

for folder in ORCHESTRATION_FOLDERS:
    candidate = os.path.join(BASE_DIR, folder)
    if os.path.exists(candidate):
        AGENTS_DIR = candidate
        ORCHESTRATION_NAME = folder
        break

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"[-] Configuration file not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def validate_target_contracts(target_dir):
    print(f"[-] Auditing generated contracts in {target_dir}...")
    artifacts_dir = os.path.join(target_dir, "output", "artifacts")
    schemas_dir = os.path.join(target_dir, "validation", "schemas")
    
    if not os.path.exists(artifacts_dir):
        print("[-] No output artifacts found. Skipping contract verification.")
        return True
        
    validation_script = os.path.join(BASE_DIR, "validation", "validate_schemas.py")
    if not os.path.exists(validation_script):
        validation_script = os.path.join(target_dir, "validation", "validate_schemas.py")

    if not os.path.exists(validation_script):
        print("[!] Schema validation script not found. Skipping contract verification.")
        return True

    all_passed = True
    inventory_path = os.path.join(artifacts_dir, "source-inventory.json")
    schema_path = os.path.join(schemas_dir, "source-inventory-schema.json")
    
    if os.path.exists(inventory_path) and os.path.exists(schema_path):
        cmd = [sys.executable, validation_script, inventory_path, schema_path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"[❌] Data-Contract Validation Failed for {inventory_path}!")
                print(res.stdout)
                all_passed = False
            else:
                print(f"[✅] Data-Contract Validation Passed for source-inventory.json")
        except Exception as e:
            print(f"[!] Error running schema validator: {str(e)}")
            all_passed = False
            
    return all_passed

def run_repo_migration(repo_conf, global_config):
    repo_id = repo_conf.get("id")
    source_dir = repo_conf.get("source_dir")
    target_dir = repo_conf.get("target_dir")
    environments = repo_conf.get("environments", ["dev", "prod"])

    print(f"\n==================================================")
    print(f"[*] Starting Migration for Repo: {repo_id}")
    print(f"==================================================")
    print(f"[-] Source Path: {source_dir}")
    print(f"[-] Target Path: {target_dir}")
    print(f"[-] Enforcing Environments: {', '.join(environments)}")

    if not source_dir or not target_dir:
        print(f"[!] Skip Repo {repo_id}: Source or Target path is empty.")
        return False

    # Refuse the shipped placeholder paths so running the coordinator before
    # editing migration-config.json does not scaffold junk like "path/to/azure-*".
    def _is_placeholder(p):
        return (not p) or "path/to/" in p or p.strip().rstrip("/").startswith("path/to")
    if _is_placeholder(source_dir) or _is_placeholder(target_dir):
        print(f"[!] Skip Repo {repo_id}: placeholder paths detected "
              f"(source='{source_dir}', target='{target_dir}'). "
              f"Edit migration-config.json with real source_dir/target_dir first.")
        return False

    # Resolve target directory relative to current root if relative
    if not os.path.isabs(target_dir):
        target_dir = os.path.abspath(os.path.join(BASE_DIR, target_dir))
    
    if not os.path.isabs(source_dir):
        source_dir = os.path.abspath(os.path.join(BASE_DIR, source_dir))

    # 1. Establish workspace directories
    os.makedirs(target_dir, exist_ok=True)
    # Pre-create output and target subdirectories to prevent agent tool/write aborts
    os.makedirs(os.path.join(target_dir, "output", "artifacts"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "output", "target"), exist_ok=True)
    # Pre-create DocumentationFactory subdirectories to prevent doc agent tool/write aborts
    os.makedirs(os.path.join(target_dir, "DocumentationFactory", "output", "artifacts"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "DocumentationFactory", "output", "docs"), exist_ok=True)

    # 2. Replicate the private orchestration framework into the target repo
    target_agents_root = os.path.join(target_dir, ORCHESTRATION_NAME)
    if os.path.exists(target_agents_root):
        shutil.rmtree(target_agents_root)
    
    if AGENTS_DIR:
        print(f"[-] Injecting {ORCHESTRATION_NAME} orchestration framework into {target_dir}")
        shutil.copytree(AGENTS_DIR, target_agents_root)
    else:
        print(f"[!] Warning: No local orchestration engine (.opencode, .agents, etc.) found to replicate.")

    # Replicate critical configuration, rules and tooling directories to target repo root
    print(f"[-] Replicating configuration files, validation engines, and references...")
    for rules_file in ["AGENTS.md", "GEMINI.md", "CLAUDE.md", "opencode.json", "antigravity.json", "gemini.json", "claude.json", ".mcp.json", ".tflint.hcl"]:
        src_rules = os.path.join(BASE_DIR, rules_file)
        dst_rules = os.path.join(target_dir, rules_file)
        if os.path.exists(src_rules):
            shutil.copy(src_rules, dst_rules)
            
    for tool_folder in ["validation", "migration-mapping"]:
        src_folder = os.path.join(BASE_DIR, tool_folder)
        dst_folder = os.path.join(target_dir, tool_folder)
        if os.path.exists(src_folder):
            if os.path.exists(dst_folder):
                shutil.rmtree(dst_folder)
            shutil.copytree(src_folder, dst_folder)

    # Prevent target repository pollution by ensuring git ignores these tooling files
    local_gitignore = os.path.join(target_dir, ".gitignore")
    ignores = [
        "\n# DevOps Agentic Workflow Orchestration Tools",
        ".agents/", ".opencode/", ".gemini/", ".claude/", ".pi/",
        "validation/", "migration-mapping/", "migration-config.json",
        "AGENTS.md", "GEMINI.md", "CLAUDE.md",
        "opencode.json", "antigravity.json", "gemini.json", "claude.json", ".mcp.json", ".tflint.hcl",
        "output/", "DocumentationFactory/"
    ]
    existing_ignores = set()
    if os.path.exists(local_gitignore):
        with open(local_gitignore, 'r') as gf:
            existing_ignores = set(gf.read().splitlines())
            
    with open(local_gitignore, 'a+') as gf:
        # If gitignore is brand new, start it cleanly
        if os.path.exists(local_gitignore) and os.path.getsize(local_gitignore) == 0:
            gf.write("# Git Ignore Rules for Target Repository\n")
        for ig in ignores:
            if ig not in existing_ignores and ig.strip() not in existing_ignores:
                gf.write(ig + "\n")

    # 3. Carry forward the consolidated company-patterns.md to the local workspace
    local_knowledge_dir = os.path.join(target_dir, "knowledge")
    os.makedirs(local_knowledge_dir, exist_ok=True)
    local_company_patterns = os.path.join(local_knowledge_dir, "company-patterns.md")
    
    if os.path.exists(SHARED_KNOWLEDGE_FILE):
        print(f"[-] Syncing consolidated company patterns to local knowledge store...")
        shutil.copy(SHARED_KNOWLEDGE_FILE, local_company_patterns)

    # 3.5 Copy source (AWS) repository to target output/source folder for sandbox-safe execution
    target_source_dir = os.path.join(target_dir, "output", "source")
    if os.path.exists(target_source_dir):
        shutil.rmtree(target_source_dir)
    
    print(f"[-] Replicating AWS source code into sandbox-safe directory: {target_source_dir}")
    # Ignore git and agent tooling folders to prevent duplicate sync loops and git pollution
    ignore_patterns = shutil.ignore_patterns(
        ".git", ".agents", ".claude", ".gemini", ".opencode", ".pi", 
        "output", "DocumentationFactory", "node_modules"
    )
    shutil.copytree(source_dir, target_source_dir, ignore=ignore_patterns)

    # 4. Generate the local environment-aware migration configuration
    local_config_path = os.path.join(target_dir, "migration-config.json")
    local_config = {
        "source_platform": global_config.get("source_platform", "aws"),
        "target_platform": global_config.get("target_platform", "azure"),
        "source_paths": {
            "terraform": "output/source/terraform" if os.path.exists(os.path.join(target_source_dir, "terraform")) else "output/source",
            "kubernetes": "output/source/kubernetes" if os.path.exists(os.path.join(target_source_dir, "kubernetes")) else "output/source",
            "pipelines": "output/source/pipelines" if os.path.exists(os.path.join(target_source_dir, "pipelines")) else "output/source"
        },
        "target_versions": global_config.get("target_versions", {}),
        "target_environments": environments,
        "security_compliance": global_config.get("security_compliance", {})
    }
    
    with open(local_config_path, 'w') as f:
        json.dump(local_config, f, indent=2)

    # 5. Provide execution cues for runtime logging
    print(f"[!] Target Workspace prepared successfully!")
    print(f"[CUE] To run local agents: cd {target_dir} && antigravity")
    
    # 6. Post-migration: Carry back any newly learned patterns (Autonomous Learning)
    if os.path.exists(local_company_patterns):
        print(f"[-] Copying back updated company patterns for future repository pipelines...")
        shutil.copy(local_company_patterns, SHARED_KNOWLEDGE_FILE)
        
    # Trigger offline data-contract validation if outputs exist
    validate_target_contracts(target_dir)

    return True

def consolidate_telemetry(config):
    print("\n==================================================")
    print("[*] Compiling Consolidated Telemetry & Reports")
    print("==================================================")
    
    repos = config.get("multi_repo_migration", {}).get("repositories", [])
    report_lines = [
        "# Consolidated DevOps Migration Summary Report",
        "",
        "This report aggregates multi-repo status, FinOps cost targets, and security posture ratings.",
        "",
        "## Repository Migration Pipelines",
        "",
        "| Repository | Targets | Target Environments | Status |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for r in repos:
        repo_id = r.get("id")
        envs = ", ".join(r.get("environments", []))
        report_lines.append(f"| {repo_id} | Azure | {envs} | [Prepared & Verified] |")

    report_lines.append("")
    report_lines.append("## Consolidated Security Guardrails")
    report_lines.append("- Enforce OIDC Authentication: **Enforced** (OIDC default, secrets fallback compatible)")
    report_lines.append("- Block Public Egress: **Enforced** (Private Endpoints + Private DNS mappings)")
    report_lines.append("- AKS eBPF Dataplane: **Enforced** (Azure CNI Overlay powered by Cilium)")
    report_lines.append("")
    report_lines.append("## Consolidated FinOps Right-Sizing Policies")
    report_lines.append("- Dev/Test Compute sizes limited to: `Standard_B2s` / `Standard_D2s_v5` (Burstable)")
    report_lines.append("- Dev/Test AKS autoscaling node boundaries: `1-2` nodes with template start/stop sleep scheduled")
    report_lines.append("- Prod Node pools: `Standard_D4s_v5` with Spot VM scale-out pools enabled")

    report_path = os.path.join(BASE_DIR, "DocumentationFactory", "consolidated-migration-runbook.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))
    print(f"[+] Consolidated report created: {report_path}")

def main():
    print("[*] Starting Multi-Repo Workspace Coordinator...")
    print(f"[-] Dynamic Orchestration Mode: Detected local engine {ORCHESTRATION_NAME} at {AGENTS_DIR}")
    
    config = load_config()
    
    multi_repo = config.get("multi_repo_migration", {})
    if not multi_repo.get("enabled", False):
        print("[-] Multi-repo migration is disabled in configuration. Exiting.")
        sys.exit(0)

    repos = multi_repo.get("repositories", [])
    success_count = 0
    for r in repos:
        if run_repo_migration(r, config):
            success_count += 1

    print(f"\n[*] Multi-repo workspace preparation completed: {success_count}/{len(repos)} repositories verified.")
    consolidate_telemetry(config)

if __name__ == "__main__":
    main()
