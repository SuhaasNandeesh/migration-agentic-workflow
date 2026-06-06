#!/usr/bin/env python3
"""
Sync Script for CLI Agentic Workflow
------------------------------------
This script reads the master configuration, agents, and skills from the
`opencode` directory and translates them into the native formats required
by `gemini-cli`, `claude-cli`, `pi-cli`, and `antigravity-cli`.

Usage:
    python3 sync-cli-agents.py

Run this script anytime you add, modify, or delete an agent or skill
in the `opencode` folder to ensure all CLI environments remain up-to-date.
"""

import os
import glob
import re
import json
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Source directories
OPENCODE_ROOT = os.path.join(BASE_DIR, "opencode")
OPENCODE_DIR = os.path.join(OPENCODE_ROOT, ".opencode")

# Target directories - Gemini
GEMINI_ROOT = os.path.join(BASE_DIR, "gemini-cli")
GEMINI_AGENTS_DIR = os.path.join(GEMINI_ROOT, ".gemini", "agents")
GEMINI_SKILLS_DIR = os.path.join(GEMINI_ROOT, ".gemini", "skills")

# Target directories - Claude
CLAUDE_ROOT = os.path.join(BASE_DIR, "claude-cli")
CLAUDE_AGENTS_DIR = os.path.join(CLAUDE_ROOT, ".claude", "agents")
CLAUDE_CMDS_DIR = os.path.join(CLAUDE_ROOT, ".claude", "commands")
CLAUDE_SKILLS_DIR = os.path.join(CLAUDE_ROOT, ".claude", "skills")

# Target directories - Pi
PI_ROOT = os.path.join(BASE_DIR, "pi-cli")
PI_AGENTS_DIR = os.path.join(PI_ROOT, ".pi", "prompts")
PI_SKILLS_DIR = os.path.join(PI_ROOT, ".pi", "skills")

# Target directories - Antigravity (New standard)
ANTIGRAVITY_ROOT = os.path.join(BASE_DIR, "antigravity-cli")
ANTIGRAVITY_AGENTS_DIR = os.path.join(ANTIGRAVITY_ROOT, ".agents", "agents")
ANTIGRAVITY_SKILLS_DIR = os.path.join(ANTIGRAVITY_ROOT, ".agents", "skills")
ANTIGRAVITY_WIKI_DIR = os.path.join(ANTIGRAVITY_ROOT, ".agents", "wiki")

# --- Per-agent tool capability mapping ---------------------------------------
CAP_ORDER = ['read', 'write', 'edit', 'bash', 'glob', 'grep', 'fetch']

CAP_TO_TOOLS = {
    'gemini': {
        'read': ['read_file'],
        'write': ['write_file'],
        'edit': ['replace'],
        'bash': ['run_shell_command'],
        'glob': ['glob'],
        'grep': ['search_file_content'],
        'fetch': ['web_fetch', 'google_web_search'],
    },
    'claude': {
        'read': ['Read'],
        'write': ['Write'],
        'edit': ['Edit'],
        'bash': ['Bash'],
        'glob': ['Glob'],
        'grep': ['Grep'],
        'fetch': ['WebFetch', 'WebSearch'],
    },
    'antigravity': {
        'read': ['read_file', 'view_file'],
        'write': ['write_file', 'write_to_file'],
        'edit': ['replace_file_content', 'multi_replace_file_content'],
        'bash': ['run_command'],
        'glob': ['list_dir'],
        'grep': ['grep_search'],
        'fetch': ['web_fetch'],
    },
    'pi': {
        'read': ['read'],
        'write': ['write'],
        'edit': ['edit'],
        'bash': ['bash'],
        'glob': ['ls', 'find'],
        'grep': ['grep'],
        'fetch': [],
    },
}

DEFAULT_PLATFORM_MODELS = {
    'claude': 'sonnet',
    'gemini': 'gemini-2.5-pro',
    'antigravity': 'gemini-2.5-pro',
}

# --- Helper Utilities --------------------------------------------------------

def setup_directories():
    print("Preparing directories and performing workspace sync...")
    
    # List of directories to clean up and recreate
    recreate_dirs = [
        GEMINI_AGENTS_DIR, GEMINI_SKILLS_DIR,
        CLAUDE_AGENTS_DIR, CLAUDE_CMDS_DIR, CLAUDE_SKILLS_DIR,
        PI_AGENTS_DIR, PI_SKILLS_DIR,
        ANTIGRAVITY_AGENTS_DIR, ANTIGRAVITY_SKILLS_DIR
    ]
    
    for d in recreate_dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
        
    # Set up Workspace items for all target CLI platforms and always overwrite to keep them in sync
    target_roots = [GEMINI_ROOT, CLAUDE_ROOT, PI_ROOT, ANTIGRAVITY_ROOT]
    workspace_items = ["DocumentationFactory", "knowledge", "migration-mapping", "validation", "migration-config.json", "run-multi-repo-coordinator.py", ".tflint.hcl"]
    
    for target_root in target_roots:
        os.makedirs(target_root, exist_ok=True)
        for item in workspace_items:
            src = os.path.join(OPENCODE_ROOT, item)
            dst = os.path.join(target_root, item)
            if os.path.exists(src):
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("temp_test_run", "output", "__pycache__"))
                else:
                    shutil.copy(src, dst)
        print(f"Synced Workspace Items to {os.path.relpath(target_root, BASE_DIR)}")

    # Sync Wiki recursively to all CLI platforms
    wiki_src = os.path.join(OPENCODE_DIR, "wiki")
    if os.path.exists(wiki_src):
        for target_wiki in [
            os.path.join(GEMINI_ROOT, ".gemini", "wiki"),
            os.path.join(CLAUDE_ROOT, ".claude", "wiki"),
            os.path.join(PI_ROOT, ".pi", "wiki"),
            ANTIGRAVITY_WIKI_DIR
        ]:
            if os.path.exists(target_wiki):
                shutil.rmtree(target_wiki)
            shutil.copytree(wiki_src, target_wiki)
            print(f"Synced Wiki to {os.path.relpath(target_wiki, BASE_DIR)}")

def yaml_dq(s):
    """Return a YAML-safe double-quoted scalar (escapes backslashes and quotes)"""
    s = str(s).replace('\\', '\\\\').replace('"', '\\"')
    return f'"{s}"'

def resolve_platform_models(config):
    pm = config.get('platform_models') if isinstance(config.get('platform_models'), dict) else {}
    out = dict(DEFAULT_PLATFORM_MODELS)
    for k in out:
        if pm.get(k):
            out[k] = pm[k]
    return out

def resolve_claude_model():
    p = os.path.join(OPENCODE_ROOT, 'opencode.json')
    if os.path.exists(p):
        try:
            with open(p) as f:
                return resolve_platform_models(json.load(f))['claude']
        except Exception:
            pass
    return DEFAULT_PLATFORM_MODELS['claude']

def parse_md(filepath):
    with open(filepath, 'r') as f:
        # Normalize CRLF/CR so frontmatter detection is line-ending agnostic.
        content = f.read().replace('\r\n', '\n').replace('\r', '\n')

    match = re.match(r'^---\n(.*?)\n---\n?(.*)', content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter_str = match.group(1)
    body = match.group(2)

    frontmatter = {}
    current_key = None
    current_is_block = False  # True only after a key that opens a nested block
    for line in frontmatter_str.split('\n'):
        if not line.strip():
            continue
        if line.startswith('  ') and current_key and current_is_block:
            # nested map/list entry (e.g. under `tools:`)
            if not isinstance(frontmatter[current_key], list):
                frontmatter[current_key] = []
            frontmatter[current_key].append(line.strip().split(':')[0].strip('- '))
        elif not line.startswith(' ') and ':' in line:
            k, v = line.split(':', 1)
            k = k.strip()
            v = v.strip().strip('"\'')
            frontmatter[k] = v
            current_key = k
            current_is_block = (v == '')
    return frontmatter, body

def parse_tool_caps(filepath):
    """Extract the set of enabled tool capabilities from an agent's frontmatter"""
    with open(filepath, 'r') as f:
        content = f.read()
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {'read', 'write', 'bash', 'glob', 'grep'}
    caps = set()
    in_tools = False
    for line in m.group(1).split('\n'):
        if re.match(r'^tools:\s*$', line):
            in_tools = True
            continue
        if in_tools:
            tm = re.match(r'^\s+([A-Za-z_]+):\s*(true|false)\s*$', line)
            if tm:
                if tm.group(2).lower() == 'true':
                    caps.add(tm.group(1).lower())
                continue
            if re.match(r'^\S', line):  # reached the next top-level key
                in_tools = False
    return caps or {'read', 'write', 'bash', 'glob', 'grep'}

def map_tools(platform, caps):
    """Translate a set of source capabilities into ordered, de-duplicated native tool names"""
    tools, seen = [], set()
    for cap in CAP_ORDER:
        if cap in caps:
            for t in CAP_TO_TOOLS[platform].get(cap, []):
                if t not in seen:
                    seen.add(t)
                    tools.append(t)
    return tools

def clean_markdown(text):
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# --- Agent Processing Helpers ------------------------------------------------

def load_system_common_rules():
    """Load and parse categorized rules from system_common.md"""
    system_common_path = os.path.join(OPENCODE_DIR, "agents", "system_common.md")
    core_rules, devops_rules, ast_rules = [], [], []
    cat_buckets = {"core": core_rules, "devops": devops_rules, "ast": ast_rules}
    current_category = None
    
    if os.path.exists(system_common_path):
        with open(system_common_path, 'r') as f:
            for line in f:
                m_cat = re.match(r'^##\s*\[(CORE|DEVOPS|AST)\]\s*', line)
                if m_cat:
                    current_category = m_cat.group(1).lower()
                    cat_buckets[current_category].append(
                        re.sub(r'^(##\s*)\[(?:CORE|DEVOPS|AST)\]\s*', r'\1', line))
                elif line.startswith("## "):
                    current_category = None
                elif current_category:
                    cat_buckets[current_category].append(line)
                    
    return "".join(core_rules).strip(), "".join(devops_rules).strip(), "".join(ast_rules).strip()

def stitch_agent_rules(name, body, core_block, devops_block, ast_block):
    """Inject CORE, DEVOPS, or AST rules based on the agent's responsibilities"""
    devops_agents = ["developer", "qa-tester", "validator", "security", "cost-estimator", "knowledge-compiler", "planner", "secrets-migrator", "drift-verifier"]
    ast_agents = ["developer", "code-reviewer", "surgical-fix", "spec-analyst", "flow-tracer"]

    stitched_rules = []
    if core_block:
        stitched_rules.append(core_block)
    if name in devops_agents and devops_block:
        stitched_rules.append(devops_block)
    if name in ast_agents and ast_block:
        stitched_rules.append(ast_block)
        
    return body + "".join(stitched_rules)

def rewrite_wiki_and_skill_paths(text, platform_skills, platform_wiki):
    """Rewrite opencode paths into target-specific path patterns"""
    return text.replace("../.opencode/skills/", platform_skills) \
               .replace(".opencode/skills/", platform_skills) \
               .replace("../.opencode/wiki/", platform_wiki) \
               .replace(".opencode/wiki/", platform_wiki)

def append_delegation_logic(name, body, platform):
    """Appends CLI-specific autonomous delegation rules for supervising orchestrators"""
    if name not in ("supervisor", "doc-supervisor"):
        return body
        
    delegation_blocks = {
        'gemini': (
            "\n\n## CLI-Specific Autonomous Delegation (Gemini CLI)\n"
            "To invoke a subagent autonomously, you MUST use the `@<agent-name>` syntax in your prompt (e.g., `@code-reviewer please review the generated files`).\n"
            "To utilize a skill, ensure you request it via standard prompt interaction or slash commands like `/skills <skill-name>` if available.\n"
        ),
        'claude': (
            "\n\n## CLI-Specific Autonomous Delegation (Claude Code CLI)\n"
            "To invoke a subagent autonomously, you MUST use the `Bash` tool to run the Claude CLI in non-interactive/headless mode with the `-p` flag and skip permissions (e.g., `claude -p --dangerously-skip-permissions --agent code-reviewer \"Please review the generated files\"`). This is essential to prevent terminal hangs and ensure the process runs fully autonomously.\n"
            "To utilize a skill/command, invoke the custom slash command `/<skill-name>` natively or run `claude -p --dangerously-skip-permissions /<skill-name>` via the Bash tool.\n"
        ),
        'pi': (
            "\n\n## CLI-Specific Autonomous Delegation (pi.dev)\n"
            "To invoke a subagent autonomously, you MUST use `/<agent-name>` to expand its Prompt Template (e.g., `/code-reviewer`).\n"
            "To utilize a skill, load it when your tasks match its description or invoke it directly if supported.\n"
        ),
        'antigravity': (
            "\n\n## CLI-Specific Autonomous Delegation (Antigravity CLI)\n"
            "To invoke a subagent autonomously, you MUST use the `invoke_subagent` tool or the `@<agent-name>` syntax in your prompt (e.g., `@code-reviewer please review the generated files`).\n"
            "To utilize a skill, ensure you refer to the skills configured under `.agents/skills/` (the platform automatically discovers them) or trigger them via slash commands like `/skills <skill-name>`.\n"
        )
    }
    
    return body + delegation_blocks.get(platform, "")

# --- Platform-Specific Exporters ---------------------------------------------

def build_gemini_frontmatter(name, fm, tools, temperature):
    desc = fm.get('description', '')
    res = f"---\nname: {name}\ndescription: {yaml_dq(desc)}\ntools:\n"
    for t in tools:
        res += f"  - {t}\n"
    if temperature is not None:
        res += f"temperature: {temperature}\n"
    res += "model: inherit\n---\n"
    return res

def build_claude_frontmatter(name, fm, tools, temperature, model):
    desc = fm.get('description', '')
    res = f"---\nname: {name}\ndescription: {yaml_dq(desc)}\ntools: {', '.join(tools)}\nmodel: {model}\n"
    if temperature is not None:
        res += f"temperature: {temperature}\n"
    res += "---\n"
    return res

def build_pi_frontmatter(name, fm, tools, temperature):
    desc = fm.get('description', '')
    res = f"---\nname: {name}\ndescription: {yaml_dq(desc)}\ntools:\n"
    for t in tools:
        res += f"  - {t}\n"
    if temperature is not None:
        res += f"temperature: {temperature}\n"
    res += "---\n"
    return res

def write_gemini_agent(name, fm, body, tools, temperature):
    gemini_fm = build_gemini_frontmatter(name, fm, tools, temperature)
    with open(os.path.join(GEMINI_AGENTS_DIR, f"{name}.md"), 'w') as f:
        f.write(gemini_fm + body)

def write_claude_agent(name, fm, body, tools, temperature, claude_model):
    claude_fm = build_claude_frontmatter(name, fm, tools, temperature, model=claude_model)
    target_dir = CLAUDE_AGENTS_DIR
    if fm.get('mode') != 'primary':
        target_dir = os.path.join(CLAUDE_AGENTS_DIR, "subagents")
        os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, f"{name}.md"), 'w') as f:
        f.write(claude_fm + body)

def write_pi_agent(name, fm, body, tools, temperature):
    pi_fm = build_pi_frontmatter(name, fm, tools, temperature)
    with open(os.path.join(PI_AGENTS_DIR, f"{name}.md"), 'w') as f:
        f.write(pi_fm + body)

def write_antigravity_agent(name, fm, body, tools, temperature):
    agent_dir = os.path.join(ANTIGRAVITY_AGENTS_DIR, name)
    os.makedirs(agent_dir, exist_ok=True)
    
    agent_config = {
        "name": name,
        "description": fm.get('description', ''),
        "model": "inherit",
        "tools": tools,
        "instructions": body
    }
    if temperature is not None:
        try:
            agent_config["temperature"] = float(temperature)
        except (TypeError, ValueError):
            pass
            
    with open(os.path.join(agent_dir, "agent.json"), 'w') as f:
        json.dump(agent_config, f, indent=2)
        
    with open(os.path.join(agent_dir, "instructions.md"), 'w') as f:
        f.write(body)

# --- Core Processes ----------------------------------------------------------

def process_agents():
    claude_model = resolve_claude_model()
    core_rules, devops_rules, ast_rules = load_system_common_rules()

    core_block = ("\n\n## Global Core Instructions\n" + core_rules) if core_rules else ""
    devops_block = ("\n\n## Global DevOps & IaC Standards\n" + devops_rules) if devops_rules else ""
    ast_block = ("\n\n## Just-in-Time Context Hydration Standards (AST)\n" + ast_rules) if ast_rules else ""

    agent_files = glob.glob(os.path.join(OPENCODE_DIR, "agents", "*.md"))

    total_raw_chars = 0
    total_precompile_chars = 0
    total_compiled_chars = 0
    processed_count = 0
    
    for filepath in agent_files:
        name = os.path.basename(filepath).replace('.md', '')
        if name == "system_common":
            continue
            
        fm, body = parse_md(filepath)
        processed_count += 1

        caps = parse_tool_caps(filepath)
        temperature = fm.get('temperature')
        gemini_tools = map_tools('gemini', caps)
        claude_tools = map_tools('claude', caps)
        antigravity_tools = map_tools('antigravity', caps)
        pi_tools = map_tools('pi', caps)

        total_raw_chars += len(body)
        
        # 1. Stitch common rules
        combined_body = stitch_agent_rules(name, body, core_block, devops_block, ast_block)
        total_precompile_chars += len(combined_body)

        # 2. Minify / Clean comments & whitespace
        combined_body = clean_markdown(combined_body)
        total_compiled_chars += len(combined_body)

        # 3. Rewrite paths and append delegation logic per platform
        gemini_body = rewrite_wiki_and_skill_paths(combined_body, ".gemini/skills/", ".gemini/wiki/")
        gemini_body = append_delegation_logic(name, gemini_body, 'gemini')

        claude_body = rewrite_wiki_and_skill_paths(combined_body, ".claude/skills/", ".claude/wiki/")
        claude_body = append_delegation_logic(name, claude_body, 'claude')

        pi_body = rewrite_wiki_and_skill_paths(combined_body, ".pi/skills/", ".pi/wiki/")
        pi_body = append_delegation_logic(name, pi_body, 'pi')

        antigravity_body = rewrite_wiki_and_skill_paths(combined_body, ".agents/skills/", ".agents/wiki/")
        antigravity_body = append_delegation_logic(name, antigravity_body, 'antigravity')
        
        # 4. Write agent configurations out
        write_gemini_agent(name, fm, gemini_body, gemini_tools, temperature)
        write_claude_agent(name, fm, claude_body, claude_tools, temperature, claude_model)
        write_pi_agent(name, fm, pi_body, pi_tools, temperature)
        write_antigravity_agent(name, fm, antigravity_body, antigravity_tools, temperature)
            
    # Compile footprint stats
    full_rules_len = len(core_block) + len(devops_block) + len(ast_block)
    naive_total = total_raw_chars + full_rules_len * processed_count
    selective_savings = naive_total - total_precompile_chars
    minified = total_precompile_chars - total_compiled_chars
    
    print(f"Processed {processed_count} agents across all platforms.")
    print(f"[COMPILE] Raw agent bodies: {total_raw_chars} chars; after selective stitching: {total_precompile_chars} chars; compiled: {total_compiled_chars} chars.")
    print(f"[COMPILE] Selective rule stitching saved ~{selective_savings} chars (~{max(selective_savings, 0) // 4} tokens) vs embedding all shared rules in every agent.")
    print(f"[COMPILE] Comment-strip & whitespace minification removed ~{minified} chars (~{max(minified, 0) // 4} tokens) per platform.")

def process_skills():
    skill_dirs = glob.glob(os.path.join(OPENCODE_DIR, "skills", "*"))
    skill_count = 0
    
    for skill_dir in skill_dirs:
        if not os.path.isdir(skill_dir):
            continue
        name = os.path.basename(skill_dir)
        
        skill_file = None
        for candidate in ["SKILL.md", "skill.md"]:
            p = os.path.join(skill_dir, candidate)
            if os.path.exists(p):
                skill_file = p
                break
                
        if not skill_file:
            continue
        skill_count += 1
        
        fm, body = parse_md(skill_file)
        desc = fm.get('description', '')
        
        # --- 1. Gemini Skill ---
        gemini_skill_dir = os.path.join(GEMINI_SKILLS_DIR, name)
        shutil.copytree(skill_dir, gemini_skill_dir)
        if os.path.exists(os.path.join(gemini_skill_dir, "skill.md")) and os.path.join(gemini_skill_dir, "skill.md") != os.path.join(gemini_skill_dir, "SKILL.md"):
            os.remove(os.path.join(gemini_skill_dir, "skill.md"))
        
        gemini_fm = f"---\nname: {name}\ndescription: {yaml_dq(desc)}\n---\n"
        gemini_body = body.replace(".opencode/skills/", ".gemini/skills/")
        with open(os.path.join(gemini_skill_dir, "SKILL.md"), 'w') as f:
            f.write(gemini_fm + gemini_body)
            
        # --- 2. Claude Command & Skill ---
        claude_fm = f"---\nname: {name}\ndescription: {yaml_dq(desc)}\n---\n"
        claude_body = body.replace(".opencode/skills/", ".claude/skills/")
        with open(os.path.join(CLAUDE_CMDS_DIR, f"{name}.md"), 'w') as f:
            f.write(claude_fm + claude_body)
            
        claude_skill_dir = os.path.join(CLAUDE_SKILLS_DIR, name)
        shutil.copytree(skill_dir, claude_skill_dir)
        claude_lower_skill = os.path.join(claude_skill_dir, "skill.md")
        claude_upper_skill = os.path.join(claude_skill_dir, "SKILL.md")
        if os.path.exists(claude_lower_skill) and claude_lower_skill != claude_upper_skill:
            os.remove(claude_lower_skill)
        with open(claude_upper_skill, 'w') as f:
            f.write(f"---\nname: {name}\ndescription: {yaml_dq(desc)}\n---\n" + claude_body)
            
        # --- 3. Pi Skill ---
        pi_skill_dir = os.path.join(PI_SKILLS_DIR, name)
        shutil.copytree(skill_dir, pi_skill_dir)
        if os.path.exists(os.path.join(pi_skill_dir, "skill.md")) and os.path.join(pi_skill_dir, "skill.md") != os.path.join(pi_skill_dir, "SKILL.md"):
            os.remove(os.path.join(pi_skill_dir, "skill.md"))
        
        pi_fm = f"---\nname: {name}\ndescription: {yaml_dq(desc)}\n---\n"
        pi_body = body.replace(".opencode/skills/", ".pi/skills/")
        with open(os.path.join(pi_skill_dir, "SKILL.md"), 'w') as f:
            f.write(pi_fm + pi_body)

        # --- 4. Antigravity Skill ---
        antigravity_skill_dir = os.path.join(ANTIGRAVITY_SKILLS_DIR, name)
        shutil.copytree(skill_dir, antigravity_skill_dir)
        if os.path.exists(os.path.join(antigravity_skill_dir, "skill.md")) and os.path.join(antigravity_skill_dir, "skill.md") != os.path.join(antigravity_skill_dir, "SKILL.md"):
            os.remove(os.path.join(antigravity_skill_dir, "skill.md"))
            
        antigravity_fm = f"---\nname: {name}\ndescription: {yaml_dq(desc)}\n---\n"
        antigravity_body = body.replace(".opencode/skills/", ".agents/skills/")
        with open(os.path.join(antigravity_skill_dir, "SKILL.md"), 'w') as f:
            f.write(antigravity_fm + antigravity_body)
            
    print(f"Processed and recursively synced {skill_count} skills across all platforms.")

def process_configs():
    # 1. Process AGENTS.md / GEMINI.md / CLAUDE.md
    agents_md_path = os.path.join(OPENCODE_ROOT, 'AGENTS.md')
    if os.path.exists(agents_md_path):
        with open(agents_md_path, 'r') as f:
            md_content = f.read()
        
        with open(os.path.join(GEMINI_ROOT, 'GEMINI.md'), 'w') as f:
            f.write(md_content.replace('AGENTS.md', 'GEMINI.md'))
            
        with open(os.path.join(CLAUDE_ROOT, 'CLAUDE.md'), 'w') as f:
            f.write(md_content.replace('AGENTS.md', 'CLAUDE.md'))

        with open(os.path.join(PI_ROOT, 'AGENTS.md'), 'w') as f:
            f.write(md_content)

        with open(os.path.join(ANTIGRAVITY_ROOT, 'AGENTS.md'), 'w') as f:
            f.write(md_content)
        os.makedirs(os.path.join(ANTIGRAVITY_ROOT, ".agents"), exist_ok=True)
        with open(os.path.join(ANTIGRAVITY_ROOT, '.agents', 'AGENTS.md'), 'w') as f:
            f.write(md_content)
            
        print("Synchronized AGENTS.md rules.")

    # 2. Process opencode.json configurations
    opencode_json_path = os.path.join(OPENCODE_ROOT, 'opencode.json')
    if os.path.exists(opencode_json_path):
        with open(opencode_json_path, 'r') as f:
            config = json.load(f)

        platform_models = resolve_platform_models(config)

        # Gemini config
        gemini_config = json.loads(json.dumps(config))
        gemini_config.pop('mcp', None)
        gemini_config.pop('provider', None)
        gemini_config['model'] = platform_models['gemini']
        gemini_config['instructions'] = ["GEMINI.md", "migration-config.json"]
        gemini_config['permission'] = {
            "read_file": "allow",
            "write_file": "allow",
            "replace": "allow",
            "run_shell_command": "allow",
            "glob": "allow",
            "search_file_content": "allow",
            "web_fetch": "allow",
            "google_web_search": "allow",
            "skill": config['permission'].get('skill', {})
        }
        with open(os.path.join(GEMINI_ROOT, 'gemini.json'), 'w') as f:
            json.dump(gemini_config, f, indent=2)
 
        # Claude config
        claude_config = json.loads(json.dumps(config))
        claude_config.pop('mcp', None)
        claude_config.pop('provider', None)
        claude_config['model'] = platform_models['claude']
        claude_config['instructions'] = ["CLAUDE.md", "migration-config.json"]
        claude_config['permission'] = {
            "Read": "allow",
            "Write": "allow",
            "Edit": "allow",
            "Bash": "allow",
            "Glob": "allow",
            "Grep": "allow",
            "WebFetch": "allow",
            "WebSearch": "allow",
            "command": config['permission'].get('skill', {})
        }
        with open(os.path.join(CLAUDE_ROOT, 'claude.json'), 'w') as f:
            json.dump(claude_config, f, indent=2)
        os.makedirs(os.path.join(CLAUDE_ROOT, '.claude'), exist_ok=True)
        with open(os.path.join(CLAUDE_ROOT, '.claude', 'config.json'), 'w') as f:
            json.dump(claude_config, f, indent=2)

        claude_settings = {
            "permissions": {
                "defaultMode": "bypassPermissions"
            }
        }
        with open(os.path.join(CLAUDE_ROOT, '.claude', 'settings.json'), 'w') as f:
            json.dump(claude_settings, f, indent=2)

        # Pi config
        model = config.get('model', 'lmstudio/gemma-4-e4b-it')
        pi_config_content = f"""export default {{
  model: "{model}",
  skillsDir: "./.pi/skills",
  promptsDir: "./.pi/prompts",
  extensions: [
    "pi-opencode-bridge"
  ]
}};
"""
        with open(os.path.join(PI_ROOT, 'pi.config.ts'), 'w') as f:
            f.write(pi_config_content)

        # Generate Pi models configuration (.pi/models.json)
        pi_models = {"providers": {}}
        for prov_id, prov_data in config.get('provider', {}).items():
            options = prov_data.get('options', {})
            base_url = options.get('baseURL') or options.get('baseUrl')
            if base_url:
                models_list = []
                for model_id in prov_data.get('models', {}).keys():
                    models_list.append({"id": model_id})
                
                pi_models["providers"][prov_id] = {
                    "baseUrl": base_url,
                    "api": "openai-completions",
                    "apiKey": prov_id,
                    "models": models_list
                }
        
        pi_models_path = os.path.join(PI_ROOT, '.pi', 'models.json')
        os.makedirs(os.path.dirname(pi_models_path), exist_ok=True)
        with open(pi_models_path, 'w') as f:
            json.dump(pi_models, f, indent=2)

        # Generate Pi settings configuration (.pi/settings.json)
        pi_settings = {}
        if '/' in model:
            parts = model.split('/', 1)
            pi_settings['defaultProvider'] = parts[0]
            pi_settings['defaultModel'] = parts[1]
        else:
            pi_settings['defaultModel'] = model
            
        pi_settings_path = os.path.join(PI_ROOT, '.pi', 'settings.json')
        with open(pi_settings_path, 'w') as f:
            json.dump(pi_settings, f, indent=2)

        # Antigravity config
        antigravity_config = json.loads(json.dumps(config))
        antigravity_config.pop('mcp', None)
        antigravity_config.pop('provider', None)
        antigravity_config['model'] = platform_models['antigravity']
        antigravity_config['instructions'] = ["AGENTS.md", "migration-config.json"]
        antigravity_config['permission'] = {
            "read_file": "allow",
            "write_file": "allow",
            "run_command": "allow",
            "grep_search": "allow",
            "list_dir": "allow",
            "view_file": "allow",
            "write_to_file": "allow",
            "replace_file_content": "allow",
            "multi_replace_file_content": "allow",
            "web_fetch": "allow",
            "skill": config['permission'].get('skill', {})
        }
        with open(os.path.join(ANTIGRAVITY_ROOT, 'antigravity.json'), 'w') as f:
            json.dump(antigravity_config, f, indent=2)
        with open(os.path.join(ANTIGRAVITY_ROOT, '.agents', 'config.json'), 'w') as f:
            json.dump(antigravity_config, f, indent=2)

        # MCP config mapping (mcp -> mcpServers)
        mcp_servers = {}
        for server_name, server_data in config.get('mcp', {}).items():
            server_conf = {}
            if 'command' in server_data:
                cmd_val = server_data['command']
                if isinstance(cmd_val, list):
                    if len(cmd_val) > 0:
                        server_conf['command'] = cmd_val[0]
                        server_conf['args'] = cmd_val[1:]
                    else:
                        server_conf['command'] = ""
                        server_conf['args'] = []
                else:
                    server_conf['command'] = cmd_val
                    if 'args' in server_data:
                        server_conf['args'] = server_data['args']
            if 'env' in server_data:
                server_conf['env'] = server_data['env']
            mcp_servers[server_name] = server_conf
        
        mcp_config_data = {
            "mcpServers": mcp_servers
        }
        
        # Write MCP Configs to each platform's native discovery location
        with open(os.path.join(ANTIGRAVITY_ROOT, '.agents', 'mcp_config.json'), 'w') as f:
            json.dump(mcp_config_data, f, indent=2)
        with open(os.path.join(CLAUDE_ROOT, '.claude', 'mcp_config.json'), 'w') as f:
            json.dump(mcp_config_data, f, indent=2)
        with open(os.path.join(CLAUDE_ROOT, '.mcp.json'), 'w') as f:
            json.dump(mcp_config_data, f, indent=2)

        gemini_settings_path = os.path.join(GEMINI_ROOT, '.gemini', 'settings.json')
        os.makedirs(os.path.dirname(gemini_settings_path), exist_ok=True)
        with open(gemini_settings_path, 'w') as f:
            json.dump(mcp_config_data, f, indent=2)

        pi_mcp_path = os.path.join(PI_ROOT, '.pi', 'mcp.json')
        os.makedirs(os.path.dirname(pi_mcp_path), exist_ok=True)
        with open(pi_mcp_path, 'w') as f:
            json.dump(mcp_config_data, f, indent=2)

        print("Successfully generated configuration files for all platforms.")

if __name__ == "__main__":
    print("Starting sync from opencode to gemini-cli, claude-cli, pi-cli, and antigravity-cli...")
    setup_directories()
    process_agents()
    process_skills()
    process_configs()
    print("Sync complete! Generated configurations, agents, skills, and wikis.")
