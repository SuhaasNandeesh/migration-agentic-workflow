import os
import sys
import argparse
import re
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Attempt to load tree-sitter bindings
try:
    import tree_sitter
    import tree_sitter_hcl
    import tree_sitter_python
    import tree_sitter_yaml
    import tree_sitter_go
    import tree_sitter_javascript
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logging.warning("Tree-sitter libraries or grammar bindings are missing. Please run './install-dev-tools.sh' to install required dependencies. Falling back to regex folding.")

# Global cache for compiled tree-sitter grammars
GRAMMARS = {}

def get_grammar(lang_name):
    """Dynamically loads tree-sitter grammars as needed, returning None on failure"""
    if lang_name in GRAMMARS:
        return GRAMMARS[lang_name]
        
    try:
        from tree_sitter import Language
        if lang_name == "hcl":
            import tree_sitter_hcl
            lang = Language(tree_sitter_hcl.language())
        elif lang_name == "python":
            import tree_sitter_python
            lang = Language(tree_sitter_python.language())
        elif lang_name == "yaml":
            import tree_sitter_yaml
            lang = Language(tree_sitter_yaml.language())
        elif lang_name == "go":
            import tree_sitter_go
            lang = Language(tree_sitter_go.language())
        elif lang_name == "javascript":
            import tree_sitter_javascript
            lang = Language(tree_sitter_javascript.language())
        else:
            lang = None
            
        GRAMMARS[lang_name] = lang
        return lang
    except Exception as e:
        logging.warning(f"Failed to load tree-sitter grammar for '{lang_name}': {e}.")
        GRAMMARS[lang_name] = None
        return None

def get_braces_span(node):
    # Find all descendants that are "{" and "}"
    braces = []
    def collect(n):
        if n.type in ("{", "}"):
            braces.append(n)
        for child in n.children:
            collect(child)
            
    collect(node)
    
    first_open = None
    last_close = None
    for b in braces:
        if b.type == "{" and first_open is None:
            first_open = b
        elif b.type == "}":
            last_close = b
            
    if first_open and last_close and first_open.end_byte <= last_close.start_byte:
        return first_open.end_byte, last_close.start_byte
    return None

def fold_with_treesitter(content: str, ext: str) -> str:
    """
    Parses content using tree-sitter and returns a structurally folded string.
    Supports HCL, Python, Go, JS/TS, and YAML natively.
    """
    # Map file extension to grammar language
    ext_map = {
        ".tf": "hcl",
        ".py": "python",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".go": "go",
        ".js": "javascript",
        ".ts": "javascript"
    }
    
    lang_name = ext_map.get(ext)
    if not lang_name:
        raise ValueError(f"No grammar mapping for extension: {ext}")
        
    grammar = get_grammar(lang_name)
    if not grammar:
        raise RuntimeError(f"Grammar loading failed or not installed for language: {lang_name}")
        
    from tree_sitter import Parser
    parser = Parser(grammar)
    
    tree = parser.parse(content.encode('utf-8'))
    
    candidates = []
    
    def traverse(node):
        # 1. HCL block
        if lang_name == "hcl" and node.type == "block":
            span = get_braces_span(node)
            if span:
                start, end = span
                body_text = content[start:end]
                line_count = body_text.count('\n')
                if line_count > 5:
                    start_line = content.count('\n', 0, start) + 1
                    end_line = content.count('\n', 0, end) + 1
                    candidates.append((start, end, "hcl_block", start_line, end_line))
                    return
        # 2. Python class or function block
        elif lang_name == "python" and node.type in ("class_definition", "function_definition"):
            block_child = None
            for child in node.children:
                if child.type == "block":
                    block_child = child
                    break
            if block_child:
                body_text = content[block_child.start_byte:block_child.end_byte]
                line_count = body_text.count('\n')
                if line_count > 6:
                    start_line = content.count('\n', 0, block_child.start_byte) + 1
                    end_line = content.count('\n', 0, block_child.end_byte) + 1
                    candidates.append((block_child.start_byte, block_child.end_byte, "python_block", start_line, end_line))
                    return
        # 3. Go or Javascript brace-based block (functions/classes)
        elif lang_name in ("go", "javascript") and node.type in (
            "function_declaration", "method_declaration", "method_definition", "class_declaration", "arrow_function"
        ):
            span = get_braces_span(node)
            if span:
                start, end = span
                body_text = content[start:end]
                line_count = body_text.count('\n')
                if line_count > 6:
                    start_line = content.count('\n', 0, start) + 1
                    end_line = content.count('\n', 0, end) + 1
                    candidates.append((start, end, "brace_block", start_line, end_line))
                    return
        # 4. YAML mapping or sequence block
        elif lang_name == "yaml" and node.type in ("block_mapping", "block_sequence"):
            body_text = content[node.start_byte:node.end_byte]
            line_count = body_text.count('\n')
            if line_count > 5:
                if node.parent and node.parent.type == "block_mapping_pair":
                    start_line = content.count('\n', 0, node.start_byte) + 1
                    end_line = content.count('\n', 0, node.end_byte) + 1
                    candidates.append((node.start_byte, node.end_byte, "yaml_block", start_line, end_line))
                    return
                    
        for child in node.children:
            traverse(child)
            
    traverse(tree.root_node)
    
    candidates.sort(key=lambda x: x[0])
    active_ranges = []
    current_end = -1
    for start, end, node_type, s_line, e_line in candidates:
        if start >= current_end:
            active_ranges.append((start, end, node_type, s_line, e_line))
            current_end = end
            
    active_ranges.sort(key=lambda x: x[0], reverse=True)
    
    result = content
    for start, end, node_type, s_line, e_line in active_ranges:
        line_count = e_line - s_line + 1
        line_start = content.rfind('\n', 0, start) + 1
        indent = ""
        m_indent = re.match(r'^([ \t]*)', content[line_start:])
        if m_indent:
            indent = m_indent.group(1)
            
        if node_type == "python_block":
            placeholder = f"\n{indent}pass # ... [Folded Python Block: lines {s_line}-{e_line} - {line_count} lines folded for context protection]\n"
        elif node_type == "hcl_block":
            placeholder = f"\n{indent}  # ... [Folded Block: lines {s_line}-{e_line} - {line_count} lines folded for context protection]\n{indent}"
        elif node_type == "yaml_block":
            placeholder = f"\n{indent}  # ... [Folded YAML Block: lines {s_line}-{e_line} - {line_count} lines folded for context protection]\n"
        else:
            placeholder = f"\n{indent}  // ... [Folded Block: lines {s_line}-{e_line} - {line_count} lines folded for context protection]\n{indent}"
            
        result = result[:start] + placeholder + result[end:]
        
    return result

def fold_hcl_brackets(content: str) -> str:
    """
    Folds an HCL file by parsing matching curly braces {}.
    Preserves top-level block signatures and folds their interior bodies.
    """
    lines = content.splitlines()
    folded_lines = []
    i = 0
    total_lines = len(lines)
    
    block_header_re = re.compile(r'^\s*(resource|module|variable|output|data|locals|terraform|provider)\b')

    while i < total_lines:
        line = lines[i]
        if block_header_re.match(line) and '{' in line:
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
            
            if brace_count == 0 and len(block_body_lines) > 5:
                folded_lines.append(header)
                folded_lines.append(f"  # ... [Folded Block: lines {start_index+2}-{j} - {len(block_body_lines)} lines folded for context protection]")
                folded_lines.append("}")
                i = j - 1
            else:
                folded_lines.append(line)
        else:
            folded_lines.append(line)
        i += 1
        
    return "\n".join(folded_lines)

def fold_python_indentation(content: str) -> str:
    """
    Folds Python/YAML files by tracking def/class/key indentations.
    """
    lines = content.splitlines()
    folded_lines = []
    i = 0
    total_lines = len(lines)
    
    while i < total_lines:
        line = lines[i]
        stripped = line.strip()
        
        if stripped.endswith(":") and not stripped.startswith("#") and not stripped.startswith("//"):
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
                folded_lines.append(" " * (indent + 4) + f"# ... [Folded Block: lines {i+2}-{j} - {len(body_lines)} lines folded for context protection]")
                i = j - 1
            else:
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
    folded_content = None
    
    # 1. Try Tree-sitter folding with full DevOps scope
    if TREE_SITTER_AVAILABLE:
        try:
            folded_content = fold_with_treesitter(content, ext)
            logging.info("Successfully generated stub using tree-sitter AST parser.")
        except Exception as e:
            logging.warning(f"Tree-sitter folding failed for {file_path}: {e}. Falling back to text-based folding.")
            
    # 2. Resilient Text-based Fallbacks if Tree-sitter is missing or fails
    if folded_content is None:
        if ext in (".py", ".yaml", ".yml"):
            folded_content = fold_python_indentation(content)
        elif ext in (".tf", ".hcl"):
            folded_content = fold_hcl_brackets(content)
        else:
            folded_content = fold_hcl_brackets(content)
            
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
        
    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line)
    
    snippet = "".join(lines[start_idx:end_idx])
    
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
        
    clean_target = block_name.replace('"', '').replace("'", "").replace(" ", "")
    
    lines = content.splitlines()
    total_lines = len(lines)
    i = 0
    found = False
    
    while i < total_lines:
        line = lines[i]
        clean_line = line.replace('"', '').replace("'", "").replace(" ", "")
        
        if clean_target in clean_line and '{' in line:
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
