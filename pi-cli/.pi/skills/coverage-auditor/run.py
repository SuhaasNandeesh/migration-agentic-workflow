import json
import argparse
import sys
import os

def audit_coverage(dependency_file, specs_file, flows_file, wave=None, plan_file=None):
    try:
        # Load Baseline Census
        with open(dependency_file, 'r') as f:
            dep_data = json.load(f)
            baseline_files = set(dep_data.get('baseline_census_files', []))

        # Filter baseline census files by progressive wave boundaries if wave is specified
        if wave is not None:
            # Auto-detect plan file if not provided
            if not plan_file:
                possible_plans = [
                    "DocumentationFactory/output/artifacts/doc-execution-plan.json",
                    "output/artifacts/execution-plan.json",
                    "DocumentationFactory/output/artifacts/execution-plan.json",
                    "output/artifacts/doc-execution-plan.json",
                    os.path.abspath(os.path.join(os.path.dirname(dependency_file), "doc-execution-plan.json")),
                    os.path.abspath(os.path.join(os.path.dirname(dependency_file), "execution-plan.json")),
                ]
                for p in possible_plans:
                    if os.path.exists(p):
                        plan_file = p
                        break
            
            if plan_file and os.path.exists(plan_file):
                print(f"Loading wave plan from: {plan_file}")
                try:
                    with open(plan_file, 'r') as pf:
                        plan_data = json.load(pf)
                    
                    # Resolve wave number (optionally auto-detect from pipeline-state.json)
                    actual_wave = None
                    if str(wave).lower() == 'auto':
                        state_paths = [
                            "output/pipeline-state.json",
                            "DocumentationFactory/output/pipeline-state.json",
                            "pipeline-state.json"
                        ]
                        state_file = None
                        for sp in state_paths:
                            if os.path.exists(sp):
                                state_file = sp
                                break
                        if state_file:
                            with open(state_file, 'r') as sf:
                                state_data = json.load(sf)
                            
                            # Determine active wave from completed/running categories
                            waves_list = state_data.get("waves", [])
                            for w in waves_list:
                                w_num = w.get("wave")
                                categories = w.get("categories", [])
                                if any(cat.get("developer") in ["completed", "running"] or cat.get("status") in ["completed", "running"] for cat in categories):
                                    actual_wave = w_num
                            if actual_wave is None:
                                actual_wave = 1
                            print(f"Auto-detected active wave from state: {actual_wave}")
                        else:
                            print("Warning: Could not find pipeline-state.json for auto wave detection. Defaulting to Wave 1.")
                            actual_wave = 1
                    else:
                        actual_wave = int(wave)

                    print(f"Auditing progressive coverage up to Wave {actual_wave}")
                    progressive_files = set()
                    for w in plan_data.get('waves', []):
                        w_num = w.get('wave_number')
                        if w_num is None:
                            w_num = w.get('wave')
                        if w_num is not None and int(w_num) <= actual_wave:
                            progressive_files.update(w.get('files', []))
                    
                    if progressive_files:
                        baseline_files = baseline_files.intersection(progressive_files)
                        print(f"Baseline census filtered to {len(baseline_files)} files for progressive Wave {actual_wave}")
                    else:
                        print(f"Warning: No files found in plan for waves <= {actual_wave}. Using full baseline census.")
                except Exception as pe:
                    print(f"Warning: Error parsing plan file: {str(pe)}. Falling back to full baseline census.")
            else:
                print(f"Warning: Plan file not found. Falling back to full baseline census.")
            
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
    parser.add_argument("--wave", default=None, help="Current wave number or 'auto'")
    parser.add_argument("--plan", default=None, help="Path to execution plan JSON file")
    args = parser.parse_args()
    
    audit_coverage(args.deps, args.specs, args.flows, args.wave, args.plan)
