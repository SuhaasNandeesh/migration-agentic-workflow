import json
import argparse
import sys
import re

def lint_mermaid(code):
    errors = []
    raw_lines = code.split('\n')
    
    # Filter out leading blank lines and comments to locate the true declaration line
    first_dec_line = ""
    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("%%"):
            continue
        first_dec_line = stripped
        break
        
    if not first_dec_line:
        errors.append("Diagram is empty or contains only comments.")
        return errors
        
    # Check against a comprehensive list of standard Mermaid chart headers
    valid_types = [
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
        'stateDiagram-v2', 'erDiagram', 'gantt', 'pie', 'gitGraph', 
        'C4Context', 'C4Container', 'C4Component'
    ]
    if not any(first_dec_line.startswith(typ) for typ in valid_types):
        errors.append(f"Diagram must start with a valid chart type (e.g., 'graph TD', 'flowchart LR', 'sequenceDiagram'). Got: '{first_dec_line}'")
        
    for i, line in enumerate(raw_lines):
        stripped_line = line.strip()
        # Skip comment lines for validation checking
        if stripped_line.startswith("%%"):
            continue
            
        # Check for unescaped HTML/XML characters inside node definitions
        # A node definition looks like ID[label] or ID(label). Extract and validate labels.
        brackets = re.findall(r'\[([^\]]+)\]|\(([^)]+)\)', line)
        for b_sq, b_rd in brackets:
            label = b_sq or b_rd
            if label.startswith('"') and label.endswith('"'):
                continue
            if any(char in label for char in ['<', '>', '&']):
                errors.append(f"Line {i+1}: Unescaped HTML/XML characters found in node label: '{stripped_line}'")
            
        # Check for unbalanced brackets (only in active code lines)
        if line.count('[') != line.count(']') or line.count('(') != line.count(')'):
            errors.append(f"Line {i+1}: Unbalanced brackets or parentheses: '{stripped_line}'")
            
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
