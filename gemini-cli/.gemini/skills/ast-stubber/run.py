import os
import sys
import argparse
import re
import logging
import subprocess

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Attempt to load tree-sitter bindings; auto-install if missing (mirroring dep-graph-builder)
try:
    import tree_sitter
    import tree_sitter_hcl
    TREE_SITTER_AVAILABLE = True
except ImportError:
    try:
        req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        if os.path.exists(req_path):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import tree_sitter
            import tree_sitter_hcl
            TREE_SITTER_AVAILABLE = True
        else:
            TREE_SITTER_AVAILABLE = False
    except Exception:
        TREE_SITTER_AVAILABLE = False

def fold_hcl_brackets(content: str) -> str:
    """
    Folds an HCL file by parsing matching curly braces {}.
    Preserves top-level block signatures and folds their interior bodies.
    """
    lines = content.splitlines()
    folded_lines = []
    i = 0
    total_lines = len(lines)
    
    # Matches patterns like: resource "aws_instance" "web" {
    # or: variable "name" {
    # or: module "vpc" {
    block_header_re = re.compile(r'^\s*(resource|module|variable|output|data|locals|terraform|provider)\b')

    while i < total_lines:
        line = lines[i]
        stripped = line.strip()
        
        # Check if line starts a major block
        if block_header_re.match(line) and '{' in line:
            # We found a block start. Let's find its matching closing brace
            header = line.split('{')[0] + '{'
            brace_count = 1
            start_index = i
            j = i + 1
            block_body_lines = []
            
            while j < total_lines and brace_count > 0:
                body_line = lines[j]
                brace_count += body_line.count('{')
                brace_count -= body_line.count('}')
                if brace_count > 0:
                    block_body_lines.append(body_line)
                j += 1
            
            # If successfully found matching closing brace and block is large
            if brace_count == 0 and len(block_body_lines) > 5:
                folded_lines.append(header)
                folded_lines.append(f"  # ... [Folded Block: lines {start_index+2}-{j} - {len(block_body_lines)} lines folded for context protection]")
                folded_lines.append("}")
                i = j - 1
            else:
                # Small block or unmatched brace, do not fold
                folded_lines.append(line)
        else:
            folded_lines.append(line)
        i += 1
        
    return "\n".join(folded_lines)

def fold_python_indentation(content: str) -> str:
    """
    Folds Python files by tracking def/class indentations.
    """
    lines = content.splitlines()
    folded_lines = []
    i = 0
    total_lines = len(lines)
    
    while i < total_lines:
        line = lines[i]
        stripped = line.strip()
        
        # Match class or function definitions
        if (stripped.startswith("def ") or stripped.startswith("class ")) and line.endswith(":"):
            header = line
            indent = len(line) - len(line.lstrip())
            folded_lines.append(header)
            
            j = i + 1
            body_lines = []
            while j < total_lines:
                curr_line = lines[j]
                if not curr_line.strip():
                    body_lines.append(curr_line)
                    j += 1
                    continue
                curr_indent = len(curr_line) - len(curr_line.lstrip())
                if curr_indent <= indent:
                    break
                body_lines.append(curr_line)
                j += 1
                
            if len(body_lines) > 6:
                # Fold the body
                folded_lines.append(" " * (indent + 4) + f"# ... [Folded Python Block: lines {i+2}-{j} - {len(body_lines)} lines folded for context protection]")
                i = j - 1
            else:
                # Do not fold small blocks
                folded_lines.extend(body_lines)
                i = j - 1
        else:
            folded_lines.append(line)
        i += 1
        
    return "\n".join(folded_lines)

def generate_stub(file_path: str, output_path: str):
    """Reads raw source file, creates a folded structural outline stub, and writes to disk."""
    if not os.path.exists(file_path):
        logging.error(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".tf":
        folded_content = fold_hcl_brackets(content)
    elif ext == ".py":
        folded_content = fold_python_indentation(content)
    else:
        # Generic folding (brackets fallback)
        folded_content = fold_hcl_brackets(content)
        
    # Write header comment indicating it is an AST structural stub
    stub_header = f"# AST STRUCTURAL STUB FILE\n# Generated from original: {file_path}\n# DO NOT modify this stub file directly. Use '--hydrate' to read raw sections.\n\n"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(stub_header + folded_content)
        
    logging.info(f"Successfully generated AST stub file at: {output_path}")

def hydrate_by_range(file_path: str, start_line: int, end_line: int):
    """Extracts and prints the exact raw code segment from the source file."""
    if not os.path.exists(file_path):
        logging.error(f"Error: Base file '{file_path}' does not exist.")
        sys.exit(1)
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    # Standardize to 0-indexed bounds checking
    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line)
    
    snippet = "".join(lines[start_idx:end_idx])
    
    # Output raw snippet to stdout
    print(f"\n--- HYDRATION BOUNDARY: LINES {start_line}-{end_line} ---")
    sys.stdout.write(snippet)
    print("--- END HYDRATION BOUNDARY ---\n")

def hydrate_by_block_name(file_path: str, block_name: str):
    """Searches for a block signature in the raw file and hydrates it."""
    if not os.path.exists(file_path):
        logging.error(f"Error: Base file '{file_path}' does not exist.")
        sys.exit(1)
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Search for matching block signature (e.g. resource "aws_instance" "web", or module "vpc")
    # Clean symbol spaces for fuzzy matching
    clean_target = block_name.replace('"', '').replace("'", "").replace(" ", "")
    
    lines = content.splitlines()
    total_lines = len(lines)
    i = 0
    found = False
    
    while i < total_lines:
        line = lines[i]
        clean_line = line.replace('"', '').replace("'", "").replace(" ", "")
        
        if clean_target in clean_line and '{' in line:
            # Found block signature block start. Let's capture the whole block.
            start_line = i + 1
            brace_count = 1
            j = i + 1
            
            while j < total_lines and brace_count > 0:
                body_line = lines[j]
                brace_count += body_line.count('{')
                brace_count -= body_line.count('}')
                j += 1
                
            hydrate_by_range(file_path, start_line, j)
            found = True
            break
            
        elif (line.strip().startswith("def ") or line.strip().startswith("class ")) and block_name in line:
            # Python class or function start
            start_line = i + 1
            indent = len(line) - len(line.lstrip())
            j = i + 1
            
            while j < total_lines:
                curr_line = lines[j]
                if not curr_line.strip():
                    j += 1
                    continue
                curr_indent = len(curr_line) - len(curr_line.lstrip())
                if curr_indent <= indent:
                    break
                j += 1
                
            hydrate_by_range(file_path, start_line, j)
            found = True
            break
            
        i += 1
        
    if not found:
        print(f"\n[ERROR] Symbol / Block '{block_name}' not found in '{file_path}'. Falling back to full file read.")
        hydrate_by_range(file_path, 1, len(lines))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AST Code Stubber & JIT Hydrator Utility")
    parser.add_argument("--file", required=True, help="Path to raw source file")
    parser.add_argument("--output", help="Output path for folded stub (required for --stub)")
    parser.add_argument("--stub", action="store_true", help="Generate a minified structural stub")
    parser.add_argument("--hydrate", action="store_true", help="Hydrate/expand a folded block from original source")
    parser.add_argument("--line-range", help="Line range to hydrate (format: start-end, e.g. 120-165)")
    parser.add_argument("--block-name", help="Resource or function symbol identifier to hydrate")
    
    args = parser.parse_args()
    
    if args.stub:
        if not args.output:
            parser.error("--output is required when generating a stub (--stub)")
        generate_stub(args.file, args.output)
        
    elif args.hydrate:
        if args.line_range:
            try:
                start, end = map(int, args.line_range.split("-"))
                hydrate_by_range(args.file, start, end)
            except ValueError:
                parser.error("Invalid line range format. Must be start-end (e.g. 120-165)")
        elif args.block_name:
            hydrate_by_block_name(args.file, args.block_name)
        else:
            parser.error("Either --line-range or --block-name is required for hydration")
    else:
        parser.error("Specify either --stub or --hydrate")
