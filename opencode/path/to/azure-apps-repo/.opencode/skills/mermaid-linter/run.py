import json
import argparse
import sys
import re

def lint_mermaid(code):
    errors = []
    lines = code.split('\n')
    
    # Basic structural check
    if not any(lines[0].strip().startswith(typ) for typ in ['graph TD', 'graph LR', 'sequenceDiagram', 'pie']):
        errors.append("Diagram must start with a valid chart type (e.g., 'graph TD', 'sequenceDiagram').")
        
    for i, line in enumerate(lines):
        # Check for unescaped characters in node definitions
        if re.search(r'\[.*[<>&].*\]', line) or re.search(r'\(.*[<>&].*\)', line):
            errors.append(f"Line {i+1}: Unescaped HTML/XML characters found in node label: '{line.strip()}'")
            
        # Check for unbalanced brackets (common LLM hallucination)
        if line.count('[') != line.count(']') or line.count('(') != line.count(')'):
            errors.append(f"Line {i+1}: Unbalanced brackets or parentheses: '{line.strip()}'")
            
    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            data = json.load(f)
            
        all_passed = True
        for diagram in data.get('diagrams', []):
            code = diagram.get('code', '')
            errors = lint_mermaid(code)
            
            if errors:
                all_passed = False
                print(f"ERROR in diagram '{diagram.get('name')}':")
                for e in errors:
                    print(f"  - {e}")
                    
        if not all_passed:
            sys.exit(1)
        else:
            print("All Mermaid diagrams passed validation.")
            sys.exit(0)
            
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        sys.exit(1)
