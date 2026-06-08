#!/usr/bin/env bash
# ==============================================================================
# Enterprise DevOps Migration Workspace - macOS Tooling Setup & Dependency Installer
# ==============================================================================
# Purpose: Prepares a macOS workstation with all offline syntax compilers, linter 
#          engines, and DevSecOps scanners required for the autonomous agents to 
#          perform at maximum potential (preventing LLM context bloat and 
#          validating code locally prior to API calls).
#
# Requirements: macOS, Homebrew (https://brew.sh), and Python 3.9+ (pip3).
# ==============================================================================

set -o pipefail

# ANSI Color Codes for Premium Console UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print Banner
echo -e "${CYAN}${BOLD}======================================================================${NC}"
echo -e "${PURPLE}${BOLD}   ___        _   _                                _ _             ${NC}"
echo -e "${PURPLE}${BOLD}  / _ \ _ __ | |_| |__  ___  __ _ _ __   __ _  ___  (_)___         ${NC}"
echo -e "${PURPLE}${BOLD} | | | | '_ \| __| '_ \/ __|/ _\` | '_ \ / _\` |/ _ \ | / __|        ${NC}"
echo -e "${PURPLE}${BOLD} | |_| | |_) | |_| | | \__ \ (_| | | | | (_| |  __/ | \__ \        ${NC}"
echo -e "${PURPLE}${BOLD}  \___/| .__/ \__|_| |_|___/\__,_|_| |_|\__, |\___| |_|___/        ${NC}"
echo -e "${PURPLE}${BOLD}       |_|                              |___/                      ${NC}"
echo -e "${CYAN}${BOLD}   DevOps Migration Factory - macOS Tooling Setup Script${NC}"
echo -e "${CYAN}${BOLD}======================================================================${NC}"

# Verification tracking
TOTAL_PLANNED=31
INSTALLED_COUNT=0
MISSING_COUNT=0
FAILED_COUNT=0

# Declare arrays for status report
declare -a ALREADY_INSTALLED
declare -a NEWLY_INSTALLED
declare -a INSTALL_FAILED

# Verify Operating System is macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
  echo -e "${RED}${BOLD}ERROR: This installation script is designed exclusively for macOS.${NC}"
  echo -e "${YELLOW}For other OS variants, please refer to README.md and install the equivalent packages.${NC}"
  exit 1
fi

# Ensure Homebrew is Installed
if ! command -v brew &> /dev/null; then
  echo -e "${YELLOW}${BOLD}WARNING: Homebrew (macOS Package Manager) was not found.${NC}"
  echo -e "${BLUE}Attempting to install Homebrew...${NC}"
  # Note: Standard silent installer prompt
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
    echo -e "${RED}${BOLD}ERROR: Homebrew installation failed. Please install it manually from https://brew.sh${NC}"
    exit 1
  }
  # Add brew to path for the active session if just installed
  if [ -f "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -f "/usr/local/bin/brew" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
else
  echo -e "${GREEN}✓ Homebrew is present: $(brew --version | head -n 1)${NC}"
fi

# Ensure Python 3 and pip3 are present
if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null; then
  echo -e "${YELLOW}${BOLD}WARNING: Python 3 or pip3 is missing. Installing Python via Homebrew...${NC}"
  brew install python || {
    echo -e "${RED}${BOLD}ERROR: Python installation failed. Python 3 and pip3 are mandatory.${NC}"
    exit 1
  }
else
  echo -e "${GREEN}✓ Python 3 and pip3 are present.${NC}"
fi

# Ensure Python skill dependencies (tree-sitter) are installed
echo -e "\n${BOLD}[0] Prime Python Skill Dependencies (Tree-sitter)${NC}"
REQ_PATH="opencode/.opencode/skills/requirements.txt"
if [ -f "$REQ_PATH" ]; then
  echo -e "  Installing Tree-sitter requirements from ${BOLD}${REQ_PATH}${NC}..."
  if pip3 install -r "$REQ_PATH" &> /dev/null || pip3 install --user -r "$REQ_PATH" &> /dev/null; then
    echo -e "      ${GREEN}✓ Successfully installed Tree-sitter libraries!${NC}"
  else
    echo -e "      ${RED}❌ Failed to install Tree-sitter libraries via pip3.${NC}"
  fi
else
  echo -e "  Installing default Tree-sitter libraries..."
  if pip3 install tree-sitter tree-sitter-hcl tree-sitter-python tree-sitter-yaml tree-sitter-go tree-sitter-javascript &> /dev/null || \
     pip3 install --user tree-sitter tree-sitter-hcl tree-sitter-python tree-sitter-yaml tree-sitter-go tree-sitter-javascript &> /dev/null; then
    echo -e "      ${GREEN}✓ Successfully installed default Tree-sitter libraries!${NC}"
  else
    echo -e "      ${RED}❌ Failed to install default Tree-sitter libraries.${NC}"
  fi
fi


echo -e "\n${BLUE}${BOLD}Analyzing workspace tooling status...${NC}"

# Function to check and install a tool via brew
check_and_install_brew() {
  local binary_name="$1"
  local formula_name="$2"
  local category="$3"

  echo -e -n "  Checking [${category}] ${BOLD}${binary_name}${NC} ... "

  if command -v "$binary_name" &> /dev/null; then
    echo -e "${GREEN}✓ Present${NC}"
    ALREADY_INSTALLED+=("$binary_name")
    ((INSTALLED_COUNT++))
  else
    echo -e "${YELLOW}⚠️  Missing${NC}"
    ((MISSING_COUNT++))
    
    echo -e "  --> Installing ${BOLD}${formula_name}${NC} via Homebrew..."
    if brew install "$formula_name" &> /dev/null; then
      echo -e "      ${GREEN}✓ Successfully installed ${binary_name}!${NC}"
      NEWLY_INSTALLED+=("$binary_name")
      ((INSTALLED_COUNT++))
      ((MISSING_COUNT--))
    else
      echo -e "      ${RED}❌ Failed to install ${binary_name}${NC}"
      INSTALL_FAILED+=("$binary_name")
      ((FAILED_COUNT++))
      ((MISSING_COUNT--))
    fi
  fi
}

# Function to check and install a tool via pip3
check_and_install_pip() {
  local binary_name="$1"
  local package_name="$2"
  local category="$3"

  echo -e -n "  Checking [${category}] ${BOLD}${binary_name}${NC} ... "

  if command -v "$binary_name" &> /dev/null; then
    echo -e "${GREEN}✓ Present${NC}"
    ALREADY_INSTALLED+=("$binary_name")
    ((INSTALLED_COUNT++))
  else
    echo -e "${YELLOW}⚠️  Missing${NC}"
    ((MISSING_COUNT++))

    echo -e "  --> Installing ${BOLD}${package_name}${NC} via pip3..."
    if pip3 install --user "$package_name" &> /dev/null || pip3 install "$package_name" &> /dev/null; then
      echo -e "      ${GREEN}✓ Successfully installed ${binary_name}!${NC}"
      NEWLY_INSTALLED+=("$binary_name")
      ((INSTALLED_COUNT++))
      ((MISSING_COUNT--))
    else
      echo -e "      ${RED}❌ Failed to install ${binary_name}${NC}"
      INSTALL_FAILED+=("$binary_name")
      ((FAILED_COUNT++))
      ((MISSING_COUNT--))
    fi
  fi
}

# Category 1: Infrastructure as Code (IaC) Tools
echo -e "\n${BOLD}[1] Infrastructure as Code (IaC) Category${NC}"
check_and_install_brew "terraform" "hashicorp/tap/terraform" "IaC"
check_and_install_brew "tflint" "terraform-linters/tap/tflint" "IaC"
check_and_install_brew "tfsec" "tfsec" "IaC"
check_and_install_pip "checkov" "checkov" "IaC"
# Trivy supersedes the now-EOL tfsec and also covers container image, SBOM, and
# secret scanning from one binary (used by the security agent's modern scan path).
check_and_install_brew "trivy" "trivy" "IaC"

# Category 1b: Policy-as-Code & Cost (org governance + FinOps)
echo -e "\n${BOLD}[1b] Policy-as-Code & Cost Category${NC}"
check_and_install_brew "infracost" "infracost" "Cost"
check_and_install_brew "opa" "opa" "Policy"
check_and_install_brew "conftest" "conftest" "Policy"

# Category 2: Kubernetes Manifests & Linting
echo -e "\n${BOLD}[2] Kubernetes Manifests & Helm Category${NC}"
check_and_install_brew "kubectl" "kubernetes-cli" "K8s"
check_and_install_brew "kubeconform" "kubeconform" "K8s"
check_and_install_brew "helm" "helm" "K8s"
check_and_install_brew "kustomize" "kustomize" "K8s"
# kubeconform only validates schema; kube-linter adds security/best-practice checks.
check_and_install_brew "kube-linter" "kube-linter" "K8s"

# Category 3: CI/CD & Shell Static Analysis
echo -e "\n${BOLD}[3] CI/CD & Shell Static Analysis Category${NC}"
check_and_install_brew "actionlint" "actionlint" "CI/CD"
check_and_install_brew "yamllint" "yamllint" "CI/CD"
check_and_install_brew "shellcheck" "shellcheck" "Shell"
check_and_install_brew "hadolint" "hadolint" "Docker"

# Category 4: Deep DevSecOps Secret Scanners
echo -e "\n${BOLD}[4] DevSecOps Secret Scanners Category${NC}"
check_and_install_brew "gitleaks" "gitleaks" "Security"
check_and_install_brew "trufflehog" "trufflehog" "Security"
check_and_install_pip "detect-secrets" "detect-secrets" "Security"

# Category 5: Git Integration
echo -e "\n${BOLD}[5] Shell Integrations Category${NC}"
check_and_install_brew "gh" "gh" "Git"

# Category 6: Cloud Provider CLIs
# Auth-dependent: enable optional ONLINE validation (Azure naming/SKU/region,
# `az deployment ... what-if`, `terraform plan`) and live source-side AWS introspection.
echo -e "\n${BOLD}[6] Cloud Provider CLIs Category${NC}"
check_and_install_brew "az" "azure-cli" "Azure"
check_and_install_brew "aws" "awscli" "AWS"
check_and_install_brew "bicep" "bicep" "Azure"

# Category 7: Structured Data Utilities (deterministic JSON/YAML manipulation)
echo -e "\n${BOLD}[7] Structured Data Utilities Category${NC}"
check_and_install_brew "jq" "jq" "Data"
check_and_install_brew "yq" "yq" "Data"

# Category 8: Supply-Chain & Container Security (used by the security agent when
# migrating container workloads: image scan, SBOM, vuln scan, signing, ECR->ACR copy)
echo -e "\n${BOLD}[8] Supply-Chain & Container Security Category${NC}"
check_and_install_brew "syft" "syft" "Supply-Chain"
check_and_install_brew "grype" "grype" "Supply-Chain"
check_and_install_brew "cosign" "cosign" "Supply-Chain"
check_and_install_brew "skopeo" "skopeo" "Container"
check_and_install_brew "crane" "crane" "Container"

# Category 9: Pi Agent Extensions (Optional Setup)
if command -v pi &>/dev/null; then
  echo -e "\n${BOLD}[9] Pi Coding Agent Extensions Category${NC}"
  echo -e "  Pi Coding Agent is present. Installing required extensions..."
  if pi install npm:pi-subagents &>/dev/null && pi install npm:pi-opencode-bridge &>/dev/null; then
    echo -e "      ${GREEN}✓ Successfully installed pi-subagents and pi-opencode-bridge!${NC}"
    
    # Configure NODE_PATH for global resolution of dependencies in Pi Agent
    GLOBAL_NODE_ROOT=$(npm root -g 2>/dev/null)
    if [[ -n "$GLOBAL_NODE_ROOT" ]]; then
      # Check for older @mariozechner scope and alias to new @earendil-works scope to prevent load regressions
      OLD_SCOPE_DIR="$GLOBAL_NODE_ROOT/@mariozechner/pi-coding-agent"
      NEW_SCOPE_DIR="$GLOBAL_NODE_ROOT/@earendil-works/pi-coding-agent"
      if [[ -d "$OLD_SCOPE_DIR" && ! -d "$NEW_SCOPE_DIR" ]]; then
        echo -e "  Found older @mariozechner package. Creating backward-compatible symlink alias under @earendil-works..."
        mkdir -p "$GLOBAL_NODE_ROOT/@earendil-works" &>/dev/null
        ln -sf "$OLD_SCOPE_DIR" "$NEW_SCOPE_DIR" &>/dev/null
        echo -e "      ${GREEN}✓ Created @earendil-works compat alias symlink.${NC}"
      fi

      if [[ -z "$NODE_PATH" || "$NODE_PATH" != *"$GLOBAL_NODE_ROOT"* ]]; then
        ZSHRC="$HOME/.zshrc"
        if [ -f "$ZSHRC" ]; then
          if ! grep -q "NODE_PATH" "$ZSHRC"; then
            echo -e "\n# Node global modules path for Pi Coding Agent" >> "$ZSHRC"
            echo "export NODE_PATH=\"$GLOBAL_NODE_ROOT\"" >> "$ZSHRC"
            echo -e "      ${GREEN}✓ Appended export NODE_PATH=\"$GLOBAL_NODE_ROOT\" to $ZSHRC.${NC}"
            echo -e "      ${YELLOW}Please run 'source $ZSHRC' or open a new terminal tab to apply the configuration.${NC}"
          fi
        else
          echo -e "      ${YELLOW}⚠️  Note: Please add the following to your shell profile to resolve global node packages:${NC}"
          echo -e "          ${BOLD}export NODE_PATH=\"$GLOBAL_NODE_ROOT\"${NC}"
        fi
      fi
    fi
  else
    echo -e "      ${YELLOW}⚠️  Failed to install some Pi extensions. Ensure network access and try running them manually.${NC}"
  fi
fi

# Print Installation Summary
echo -e "\n${CYAN}${BOLD}======================================================================${NC}"
echo -e "${BOLD}                     SETUP SUMMARY & REPORT                           ${NC}"
echo -e "${CYAN}${BOLD}======================================================================${NC}"
echo -e "  Total Analyzed Toolsets : ${BOLD}${TOTAL_PLANNED}${NC}"
echo -e "  Active/Working Toolsets : ${GREEN}${BOLD}${INSTALLED_COUNT}${NC} / ${TOTAL_PLANNED}"
echo -e "  Failed Installations    : ${RED}${BOLD}${FAILED_COUNT}${NC}"

if [ ${#ALREADY_INSTALLED[@]} -gt 0 ]; then
  echo -e "\n${GREEN}✓ Already Present Tools:${NC}"
  echo -e "  ${ALREADY_INSTALLED[*]}"
fi

if [ ${#NEWLY_INSTALLED[@]} -gt 0 ]; then
  echo -e "\n${GREEN}✓ Newly Configured Tools:${NC}"
  echo -e "  ${NEWLY_INSTALLED[*]}"
fi

if [ ${#INSTALL_FAILED[@]} -gt 0 ]; then
  echo -e "\n${RED}❌ Failed Tool Configs (Manual Brew/Pip Action Required):${NC}"
  echo -e "  ${INSTALL_FAILED[*]}"
  echo -e "  --> Check Homebrew errors or try running: 'brew install <tool-name>'"
fi

# Exit Status Code
if [ ${FAILED_COUNT} -eq 0 ]; then
  echo -e "\n${GREEN}${BOLD}✓ System Setup Completed. All migration agents are equipped for full potential!${NC}\n"
  exit 0
else
  echo -e "\n${YELLOW}${BOLD}⚠️  System Setup Completed with warnings. Please resolve failed dependencies.${NC}\n"
  exit 1
fi
