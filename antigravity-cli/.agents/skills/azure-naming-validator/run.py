#!/usr/bin/env python3
"""
Azure Resource Naming & Constraints Validator (offline, deterministic)
----------------------------------------------------------------------
Azure enforces strict, resource-specific naming rules (length, allowed
characters, global uniqueness). Violations are a very common migration failure
class that `terraform validate` does NOT catch — they only surface at apply time
against the live API. This skill validates the `name` of generated `azurerm_*`
resources against those rules entirely offline (no cloud credentials needed),
so the developer/validator can fix them before deployment.

Usage:
    # Scan a directory of generated Terraform (default: output/target)
    python3 run.py --dir output/target --output output/artifacts/azure-naming-results.json

    # Validate a single literal name for a given resource type (quick check)
    python3 run.py --check azurerm_storage_account --name "myprodstorage01"

Exit code: 0 if no error-severity violations, 1 otherwise (so it can gate a pipeline).

Names built from interpolation (e.g. "st${var.env}prod") cannot be fully
resolved offline; the validator checks the STATIC portion (length budget +
charset) and reports those as warnings rather than hard errors.
"""

import argparse
import glob
import json
import os
import re
import sys

# Per-resource constraints. `regex` validates the *full literal* name; `charset`
# is a human description. `global` = must be globally unique across Azure.
CONSTRAINTS = {
    "azurerm_storage_account":        {"min": 3,  "max": 24, "regex": r"^[a-z0-9]+$",                 "global": True,  "charset": "lowercase letters and numbers only"},
    "azurerm_key_vault":              {"min": 3,  "max": 24, "regex": r"^[A-Za-z][A-Za-z0-9-]*[A-Za-z0-9]$", "global": True,  "charset": "alphanumerics and hyphens, start with a letter, end with letter/digit, no consecutive hyphens"},
    "azurerm_container_registry":     {"min": 5,  "max": 50, "regex": r"^[a-zA-Z0-9]+$",              "global": True,  "charset": "alphanumerics only"},
    "azurerm_cosmosdb_account":       {"min": 3,  "max": 44, "regex": r"^[a-z0-9][a-z0-9-]*[a-z0-9]$","global": True,  "charset": "lowercase letters, numbers and hyphens"},
    "azurerm_postgresql_flexible_server": {"min": 3, "max": 63, "regex": r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", "global": True, "charset": "lowercase letters, numbers and hyphens"},
    "azurerm_mysql_flexible_server":  {"min": 3,  "max": 63, "regex": r"^[a-z0-9][a-z0-9-]*[a-z0-9]$","global": True,  "charset": "lowercase letters, numbers and hyphens"},
    "azurerm_redis_cache":            {"min": 1,  "max": 63, "regex": r"^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$", "global": True, "charset": "alphanumerics and hyphens, no consecutive hyphens"},
    "azurerm_servicebus_namespace":   {"min": 6,  "max": 50, "regex": r"^[A-Za-z][A-Za-z0-9-]*[A-Za-z0-9]$", "global": True, "charset": "alphanumerics and hyphens, start with a letter"},
    "azurerm_eventhub_namespace":     {"min": 6,  "max": 50, "regex": r"^[A-Za-z][A-Za-z0-9-]*[A-Za-z0-9]$", "global": True, "charset": "alphanumerics and hyphens, start with a letter"},
    "azurerm_linux_function_app":     {"min": 2,  "max": 60, "regex": r"^[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]$", "global": True, "charset": "alphanumerics and hyphens (part of *.azurewebsites.net)"},
    "azurerm_windows_function_app":   {"min": 2,  "max": 60, "regex": r"^[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]$", "global": True, "charset": "alphanumerics and hyphens (part of *.azurewebsites.net)"},
    "azurerm_linux_web_app":          {"min": 2,  "max": 60, "regex": r"^[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]$", "global": True, "charset": "alphanumerics and hyphens (part of *.azurewebsites.net)"},
    "azurerm_windows_web_app":        {"min": 2,  "max": 60, "regex": r"^[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]$", "global": True, "charset": "alphanumerics and hyphens (part of *.azurewebsites.net)"},
    "azurerm_resource_group":         {"min": 1,  "max": 90, "regex": r"^[A-Za-z0-9_.()\-]*[A-Za-z0-9_()\-]$", "global": False, "charset": "alphanumerics, underscore, parentheses, hyphen, period (cannot end with period)"},
    "azurerm_virtual_network":        {"min": 2,  "max": 64, "regex": r"^[A-Za-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9_]$", "global": False, "charset": "alphanumerics, underscore, period, hyphen"},
    "azurerm_subnet":                 {"min": 1,  "max": 80, "regex": r"^[A-Za-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9_]$", "global": False, "charset": "alphanumerics, underscore, period, hyphen"},
    "azurerm_network_security_group": {"min": 1,  "max": 80, "regex": r"^[A-Za-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9_]$", "global": False, "charset": "alphanumerics, underscore, period, hyphen"},
    "azurerm_public_ip":              {"min": 1,  "max": 80, "regex": r"^[A-Za-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9_]$", "global": False, "charset": "alphanumerics, underscore, period, hyphen"},
    "azurerm_nat_gateway":            {"min": 1,  "max": 80, "regex": r"^[A-Za-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9_]$", "global": False, "charset": "alphanumerics, underscore, period, hyphen"},
    "azurerm_lb":                     {"min": 1,  "max": 80, "regex": r"^[A-Za-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9_]$", "global": False, "charset": "alphanumerics, underscore, period, hyphen"},
    "azurerm_kubernetes_cluster":     {"min": 1,  "max": 63, "regex": r"^[A-Za-z0-9][A-Za-z0-9_\-]*[A-Za-z0-9]$", "global": False, "charset": "alphanumerics, underscore, hyphen"},
    "azurerm_user_assigned_identity": {"min": 3,  "max": 128,"regex": r"^[A-Za-z0-9][A-Za-z0-9_\-]*$",  "global": False, "charset": "alphanumerics, underscore, hyphen"},
    "azurerm_linux_virtual_machine":  {"min": 1,  "max": 64, "regex": r"^[A-Za-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9_]$", "global": False, "charset": "alphanumerics, underscore, period, hyphen (computer_name <= 64)"},
    "azurerm_windows_virtual_machine":{"min": 1,  "max": 15, "regex": r"^[A-Za-z0-9\-]+$",             "global": False, "charset": "<= 15 chars (Windows computer name limit), alphanumerics and hyphen"},
}


def find_tf_files(directory):
    return sorted(glob.glob(os.path.join(directory, "**", "*.tf"), recursive=True))


def extract_resources(text):
    """Yield (rtype, label, raw_name_rhs_or_None) for each azurerm_* resource block.
    Only the resource's own top-level `name =` (brace depth 1) is captured."""
    pat = re.compile(r'resource\s+"(azurerm_[a-z0-9_]+)"\s+"([^"]+)"\s*\{')
    out = []
    for m in pat.finditer(text):
        rtype, label = m.group(1), m.group(2)
        depth, k, n = 1, m.end(), len(text)
        top_chars = []
        in_str = False   # string-aware so braces inside "" / "${...}" don't affect depth
        esc = False
        while k < n and depth > 0:
            c = text[k]
            if in_str:
                if depth == 1:
                    top_chars.append(c)
                if esc:
                    esc = False
                elif c == '\\':
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
                if depth == 1:
                    top_chars.append(c)
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            elif depth == 1:
                top_chars.append(c)
            k += 1
        block = "".join(top_chars)
        nm = re.search(r'(?:^|\n)\s*name\s*=\s*(.+)', block)
        out.append((rtype, label, nm.group(1).strip() if nm else None))
    return out


def static_prefix(rhs):
    """Return the leading literal text of an interpolated string value, e.g.
    "st${var.env}" -> 'st'.  Returns '' if not a quoted string."""
    m = re.match(r'"([^"$]*)', rhs)
    return m.group(1) if m else ""


def validate_name(rtype, rhs):
    """Return list of violation dicts for one resource's name RHS."""
    c = CONSTRAINTS.get(rtype)
    if not c or rhs is None:
        return []
    violations = []
    literal = rhs.startswith('"') and '${' not in rhs
    if literal:
        name = rhs.strip('"')
        if len(name) < c["min"] or len(name) > c["max"]:
            violations.append(("error",
                f"name '{name}' is {len(name)} chars; must be {c['min']}-{c['max']}"))
        if not re.match(c["regex"], name):
            violations.append(("error",
                f"name '{name}' violates charset: {c['charset']}"))
    else:
        prefix = static_prefix(rhs)
        if len(prefix) > c["max"]:
            violations.append(("error",
                f"static prefix '{prefix}' already exceeds max {c['max']} chars"))
        if prefix and not re.match(r'^[A-Za-z0-9_.()\-]*$', prefix):
            violations.append(("warning",
                f"static prefix '{prefix}' may contain characters disallowed for {rtype} ({c['charset']})"))
        # always remind that the interpolated portion needs runtime verification
        violations.append(("warning",
            f"name is interpolated ({rhs}); verify the resolved value fits {c['min']}-{c['max']} chars, {c['charset']}"
            + (" (GLOBALLY UNIQUE)" if c.get("global") else "")))
    return violations


def main():
    ap = argparse.ArgumentParser(description="Validate Azure resource names offline.")
    ap.add_argument("--dir", default="output/target", help="directory of generated Terraform to scan")
    ap.add_argument("--output", help="write JSON results to this path (also prints summary)")
    ap.add_argument("--check", help="validate a single resource type (with --name)")
    ap.add_argument("--name", help="literal name to validate against --check type")
    args = ap.parse_args()

    # Single quick check mode
    if args.check:
        rhs = f'"{args.name}"' if args.name is not None else None
        vs = validate_name(args.check, rhs)
        if args.check not in CONSTRAINTS:
            print(f"No constraints recorded for {args.check} (treated as OK).")
            return 0
        if not vs:
            print(f"OK: '{args.name}' is valid for {args.check}.")
            return 0
        for sev, msg in vs:
            print(f"[{sev.upper()}] {args.check}: {msg}")
        return 1 if any(s == "error" for s, _ in vs) else 0

    files = find_tf_files(args.dir)
    result = {
        "skill": "azure-naming-validator",
        "scanned_dir": args.dir,
        "files_scanned": len(files),
        "resources_checked": 0,
        "violations": [],
        "summary": {"errors": 0, "warnings": 0, "status": "pass"},
    }
    for fp in files:
        try:
            with open(fp, "r") as f:
                text = f.read()
        except Exception:
            continue
        for rtype, label, rhs in extract_resources(text):
            if rtype not in CONSTRAINTS:
                continue
            result["resources_checked"] += 1
            for sev, msg in validate_name(rtype, rhs):
                result["violations"].append({
                    "file": fp, "resource_type": rtype, "label": label,
                    "severity": sev, "message": msg,
                })
                result["summary"]["errors" if sev == "error" else "warnings"] += 1

    result["summary"]["status"] = "fail" if result["summary"]["errors"] > 0 else "pass"

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

    print(f"[azure-naming-validator] {result['resources_checked']} resources checked across "
          f"{result['files_scanned']} files: {result['summary']['errors']} errors, "
          f"{result['summary']['warnings']} warnings -> {result['summary']['status'].upper()}")
    return 1 if result["summary"]["errors"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
