#!/usr/bin/env python3
"""
AST-Style Resource Delta Analyzer
---------------------------------
Parses a git diff patch file natively and compiles a structured, concise Markdown
summary of resource additions, deletions, and property modifications (tags, compute sizes).
Zero pip dependencies.

Usage:
    python3 resource_delta_analyzer.py <diff_patch_path> [output_summary_path]
"""

import sys
import os
import re

def analyze_diff(diff_content):
    file_deltas = {}
    current_file = None
    in_block_comment_add = False
    in_block_comment_del = False
    k8s_added_kind = None
    k8s_deleted_kind = None
    k8s_added_name = None
    k8s_deleted_name = None
    in_metadata_add = False
    in_metadata_del = False
    metadata_indent_add = -1
    metadata_indent_del = -1

    # Regex definitions for IaC (Terraform) and Kubernetes elements
    tf_resource_re = re.compile(r'^\s*resource\s+"([^"]+)"\s+"([^"]+)"')
    tf_module_re = re.compile(r'^\s*module\s+"([^"]+)"')
    k8s_kind_re = re.compile(r'^\s*kind:\s*(\w+)')
    k8s_name_re = re.compile(r'^\s*name:\s*([\w\-]+)')
    k8s_metadata_re = re.compile(r'^\s*metadata:\s*$')

    lines = diff_content.split('\n')

    for line in lines:
        if line.startswith('diff --git'):
            current_file = None
            in_block_comment_add = False
            in_block_comment_del = False
            k8s_added_kind = None
            k8s_deleted_kind = None
            k8s_added_name = None
            k8s_deleted_name = None
            in_metadata_add = False
            in_metadata_del = False
            metadata_indent_add = -1
            metadata_indent_del = -1
        elif line.startswith('--- a/') or line.startswith('+++ b/'):
            # Extract file name, skipping /dev/null
            filename = line[6:]
            if filename != "/dev/null":
                current_file = filename
                if current_file not in file_deltas:
                    file_deltas[current_file] = {
                        "added": [],
                        "deleted": [],
                        "modified": []
                    }
        elif current_file and (line.startswith('+') or line.startswith('-')):
            # Ignore structural git diff metadata
            if line.startswith('+++') or line.startswith('---'):
                continue

            # Calculate indentation level in diff content (excluding the diff prefix + or -)
            indent = len(line[1:]) - len(line[1:].lstrip())
            content = line[1:].strip()
            is_added = line.startswith('+')

            # Skip comments and track multi-line block comments
            if is_added:
                if "/*" in content:
                    in_block_comment_add = True
                if in_block_comment_add:
                    if "*/" in content:
                        in_block_comment_add = False
                    continue
                if "*/" in content:
                    continue
                if content.startswith('#') or content.startswith('//'):
                    continue
            else:
                if "/*" in content:
                    in_block_comment_del = True
                if in_block_comment_del:
                    if "*/" in content:
                        in_block_comment_del = False
                    continue
                if "*/" in content:
                    continue
                if content.startswith('#') or content.startswith('//'):
                    continue

            # 1. Parse Terraform resource additions/deletions
            m_res = tf_resource_re.match(content)
            if m_res:
                res_type, res_name = m_res.groups()
                item = f"resource `{res_type}.{res_name}`"
                if is_added:
                    file_deltas[current_file]["added"].append(item)
                else:
                    file_deltas[current_file]["deleted"].append(item)
                continue

            # 2. Parse Terraform module additions/deletions
            m_mod = tf_module_re.match(content)
            if m_mod:
                mod_name = m_mod.group(1)
                item = f"module `{mod_name}`"
                if is_added:
                    file_deltas[current_file]["added"].append(item)
                else:
                    file_deltas[current_file]["deleted"].append(item)
                continue

            # 2.5. Parse Kubernetes additions/deletions
            if is_added:
                # Track exiting metadata block
                if in_metadata_add and indent <= metadata_indent_add:
                    if content: # non-empty line exits metadata if at or above its indentation
                        in_metadata_add = False
                        metadata_indent_add = -1

                if k8s_metadata_re.match(content):
                    in_metadata_add = True
                    metadata_indent_add = indent
                    continue

                m_kind = k8s_kind_re.match(content)
                if m_kind:
                    k8s_added_kind = m_kind.group(1)
                    if k8s_added_name:
                        item = f"Kubernetes resource `{k8s_added_kind}.{k8s_added_name}`"
                        file_deltas[current_file]["added"].append(item)
                        k8s_added_kind = None
                        k8s_added_name = None
                    continue

                m_name = k8s_name_re.match(content)
                if m_name and in_metadata_add:
                    k8s_added_name = m_name.group(1)
                    if k8s_added_kind:
                        item = f"Kubernetes resource `{k8s_added_kind}.{k8s_added_name}`"
                        file_deltas[current_file]["added"].append(item)
                        k8s_added_kind = None
                        k8s_added_name = None
                    continue
            else:
                # Track exiting metadata block
                if in_metadata_del and indent <= metadata_indent_del:
                    if content:
                        in_metadata_del = False
                        metadata_indent_del = -1

                if k8s_metadata_re.match(content):
                    in_metadata_del = True
                    metadata_indent_del = indent
                    continue

                m_kind = k8s_kind_re.match(content)
                if m_kind:
                    k8s_deleted_kind = m_kind.group(1)
                    if k8s_deleted_name:
                        item = f"Kubernetes resource `{k8s_deleted_kind}.{k8s_deleted_name}`"
                        file_deltas[current_file]["deleted"].append(item)
                        k8s_deleted_kind = None
                        k8s_deleted_name = None
                    continue

                m_name = k8s_name_re.match(content)
                if m_name and in_metadata_del:
                    k8s_deleted_name = m_name.group(1)
                    if k8s_deleted_kind:
                        item = f"Kubernetes resource `{k8s_deleted_kind}.{k8s_deleted_name}`"
                        file_deltas[current_file]["deleted"].append(item)
                        k8s_deleted_kind = None
                        k8s_deleted_name = None
                    continue


            # 3. Parse general property modifications (FinOps SKUs, tags, compliance keys)
            if any(prop in content for prop in ["vm_size", "size", "sku", "tags", "CostCenter", "Orchestrator", "version"]):
                clean_prop = content.split('=')[0].strip() if '=' in content else content.split(':')[0].strip()
                if len(clean_prop) < 40 and not clean_prop.startswith('"'):
                    action = "Set" if is_added else "Removed"
                    file_deltas[current_file]["modified"].append(f"property `{clean_prop}` ({action})")

    # 4. Generate structured Markdown output
    markdown_lines = ["### AST Resource Delta Summary", ""]
    
    active_changes = False
    for filepath, delta in sorted(file_deltas.items()):
        added = sorted(list(set(delta["added"])))
        deleted = sorted(list(set(delta["deleted"])))
        modified = sorted(list(set(delta["modified"])))

        if not added and not deleted and not modified:
            continue

        active_changes = True
        markdown_lines.append(f"- **File:** `{filepath}`")
        for item in added:
            markdown_lines.append(f"  - [x] **Added** {item}")
        for item in deleted:
            markdown_lines.append(f"  - [ ] **Removed** {item}")
        for item in modified:
            markdown_lines.append(f"  - [~] **Modified** {item}")

    if not active_changes:
        markdown_lines.append("No cloud resource or compliance configuration changes detected in the patch.")

    return "\n".join(markdown_lines)

def main():
    if len(sys.argv) < 2:
        print("[-] Usage: python3 resource_delta_analyzer.py <diff_patch_path> [output_summary_path]")
        sys.exit(1)

    diff_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(diff_path):
        print(f"[!] Diff file not found: {diff_path}")
        sys.exit(1)

    with open(diff_path, 'r', errors='ignore') as f:
        content = f.read()

    summary = analyze_diff(content)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(summary)
        print(f"[✅] AST delta analysis compiled to: {output_path}")
    else:
        print(summary)

if __name__ == "__main__":
    main()
