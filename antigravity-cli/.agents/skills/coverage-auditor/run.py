import json
import argparse
import sys
import os

def audit_coverage(dependency_file, specs_file, flows_file):
    try:
        # Load Baseline Census
        with open(dependency_file, 'r') as f:
            dep_data = json.load(f)
            baseline_files = set(dep_data.get('baseline_census_files', []))
            
        # Load LLM Coverage Tags
        covered_files = set()
        
        try:
            with open(specs_file, 'r') as f:
                specs_data = json.load(f)
                for spec in specs_data.get('specs', []):
                    covered_files.update(spec.get('files_covered', []))
        except FileNotFoundError:
            pass # It's okay if it doesn't exist yet
            
        try:
            with open(flows_file, 'r') as f:
                flows_data = json.load(f)
                for flow in flows_data.get('pipelines', []):
                    covered_files.update(flow.get('files_covered', []))
        except FileNotFoundError:
            pass
            
        # Calculate Reconciliation Math
        if not baseline_files:
            print("Warning: Baseline census is empty.")
            sys.exit(0)
            
        missing_files = baseline_files - covered_files
        coverage_percent = (len(baseline_files) - len(missing_files)) / len(baseline_files) * 100
        
        print(f"Coverage: {coverage_percent:.2f}%")
        
        # Load Threshold from gate-thresholds.json dynamically
        threshold = 95.0
        try:
            # Check several possible path layers relative to dependency_file or current working dir
            possible_paths = [
                os.path.abspath(os.path.join(os.path.dirname(dependency_file), "..", "..", "..", "validation", "gate-thresholds.json")),
                os.path.abspath(os.path.join(os.path.dirname(dependency_file), "..", "..", "validation", "gate-thresholds.json")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "validation", "gate-thresholds.json")),
                os.path.abspath(os.path.join(os.getcwd(), "validation", "gate-thresholds.json")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "validation", "gate-thresholds.json"))
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    with open(p, 'r') as tf:
                        tdata = json.load(tf)
                        val = tdata.get("completeness", {}).get("thresholds", {}).get("min_file_coverage_percent")
                        if val is not None:
                            threshold = float(val)
                            print(f"Loaded dynamic completeness threshold: {threshold}%")
                            break
        except Exception as te:
            print(f"Warning: Could not load gate-thresholds.json: {str(te)}. Falling back to default {threshold}% threshold.")
        
        # Dynamic Threshold Check
        if coverage_percent < threshold:
            print(f"STATUS: FAIL - Coverage below {threshold}% threshold.")
            print("Missing files that must be documented:")
            for m in missing_files:
                print(f" - {m}")
            sys.exit(1)
        else:
            print(f"STATUS: PASS - Coverage meets or exceeds {threshold}% threshold.")
            if missing_files:
                print("Note: The following files were skipped but are within threshold allowance:")
                for m in missing_files:
                    print(f" - {m}")
            sys.exit(0)

    except Exception as e:
        print(f"Audit failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--deps", required=True)
    parser.add_argument("--specs", required=True)
    parser.add_argument("--flows", required=True)
    args = parser.parse_args()
    
    audit_coverage(args.deps, args.specs, args.flows)
