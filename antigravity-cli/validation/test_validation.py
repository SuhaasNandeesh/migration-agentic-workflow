#!/usr/bin/env python3
"""
Integration Test Suite for Offline Data-Contract & Validation Framework
------------------------------------------------------------------------
Tests validate_schemas.py, resource_delta_analyzer.py, and run-mock-tests.sh.
"""

import os
import sys
import json
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")
TEMP_TEST_DIR = os.path.join(BASE_DIR, "temp_test_run")

def setup_temp_dir():
    if os.path.exists(TEMP_TEST_DIR):
        shutil.rmtree(TEMP_TEST_DIR)
    os.makedirs(TEMP_TEST_DIR, exist_ok=True)

def cleanup_temp_dir():
    if os.path.exists(TEMP_TEST_DIR):
        shutil.rmtree(TEMP_TEST_DIR)

def test_schema_validator():
    print("[*] Running Schema Validator Tests...")
    schema_path = os.path.join(SCHEMAS_DIR, "source-inventory-schema.json")
    validate_script = os.path.join(BASE_DIR, "validate_schemas.py")

    # 1. Valid Input test
    valid_data = {
        "source_platform": "aws",
        "inventory": {
            "infrastructure": [
                {
                    "file": "main.tf",
                    "type": "terraform",
                    "provider": "aws",
                    "resources": [
                        {
                            "resource_type": "aws_instance",
                            "name": "web",
                            "key_config": {},
                            "dependencies": []
                        }
                    ]
                }
            ]
        },
        "categories": {
            "compute": {
                "files": ["main.tf"],
                "resources": ["aws_instance.web"],
                "count": 1
            }
        },
        "dependency_graph": {},
        "statistics": {
            "total_files": 1,
            "total_resources": 1,
            "by_category": {"compute": 1},
            "unrecognized_files": []
        }
    }

    valid_json_path = os.path.join(TEMP_TEST_DIR, "valid-inventory.json")
    with open(valid_json_path, 'w') as f:
        json.dump(valid_data, f, indent=2)

    # Run validation on valid input
    cmd = [sys.executable, validate_script, valid_json_path, schema_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Expected returncode 0 for valid JSON, got {res.returncode}. Output:\n{res.stdout}\nError:\n{res.stderr}"
    print("[✅] Valid schema validation passed successfully!")

    # 2. Invalid Input test (Missing required categories and statistics)
    invalid_data = {
        "source_platform": "aws",
        "inventory": {
            "infrastructure": [
                {
                    "file": "main.tf",
                    "type": "terraform",
                    "provider": "aws",
                    "resources": [
                        {
                            "resource_type": "aws_instance",
                            "name": "web"
                        }
                    ]
                }
            ]
        }
    }
    
    invalid_json_path = os.path.join(TEMP_TEST_DIR, "invalid-inventory.json")
    with open(invalid_json_path, 'w') as f:
        json.dump(invalid_data, f, indent=2)

    cmd = [sys.executable, validate_script, invalid_json_path, schema_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode != 0, f"Expected non-zero returncode for invalid JSON, got {res.returncode}"
    assert "Missing required field" in res.stdout, f"Expected 'Missing required field' in output, got:\n{res.stdout}"
    print("[✅] Invalid schema validation correctly failed and identified errors!")

def test_resource_delta_analyzer():
    print("[*] Running Resource Delta Analyzer Tests...")
    analyzer_script = os.path.join(BASE_DIR, "resource_delta_analyzer.py")

    mock_diff = """diff --git a/terraform/main.tf b/terraform/main.tf
index 515867b..c1fb4b6 100644
--- a/terraform/main.tf
+++ b/terraform/main.tf
@@ -10,12 +10,12 @@
-resource "aws_instance" "old_web" {
-  ami           = "ami-12345"
-  instance_type = "t2.micro"
-}
+resource "azurerm_linux_virtual_machine" "new_web" {
+  name                = "web-server"
+  resource_group_name = azurerm_resource_group.rg.name
+  size                = "Standard_B2s"
+  admin_username      = "adminuser"
+  tags = {
+    Environment = "dev"
+    CostCenter  = "CC-999-DEVOPS"
+  }
+}
+
+module "network" {
+  source = "./modules/network"
+}
diff --git a/kubernetes/deployment.yaml b/kubernetes/deployment.yaml
--- a/kubernetes/deployment.yaml
+++ b/kubernetes/deployment.yaml
-kind: Service
-metadata:
-  name: old-service
+kind: Deployment
+metadata:
+  name: new-deployment
"""
    diff_path = os.path.join(TEMP_TEST_DIR, "mock.diff")
    with open(diff_path, 'w') as f:
        f.write(mock_diff)

    output_summary_path = os.path.join(TEMP_TEST_DIR, "delta-summary.md")
    
    cmd = [sys.executable, analyzer_script, diff_path, output_summary_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Expected delta analyzer returncode 0, got {res.returncode}. Output: {res.stdout}"
    
    assert os.path.exists(output_summary_path), "Expected output markdown summary file to be created"
    with open(output_summary_path, 'r') as f:
        summary_content = f.read()

    print("--- Delta Summary Output ---")
    print(summary_content)
    print("----------------------------")

    assert "File:" in summary_content
    assert "Added" in summary_content
    assert "Removed" in summary_content
    assert "Modified" in summary_content
    assert "resource `azurerm_linux_virtual_machine.new_web`" in summary_content
    assert "resource `aws_instance.old_web`" in summary_content
    assert "module `network`" in summary_content
    assert "property `size`" in summary_content
    assert "property `tags`" in summary_content
    assert "Kubernetes resource `Deployment.new-deployment`" in summary_content
    assert "Kubernetes resource `Service.old-service`" in summary_content


    print("[✅] Resource Delta Analyzer successfully parsed the diff and extracted changes!")

def test_mock_test_runner():
    print("[*] Running Mock Test Runner Tests...")
    runner_script = os.path.join(BASE_DIR, "run-mock-tests.sh")

    # Establish mock target terraform directory
    mock_tf_dir = os.path.join(TEMP_TEST_DIR, "terraform_src")
    os.makedirs(mock_tf_dir, exist_ok=True)

    # Let's create a minimal main.tf in the mock directory
    main_tf_content = """
resource "azurerm_resource_group" "rg" {
  name     = "rg-dev-migration"
  location = "eastus"
  tags = {
    Environment  = "dev"
    CostCenter   = "CC-999-DEVOPS"
    Orchestrator = "Antigravity-Migration-Factory"
    MigrationSource = "aws"
  }
}
"""
    with open(os.path.join(mock_tf_dir, "main.tf"), 'w') as f:
        f.write(main_tf_content)

    # Run the test runner script using bash
    # First, let's copy migration-config.json into a place where the script can find it
    # The script looks at: migration-config.json, ../migration-config.json, or /Users/username/Code/mygit/oc-cli-agentic-workflow/migration-agentic-workflow/opencode/migration-config.json
    # It will find it at /Users/username/Code/mygit/oc-cli-agentic-workflow/migration-agentic-workflow/opencode/migration-config.json automatically
    
    cmd = ["bash", runner_script, mock_tf_dir]
    
    # We must run it from BASE_DIR since the script outputs results to "output/artifacts"
    # which is relative to the current working directory of the command execution
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    
    # Let's print output
    print("--- Test Runner Output ---")
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
    print("--------------------------")

    # The script outputs results to BASE_DIR/output/artifacts/test-results.json
    results_path = os.path.join(BASE_DIR, "output", "artifacts", "test-results.json")
    if not os.path.exists(results_path):
        print(f"[❌] Error: Expected test results JSON at {results_path} was not found!")
        sys.exit(1)

    with open(results_path, 'r') as f:
        test_results = json.load(f)

    print("Test Results JSON:")
    print(json.dumps(test_results, indent=2))

    assert "status" in test_results
    assert test_results["status"] in ["pass", "fail", "skip"]
    
    print("[✅] Parameterized Mock Test Runner executed successfully!")

def main():
    setup_temp_dir()
    try:
        test_schema_validator()
        print("")
        test_resource_delta_analyzer()
        print("")
        test_mock_test_runner()
        print("\n[🎉] All integration tests passed successfully!")
    finally:
        cleanup_temp_dir()

if __name__ == "__main__":
    main()
