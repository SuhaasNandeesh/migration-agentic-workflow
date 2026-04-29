import os
import json
import argparse
import glob

def build_graph(source_dir):
    categories = {
        "infrastructure": [],
        "orchestration": [],
        "pipelines": [],
        "app_logic": [],
        "monorepo_packages": []
    }
    baseline_census = []
    
    # Simple monorepo detection
    for root, dirs, files in os.walk(source_dir):
        if "package.json" in files or "go.mod" in files or "Cargo.toml" in files or "pom.xml" in files:
            # Avoid root if it's just the wrapper
            if root != source_dir:
                categories["monorepo_packages"].append(root)

        for f in files:
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, source_dir)
            
            # Skip hidden folders and outputs
            if "/." in path or "node_modules" in path or "DocumentationFactory/output" in path:
                continue
                
            baseline_census.append(rel_path)
                
            if f.endswith(".tf"):
                categories["infrastructure"].append(rel_path)
            elif f.endswith(".yaml") or f.endswith(".yml"):
                if "deployment" in f.lower() or "service" in f.lower() or "k8s" in path:
                    categories["orchestration"].append(rel_path)
                elif "action" in f.lower() or "pipeline" in f.lower() or "gitlab-ci" in f.lower():
                    categories["pipelines"].append(rel_path)
            elif "jenkinsfile" in f.lower() or "makefile" in f.lower():
                categories["pipelines"].append(rel_path)
            elif f.endswith(".py") or f.endswith(".js") or f.endswith(".ts") or f.endswith(".go") or f.endswith(".java") or f.endswith(".rs"):
                categories["app_logic"].append(rel_path)
                
    return {"categories": categories, "dependencies": [], "baseline_census_files": baseline_census}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    graph = build_graph(args.source)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(graph, f, indent=2)
    print(f"Graph written to {args.output}")
