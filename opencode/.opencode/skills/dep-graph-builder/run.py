import os
import json
import argparse
import logging
import sys
import re

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Attempt to load tree-sitter bindings
try:
    import tree_sitter
    import tree_sitter_hcl
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logging.warning("Tree-sitter libraries or HCL grammar bindings are missing. Please run './install-dev-tools.sh' to install required dependencies. Falling back to Regex mode.")


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
        logging.warning(f"Failed to load tree-sitter grammar for '{lang_name}': {e}. Falling back to Regex.")
        GRAMMARS[lang_name] = None
        return None

# ==========================================
# 1. HCL / Terraform Extractor
# ==========================================
def extract_hcl_treesitter(filepath, lang):
    from tree_sitter import Parser
    deps = []
    try:
        parser = Parser()
        parser.language = lang
        with open(filepath, 'rb') as f:
            code = f.read()
        tree = parser.parse(code)
        
        def traverse(node):
            if node.type == "block":
                if len(node.children) > 0 and node.children[0].type == "identifier" and node.children[0].text.decode('utf8') == "module":
                    module_name = ""
                    if len(node.children) > 1:
                        module_name = node.children[1].text.decode('utf8').strip('"\'')
                    source_val = find_source_val(node)
                    if source_val:
                        deps.append({
                            "source": filepath,
                            "target": source_val,
                            "relationship": "calls_module",
                            "module_name": module_name
                        })
            for child in node.children:
                traverse(child)
                
        def find_source_val(node):
            if node.type == "attribute":
                key_node = None
                val_node = None
                for c in node.children:
                    if c.type in ("identifier", "attribute_key"):
                        key_node = c
                    elif c.type in ("expression", "string_lit", "literal_value", "template_literal"):
                        val_node = c
                if key_node and key_node.text.decode('utf8') == "source" and val_node:
                    return val_node.text.decode('utf8').strip('"\'')
            for child in node.children:
                res = find_source_val(child)
                if res:
                    return res
            return None

        traverse(tree.root_node)
    except Exception as e:
        logging.error(f"HCL tree-sitter parse error for {filepath}: {e}")
        return extract_hcl_regex(filepath)
    return deps

def extract_hcl_regex(filepath):
    deps = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        blocks = re.findall(r'module\s+["\']([^"\']+)["\']\s*\{([^}]+)\}', content, re.DOTALL)
        for name, body in blocks:
            match = re.search(r'source\s*=\s*["\']([^"\']+)["\']', body)
            if match:
                deps.append({
                    "source": filepath,
                    "target": match.group(1),
                    "relationship": "calls_module",
                    "module_name": name
                })
    except Exception as e:
        logging.error(f"HCL regex error for {filepath}: {e}")
    return deps

# ==========================================
# 2. Python Extractor
# ==========================================
def extract_python_treesitter(filepath, lang):
    from tree_sitter import Parser
    deps = []
    try:
        parser = Parser()
        parser.language = lang
        with open(filepath, 'rb') as f:
            code = f.read()
        tree = parser.parse(code)
        
        def traverse(node):
            if node.type == "import_statement":
                for c in node.children:
                    if c.type == "dotted_name":
                        name = c.text.decode('utf8')
                        deps.append({
                            "source": filepath,
                            "target": name,
                            "relationship": "imports_python_module"
                        })
                    elif c.type == "aliased_import":
                        dotted = c.child_by_field_name("name") or (c.children[0] if c.children else None)
                        if dotted:
                            deps.append({
                                "source": filepath,
                                "target": dotted.text.decode('utf8'),
                                "relationship": "imports_python_module"
                            })
            elif node.type == "import_from_statement":
                module_name = ""
                for c in node.children:
                    if c.type in ("dotted_name", "relative_import"):
                        module_name = c.text.decode('utf8')
                        break
                if module_name:
                    deps.append({
                        "source": filepath,
                        "target": module_name,
                        "relationship": "imports_python_module"
                    })
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
    except Exception as e:
        logging.error(f"Python tree-sitter parse error for {filepath}: {e}")
        return extract_python_regex(filepath)
    return deps

def extract_python_regex(filepath):
    deps = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                import_match = re.match(r'^import\s+([a-zA-Z0-9_\.,\s]+)', line)
                if import_match:
                    for name in import_match.group(1).split(','):
                        name = name.strip().split()[0]
                        deps.append({
                            "source": filepath,
                            "target": name,
                            "relationship": "imports_python_module"
                        })
                from_match = re.match(r'^from\s+([a-zA-Z0-9_\.]+)\s+import', line)
                if from_match:
                    deps.append({
                        "source": filepath,
                        "target": from_match.group(1),
                        "relationship": "imports_python_module"
                    })
    except Exception as e:
        logging.error(f"Python regex error for {filepath}: {e}")
    return deps

# ==========================================
# 3. YAML Extractor
# ==========================================
def extract_yaml_treesitter(filepath, lang):
    from tree_sitter import Parser
    deps = []
    try:
        parser = Parser()
        parser.language = lang
        with open(filepath, 'rb') as f:
            code = f.read()
        tree = parser.parse(code)
        
        def traverse(node):
            if node.type == "block_mapping_pair":
                key_node = None
                val_node = None
                for c in node.children:
                    if c.type == "flow_node" or c.type == "scalar":
                        if not key_node:
                            key_node = c
                        else:
                            val_node = c
                if key_node and val_node:
                    key_text = key_node.text.decode('utf8').strip()
                    if key_text in ("image", "uses", "source", "ref"):
                        val_text = val_node.text.decode('utf8').strip('"\' ')
                        deps.append({
                            "source": filepath,
                            "target": val_text,
                            "relationship": f"references_yaml_{key_text}"
                        })
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
    except Exception as e:
        logging.error(f"YAML tree-sitter parse error for {filepath}: {e}")
        return extract_yaml_regex(filepath)
    return deps

def extract_yaml_regex(filepath):
    deps = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                match = re.search(r'\b(image|uses|source|ref)\s*:\s*["\']?([^"\'\s]+)["\']?', line)
                if match:
                    deps.append({
                        "source": filepath,
                        "target": match.group(2),
                        "relationship": f"references_yaml_{match.group(1)}"
                    })
    except Exception as e:
        logging.error(f"YAML regex error for {filepath}: {e}")
    return deps

# ==========================================
# 4. Go Extractor
# ==========================================
def extract_go_treesitter(filepath, lang):
    from tree_sitter import Parser
    deps = []
    try:
        parser = Parser()
        parser.language = lang
        with open(filepath, 'rb') as f:
            code = f.read()
        tree = parser.parse(code)
        
        def traverse(node):
            if node.type == "import_spec":
                path_node = node.child_by_field_name("path") or (node.children[0] if node.children else None)
                if path_node:
                    path_text = path_node.text.decode('utf8').strip('"\' ')
                    deps.append({
                        "source": filepath,
                        "target": path_text,
                        "relationship": "imports_go_package"
                    })
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
    except Exception as e:
        logging.error(f"Go tree-sitter parse error for {filepath}: {e}")
        return extract_go_regex(filepath)
    return deps

def extract_go_regex(filepath):
    deps = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        single_matches = re.findall(r'import\s+["\']([^"\']+)["\']', content)
        for m in single_matches:
            deps.append({
                "source": filepath,
                "target": m,
                "relationship": "imports_go_package"
            })
        block_matches = re.findall(r'import\s*\(\s*([^)]+)\s*\)', content, re.DOTALL)
        for block in block_matches:
            for line in block.split('\n'):
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                match = re.search(r'["\']([^"\']+)["\']', line)
                if match:
                    deps.append({
                        "source": filepath,
                        "target": match.group(1),
                        "relationship": "imports_go_package"
                    })
    except Exception as e:
        logging.error(f"Go regex error for {filepath}: {e}")
    return deps

# ==========================================
# 5. JavaScript / TypeScript Extractor
# ==========================================
def extract_js_treesitter(filepath, lang):
    from tree_sitter import Parser
    deps = []
    try:
        parser = Parser()
        parser.language = lang
        with open(filepath, 'rb') as f:
            code = f.read()
        tree = parser.parse(code)
        
        def traverse(node):
            if node.type == "import_statement":
                source_node = node.child_by_field_name("source")
                if source_node:
                    source_text = source_node.text.decode('utf8').strip('"\' ')
                    deps.append({
                        "source": filepath,
                        "target": source_text,
                        "relationship": "imports_javascript_module"
                    })
            elif node.type == "call_expression":
                func_node = node.child_by_field_name("function")
                if func_node and func_node.text.decode('utf8') == "require":
                    args_node = node.child_by_field_name("arguments")
                    if args_node and len(args_node.children) > 1:
                        val_node = args_node.children[1]
                        val_text = val_node.text.decode('utf8').strip('"\' ')
                        deps.append({
                            "source": filepath,
                            "target": val_text,
                            "relationship": "requires_javascript_module"
                        })
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
    except Exception as e:
        logging.error(f"JS tree-sitter parse error for {filepath}: {e}")
        return extract_js_regex(filepath)
    return deps

def extract_js_regex(filepath):
    deps = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith('//') or line.startswith('/*') or not line:
                    continue
                import_match = re.search(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', line)
                if import_match:
                    deps.append({
                        "source": filepath,
                        "target": import_match.group(1),
                        "relationship": "imports_javascript_module"
                    })
                require_match = re.search(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', line)
                if require_match:
                    deps.append({
                        "source": filepath,
                        "target": require_match.group(1),
                        "relationship": "requires_javascript_module"
                    })
    except Exception as e:
        logging.error(f"JS regex error for {filepath}: {e}")
    return deps

# ==========================================
# Main Router
# ==========================================
def extract_dependencies(filepath):
    """Main routing function for unified multi-language dependency extraction"""
    ext = os.path.splitext(filepath)[1].lower()
    
    # 1. HCL / Terraform
    if ext == ".tf":
        lang = get_grammar("hcl") if TREE_SITTER_AVAILABLE else None
        if lang:
            return extract_hcl_treesitter(filepath, lang)
        else:
            return extract_hcl_regex(filepath)
            
    # 2. Python
    elif ext == ".py":
        lang = get_grammar("python") if TREE_SITTER_AVAILABLE else None
        if lang:
            return extract_python_treesitter(filepath, lang)
        else:
            return extract_python_regex(filepath)
            
    # 3. YAML
    elif ext in (".yaml", ".yml"):
        lang = get_grammar("yaml") if TREE_SITTER_AVAILABLE else None
        if lang:
            return extract_yaml_treesitter(filepath, lang)
        else:
            return extract_yaml_regex(filepath)
            
    # 4. Go
    elif ext == ".go":
        lang = get_grammar("go") if TREE_SITTER_AVAILABLE else None
        if lang:
            return extract_go_treesitter(filepath, lang)
        else:
            return extract_go_regex(filepath)
            
    # 5. JS/TS
    elif ext in (".js", ".ts"):
        lang = get_grammar("javascript") if TREE_SITTER_AVAILABLE else None
        if lang:
            return extract_js_treesitter(filepath, lang)
        else:
            return extract_js_regex(filepath)
            
    return []

def build_graph(source_dir):
    """Builds a deterministic census of the directory, cataloging monorepos and dependency flows"""
    categories = {
        "infrastructure": [],
        "orchestration": [],
        "pipelines": [],
        "app_logic": [],
        "monorepo_packages": []
    }
    baseline_census = []
    dependencies = []
    
    # Simple monorepo detection
    for root, dirs, files in os.walk(source_dir):
        if "package.json" in files or "go.mod" in files or "Cargo.toml" in files or "pom.xml" in files:
            if root != source_dir:
                categories["monorepo_packages"].append(os.path.relpath(root, source_dir))

        for f in files:
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, source_dir)
            
            # Skip hidden folders, node modules, and output target directories
            if "/." in path or "node_modules" in path or "DocumentationFactory/output" in path:
                continue
                
            baseline_census.append(rel_path)
                
            if f.endswith(".tf"):
                categories["infrastructure"].append(rel_path)
                file_deps = extract_dependencies(path)
                for dep in file_deps:
                    rel_src = os.path.relpath(dep["source"], source_dir)
                    dependencies.append({
                        "source": rel_src,
                        "target": dep["target"],
                        "relationship": dep["relationship"],
                        "module_name": dep.get("module_name", "")
                    })
            elif f.endswith(".yaml") or f.endswith(".yml"):
                if "deployment" in f.lower() or "service" in f.lower() or "k8s" in path:
                    categories["orchestration"].append(rel_path)
                elif "action" in f.lower() or "pipeline" in f.lower() or "gitlab-ci" in f.lower():
                    categories["pipelines"].append(rel_path)
                else:
                    categories["pipelines"].append(rel_path)
                
                file_deps = extract_dependencies(path)
                for dep in file_deps:
                    rel_src = os.path.relpath(dep["source"], source_dir)
                    dependencies.append({
                        "source": rel_src,
                        "target": dep["target"],
                        "relationship": dep["relationship"]
                    })
            elif "jenkinsfile" in f.lower() or "makefile" in f.lower():
                categories["pipelines"].append(rel_path)
            elif f.endswith(".py") or f.endswith(".js") or f.endswith(".ts") or f.endswith(".go") or f.endswith(".java") or f.endswith(".rs"):
                categories["app_logic"].append(rel_path)
                
                if f.endswith((".py", ".go", ".js", ".ts")):
                    file_deps = extract_dependencies(path)
                    for dep in file_deps:
                        rel_src = os.path.relpath(dep["source"], source_dir)
                        dependencies.append({
                            "source": rel_src,
                            "target": dep["target"],
                            "relationship": dep["relationship"]
                        })
                
    return {"categories": categories, "dependencies": dependencies, "baseline_census_files": baseline_census}

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
