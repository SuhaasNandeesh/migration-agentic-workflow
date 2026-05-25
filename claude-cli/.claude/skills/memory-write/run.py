import os
import json
import argparse
import sys

def write_memory(problem, fix, tags, confidence):
    try:
        # Determine paths relative to the script location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        skill_root = os.path.dirname(base_dir) # .opencode/skills/
        store_root = os.path.join(skill_root, "memory-store")
        
        json_path = os.path.join(store_root, "assets", "structured", "issues.json")
        md_path = os.path.join(store_root, "assets", "docs", "issues_and_fixes.md")
        
        # 1. Append to structured issues.json
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    db = json.load(f)
                if not isinstance(db, list):
                    db = []
            except Exception:
                db = []
        else:
            db = []
            
        record = {
            "problem": problem,
            "fix": fix,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "confidence": confidence
        }
        
        db.append(record)
        
        with open(json_path, 'w') as f:
            json.dump(db, f, indent=2)
        print(f"[✅] Successfully wrote structured memory to: {json_path}")
        
        # 2. Append to Markdown docs/issues_and_fixes.md
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        
        md_entry = f"\n\n### Problem: {problem}\n"
        md_entry += f"- **Fix**: {fix}\n"
        md_entry += f"- **Tags**: {', '.join(record['tags'])}\n"
        md_entry += f"- **Confidence**: {confidence}\n"
        
        with open(md_path, 'a') as f:
            f.write(md_entry)
        print(f"[✅] Successfully appended narrative memory to: {md_path}")
        
    except Exception as e:
        print(f"[-] Error writing memory: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", required=True)
    parser.add_argument("--fix", required=True)
    parser.add_argument("--tags", required=True)
    parser.add_argument("--confidence", default="high")
    args = parser.parse_args()
    
    write_memory(args.problem, args.fix, args.tags, args.confidence)
