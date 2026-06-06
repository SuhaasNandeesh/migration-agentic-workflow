#!/usr/bin/env bash
# ==============================================================================
# Parameterized Mock Test Runner for Terraform Offline Validation
# ==============================================================================
# Usage: ./run-mock-tests.sh <target_dir>
# ==============================================================================

set -eo pipefail

TARGET_DIR="${1:-.}"
TEST_FILE="${TARGET_DIR}/validation.tftest.hcl"
RESULT_FILE="output/artifacts/test-results.json"

mkdir -p "output/artifacts"

echo "=== Initializing Local Mock Validation in: ${TARGET_DIR} ==="

if [ ! -d "${TARGET_DIR}" ]; then
  echo "Error: Target directory '${TARGET_DIR}' does not exist."
  exit 1
fi

# Ensure Terraform CLI exists, fallback gracefully if not
if ! command -v terraform &> /dev/null; then
  echo "Warning: Terraform CLI not found. Generating mock fallback result."
  cat <<EOF > "${RESULT_FILE}"
{
  "status": "skip",
  "test_results": [],
  "summary": {
    "total_files": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 1,
    "tools_not_found": ["terraform"]
  }
}
EOF
  echo "Completed: Terraform CLI missing. Fallback generated."
  exit 0
fi

# Resolve path to migration-config.json relative to the script directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="migration-config.json"
if [ ! -f "${CONFIG_PATH}" ]; then
  CONFIG_PATH="../migration-config.json"
fi
if [ ! -f "${CONFIG_PATH}" ]; then
  CONFIG_PATH="${SCRIPT_DIR}/../migration-config.json"
fi

# Generate mock test suite dynamically using dynamic variables extracted from config
CONFIG_PATH="${CONFIG_PATH}" python3 -c '
import json
import sys
import os

config_path = os.environ.get("CONFIG_PATH", "migration-config.json")
try:
    with open(config_path, "r") as f:
        conf = json.load(f)
except Exception:
    conf = {}

required_tags = conf.get("finops_standards", {}).get("required_tags", ["CostCenter", "Orchestrator"])
cost_center = conf.get("finops_standards", {}).get("default_cost_center", "CC-999-DEVOPS")

hcl_blocks = [
    "mock_provider \"azurerm\" {}",
    "mock_provider \"aws\" {}",
    "mock_provider \"google\" {}",
    "",
    "variables {",
    "  environment_name   = \"dev\"",
    "  vm_size            = \"Standard_B2s\"",
    "  system_node_count  = 1",
    "}",
    "",
    "run \"validate_vm_size\" {",
    "  command = plan",
    "  assert {",
    "    condition     = can(regex(\"^Standard_B\", var.vm_size)) || can(regex(\"^Standard_D2\", var.vm_size))",
    "    error_message = \"Dev/Test environments must use burstable compute SKUs (Standard B-series or D2s_v5).\"",
    "  }",
    "}",
    "",
    "run \"validate_finops_tags\" {",
    "  command = plan"
]

for tag in required_tags:
    if tag == "CostCenter":
        hcl_blocks.append("  assert {")
        hcl_blocks.append("    condition     = lookup(azurerm_resource_group.rg.tags, \"CostCenter\", \"\") == \"" + cost_center + "\"")
        hcl_blocks.append("    error_message = \"All resources must carry the mandatory '\''CostCenter'\'' tag: '\''" + cost_center + "'\''.\"")
        hcl_blocks.append("  }")
    elif tag == "Orchestrator":
        hcl_blocks.append("  assert {")
        hcl_blocks.append("    condition     = lookup(azurerm_resource_group.rg.tags, \"Orchestrator\", \"\") == \"Antigravity-Migration-Factory\"")
        hcl_blocks.append("    error_message = \"All resources must carry the mandatory '\''Orchestrator'\'' tag: '\''Antigravity-Migration-Factory'\''.\"")
        hcl_blocks.append("  }")
    else:
        hcl_blocks.append("  assert {")
        hcl_blocks.append("    condition     = lookup(azurerm_resource_group.rg.tags, \"" + tag + "\", \"\") != \"\"")
        hcl_blocks.append("    error_message = \"All resources must carry the mandatory '\''" + tag + "'\'' tag.\"")
        hcl_blocks.append("  }")

hcl_blocks.append("}")
print("\n".join(hcl_blocks))
' > "${TEST_FILE}"

# Execute validation and tests
cd "${TARGET_DIR}"
echo "Running: terraform init"
terraform init -backend=false > /dev/null 2>&1 || true

echo "Running: terraform fmt check"
FMT_OUTPUT=$(terraform fmt -check -recursive . 2>&1 || true)

echo "Running: terraform validate"
VALIDATE_OUTPUT=$(terraform validate -json 2>&1 || true)

echo "Running: terraform test"
TEST_OUTPUT=$(terraform test 2>&1 || true)
TEST_EXIT=$?

# Clean up local mock suite
rm -f "validation.tftest.hcl"
cd - > /dev/null

# Parse results and output JSON
STATUS="pass"
if [ $TEST_EXIT -ne 0 ] || [[ "${VALIDATE_OUTPUT}" =~ \"valid\"[[:space:]]*:[[:space:]]*false ]]; then
  STATUS="fail"
fi

python3 -c '
import json
import sys
import re

status = sys.argv[1]
fmt_output = sys.argv[2]
validate_output = sys.argv[3]
test_output = sys.argv[4]
target_dir = sys.argv[5]
result_file = sys.argv[6]
test_exit = int(sys.argv[7])

fmt_status = "pass" if not fmt_output.strip() else "fail"
validate_status = "fail" if re.search(r"\"valid\"\s*:\s*false", validate_output) else "pass"
test_status = "pass" if test_exit == 0 else "fail"

result_data = {
  "status": status,
  "test_results": [
    {
      "file": target_dir,
      "type": "terraform",
      "tests": [
        {
          "test": "terraform format",
          "status": fmt_status,
          "output": fmt_output
        },
        {
          "test": "terraform validate",
          "status": validate_status,
          "output": validate_output
        },
        {
          "test": "terraform test (offline mocks)",
          "status": test_status,
          "output": test_output
        }
      ]
    }
  ],
  "summary": {
    "total_files": 1,
    "passed": 1 if status == "pass" else 0,
    "failed": 0 if status == "pass" else 1,
    "skipped": 0,
    "tools_not_found": []
  }
}

with open(result_file, "w") as f:
    json.dump(result_data, f, indent=2)
' "${STATUS}" "${FMT_OUTPUT}" "${VALIDATE_OUTPUT}" "${TEST_OUTPUT}" "${TARGET_DIR}" "${RESULT_FILE}" "${TEST_EXIT}"

echo "=== Mock Validation Completed (Result: ${STATUS}) ==="
