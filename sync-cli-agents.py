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
    workspace_items = ["DocumentationFactory", "knowledge", "migration-mapping", "validation", "migration-config.json", "run-multi-repo-coordinator.py"]
    
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
                    shutil.copytree(src, dst)
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

def parse_md(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    
    frontmatter_str = match.group(1)
    body = match.group(2)
    
    frontmatter = {}
    current_key = None
    for line in frontmatter_str.split('\n'):
        if not line.strip(): continue
        if line.startswith('  ') and current_key:
            if not isinstance(frontmatter[current_key], list):
                frontmatter[current_key] = []
            frontmatter[current_key].append(line.strip().split(':')[0].strip('- '))
        else:
            if ':' in line:
                k, v = line.split(':', 1)
                frontmatter[k.strip()] = v.strip().strip('"\'')
                current_key = k.strip()
    return frontmatter, body

def build_gemini_frontmatter(name, fm):
    desc = fm.get('description', '')
    tools = ['read_file', 'write_file', 'run_shell_command', 'search_file_content']
    res = f"---\nname: {name}\ndescription: \"{desc}\"\ntools:\n"
    for t in tools:
        res += f"  - {t}\n"
    res += "model: inherit\n---\n"
    return res

def build_claude_frontmatter(name, fm):
    desc = fm.get('description', '')
    mode = fm.get('mode', 'subagent')
    res = f"---\nname: {name}\ndescription: \"{desc}\"\ntools: Read, Write, Bash, Glob, Grep\nmodel: sonnet\nmode: {mode}\n---\n"
    return res

def build_pi_frontmatter(name, fm):
    desc = fm.get('description', '')
    res = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
    return res

def build_antigravity_frontmatter(name, fm):
    desc = fm.get('description', '')
    tools = ['read_file', 'write_file', 'run_command', 'grep_search', 'list_dir', 'view_file', 'write_to_file', 'replace_file_content', 'multi_replace_file_content']
    res = f"---\nname: {name}\ndescription: \"{desc}\"\ntools:\n"
    for t in tools:
        res += f"  - {t}\n"
    res += "model: inherit\n---\n"
    return res

def clean_markdown(text):
    # Remove HTML-style comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Compress multiple consecutive newlines into exactly two
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def process_agents():
    system_common_path = os.path.join(OPENCODE_DIR, "agents", "system_common.md")
    system_common_body = ""
    if os.path.exists(system_common_path):
        with open(system_common_path, 'r') as f:
            system_common_body = f.read()

    agent_files = glob.glob(os.path.join(OPENCODE_DIR, "agents", "*.md"))
    
    total_raw_chars = 0
    total_compiled_chars = 0
    processed_count = 0
    
    for filepath in agent_files:
        name = os.path.basename(filepath).replace('.md', '')
        if name == "system_common":
            continue
            
        fm, body = parse_md(filepath)
        processed_count += 1
        
        # Calculate raw characters (original body)
        raw_char_len = len(body)
        total_raw_chars += raw_char_len
        
        # Combine stitched body
        combined_body = body
        if system_common_body:
            combined_body += "\n\n## Global Shared Instructions\n" + system_common_body
            
        # Clean comments and compress whitespace
        combined_body = clean_markdown(combined_body)
        
        # Rewrite wiki and skill paths inside agent instructions (including relative and absolute variants)
        gemini_body = combined_body.replace("../.opencode/skills/", ".gemini/skills/") \
                          .replace(".opencode/skills/", ".gemini/skills/") \
                          .replace(".opencode/wiki/", ".gemini/wiki/")
        
        claude_body = combined_body.replace("../.opencode/skills/", ".claude/skills/") \
                          .replace(".opencode/skills/", ".claude/skills/") \
                          .replace(".opencode/wiki/", ".claude/wiki/")
        
        pi_body = combined_body.replace("../.opencode/skills/", ".pi/skills/") \
                      .replace(".opencode/skills/", ".pi/skills/") \
                      .replace(".opencode/wiki/", ".pi/wiki/")
        
        antigravity_body = combined_body.replace("../.opencode/skills/", ".agents/skills/") \
                                .replace(".opencode/skills/", ".agents/skills/") \
                                .replace(".opencode/wiki/", ".agents/wiki/")
        
        # Track compiled characters (we take antigravity body as baseline)
        total_compiled_chars += len(antigravity_body)
        
        # Inject CLI-specific delegation logic to the supervisor
        if name == "supervisor":
            gemini_body += "\n\n## CLI-Specific Autonomous Delegation (Gemini CLI)\n"
            gemini_body += "To invoke a subagent autonomously, you MUST use the `@<agent-name>` syntax in your prompt (e.g., `@code-reviewer please review the generated files`).\n"
            gemini_body += "To utilize a skill, ensure you request it via standard prompt interaction or slash commands like `/skills <skill-name>` if available.\n"
            
            claude_body += "\n\n## CLI-Specific Autonomous Delegation (Claude Code CLI)\n"
            claude_body += "To invoke a subagent autonomously, you MUST use the `Bash` tool to run the Claude CLI in non-interactive/headless mode with the `-p` flag and skip permissions (e.g., `claude -p --dangerously-skip-permissions --agent code-reviewer \"Please review the generated files\"`). This is essential to prevent terminal hangs and ensure the process runs fully autonomously.\n"
            claude_body += "To utilize a skill/command, invoke the custom slash command `/<skill-name>` natively or run `claude -p --dangerously-skip-permissions /<skill-name>` via the Bash tool.\n"

            pi_body += "\n\n## CLI-Specific Autonomous Delegation (pi.dev)\n"
            pi_body += "To invoke a subagent autonomously, you MUST use `/<agent-name>` to expand its Prompt Template (e.g., `/code-reviewer`).\n"
            pi_body += "To utilize a skill, load it when your tasks match its description or invoke it directly if supported.\n"

            antigravity_body += "\n\n## CLI-Specific Autonomous Delegation (Antigravity CLI)\n"
            antigravity_body += "To invoke a subagent autonomously, you MUST use the `invoke_subagent` tool or the `@<agent-name>` syntax in your prompt (e.g., `@code-reviewer please review the generated files`).\n"
            antigravity_body += "To utilize a skill, ensure you refer to the skills configured under `.agents/skills/` (the platform automatically discovers them) or trigger them via slash commands like `/skills <skill-name>`.\n"

        # Gemini CLI Output
        gemini_fm = build_gemini_frontmatter(name, fm)
        with open(os.path.join(GEMINI_AGENTS_DIR, f"{name}.md"), 'w') as f:
            f.write(gemini_fm + gemini_body)
            
        # Claude CLI Output
        claude_fm = build_claude_frontmatter(name, fm)
        claude_target_dir = CLAUDE_AGENTS_DIR
        if fm.get('mode') != 'primary':
            claude_target_dir = os.path.join(CLAUDE_AGENTS_DIR, "subagents")
            os.makedirs(claude_target_dir, exist_ok=True)
        with open(os.path.join(claude_target_dir, f"{name}.md"), 'w') as f:
            f.write(claude_fm + claude_body)

        # Pi CLI Output
        pi_fm = build_pi_frontmatter(name, fm)
        with open(os.path.join(PI_AGENTS_DIR, f"{name}.md"), 'w') as f:
            f.write(pi_fm + pi_body)

        # Antigravity CLI Output
        agent_dir = os.path.join(ANTIGRAVITY_AGENTS_DIR, name)
        os.makedirs(agent_dir, exist_ok=True)
        
        agent_config = {
            "name": name,
            "description": fm.get('description', ''),
            "model": "inherit",
            "tools": ['read_file', 'write_file', 'run_command', 'grep_search', 'list_dir', 'view_file', 'write_to_file', 'replace_file_content', 'multi_replace_file_content'],
            "system_instructions": antigravity_body,
            "instructions": antigravity_body
        }
        with open(os.path.join(agent_dir, "agent.json"), 'w') as f:
            json.dump(agent_config, f, indent=2)
            
        with open(os.path.join(agent_dir, "instructions.md"), 'w') as f:
            f.write(antigravity_body)
            
    # Calculate and report prompt compilation savings
    savings_chars = (total_raw_chars + (len(system_common_body) * processed_count)) - total_compiled_chars
    print(f"Processed {processed_count} agents across all platforms.")
    print(f"[TOKEN SAVINGS] Combined total characters before compile: {total_raw_chars + (len(system_common_body) * processed_count)}")
    print(f"[TOKEN SAVINGS] Stitched & Minified characters after compile: {total_compiled_chars}")
    print(f"[TOKEN SAVINGS] Dynamic prompt minification saved ~{savings_chars} characters (~{int(savings_chars / 4)} tokens) per platform run!")

def process_skills():
    skill_dirs = glob.glob(os.path.join(OPENCODE_DIR, "skills", "*"))
    skill_count = 0
    
    for skill_dir in skill_dirs:
        if not os.path.isdir(skill_dir): continue
        name = os.path.basename(skill_dir)
        
        # Case-insensitive matching for SKILL.md
        skill_file = None
        for candidate in ["SKILL.md", "skill.md"]:
            p = os.path.join(skill_dir, candidate)
            if os.path.exists(p):
                skill_file = p
                break
                
        if not skill_file: continue
        skill_count += 1
        
        fm, body = parse_md(skill_file)
        desc = fm.get('description', '')
        
        # --- 1. Gemini Skill (Recursive copy + rewrite paths) ---
        gemini_skill_dir = os.path.join(GEMINI_SKILLS_DIR, name)
        shutil.copytree(skill_dir, gemini_skill_dir)
        if os.path.exists(os.path.join(gemini_skill_dir, "skill.md")) and os.path.join(gemini_skill_dir, "skill.md") != os.path.join(gemini_skill_dir, "SKILL.md"):
            os.remove(os.path.join(gemini_skill_dir, "skill.md"))
        
        gemini_fm = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
        gemini_body = body.replace(".opencode/skills/", ".gemini/skills/")
        with open(os.path.join(gemini_skill_dir, "SKILL.md"), 'w') as f:
            f.write(gemini_fm + gemini_body)
            
        # --- 2. Claude Command & Skill ---
        # Claude commands are single files
        claude_fm = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
        claude_body = body.replace(".opencode/skills/", ".claude/skills/")
        with open(os.path.join(CLAUDE_CMDS_DIR, f"{name}.md"), 'w') as f:
            f.write(claude_fm + claude_body)
        # Claude helper scripts and resources
        claude_skill_dir = os.path.join(CLAUDE_SKILLS_DIR, name)
        shutil.copytree(skill_dir, claude_skill_dir)
            
        # --- 3. Pi Skill ---
        pi_skill_dir = os.path.join(PI_SKILLS_DIR, name)
        shutil.copytree(skill_dir, pi_skill_dir)
        if os.path.exists(os.path.join(pi_skill_dir, "skill.md")) and os.path.join(pi_skill_dir, "skill.md") != os.path.join(pi_skill_dir, "SKILL.md"):
            os.remove(os.path.join(pi_skill_dir, "skill.md"))
        
        pi_fm = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
        pi_body = body.replace(".opencode/skills/", ".pi/skills/")
        with open(os.path.join(pi_skill_dir, "SKILL.md"), 'w') as f:
            f.write(pi_fm + pi_body)

        # --- 4. Antigravity Skill (Recursive copy + rewrite paths) ---
        antigravity_skill_dir = os.path.join(ANTIGRAVITY_SKILLS_DIR, name)
        shutil.copytree(skill_dir, antigravity_skill_dir)
        if os.path.exists(os.path.join(antigravity_skill_dir, "skill.md")) and os.path.join(antigravity_skill_dir, "skill.md") != os.path.join(antigravity_skill_dir, "SKILL.md"):
            os.remove(os.path.join(antigravity_skill_dir, "skill.md"))
            
        antigravity_fm = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
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

        # Antigravity CLI workspace context
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

        # Gemini config
        gemini_config = json.loads(json.dumps(config))
        gemini_config['instructions'] = ["GEMINI.md", "migration-config.json"]
        gemini_config['permission'] = {
            "read_file": "allow",
            "write_file": "allow",
            "run_shell_command": "allow",
            "search_file_content": "allow",
            "web_fetch": "allow",
            "skill": config['permission'].get('skill', {})
        }
        with open(os.path.join(GEMINI_ROOT, 'gemini.json'), 'w') as f:
            json.dump(gemini_config, f, indent=2)
 
        # Claude config
        claude_config = json.loads(json.dumps(config))
        claude_config['instructions'] = ["CLAUDE.md", "migration-config.json"]
        claude_config['permission'] = {
            "Read": "allow",
            "Write": "allow",
            "Bash": "allow",
            "Glob": "allow",
            "Grep": "allow",
            "Fetch": "allow",
            "command": config['permission'].get('skill', {})
        }
        with open(os.path.join(CLAUDE_ROOT, 'claude.json'), 'w') as f:
            json.dump(claude_config, f, indent=2)
        os.makedirs(os.path.join(CLAUDE_ROOT, '.claude'), exist_ok=True)
        with open(os.path.join(CLAUDE_ROOT, '.claude', 'config.json'), 'w') as f:
            json.dump(claude_config, f, indent=2)

        # Generate Claude settings.json to disable all permission prompts for fully autonomous operation
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
  promptsDir: "./.pi/prompts"
}};
"""
        with open(os.path.join(PI_ROOT, 'pi.config.ts'), 'w') as f:
            f.write(pi_config_content)

        # Antigravity config
        antigravity_config = json.loads(json.dumps(config))
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
        
        # Write MCP Configs
        with open(os.path.join(ANTIGRAVITY_ROOT, '.agents', 'mcp_config.json'), 'w') as f:
            json.dump(mcp_config_data, f, indent=2)
        with open(os.path.join(CLAUDE_ROOT, '.claude', 'mcp_config.json'), 'w') as f:
            json.dump(mcp_config_data, f, indent=2)

        print("Successfully generated configuration files for all platforms.")

if __name__ == "__main__":
    print("Starting sync from opencode to gemini-cli, claude-cli, pi-cli, and antigravity-cli...")
    setup_directories()
    process_agents()
    process_skills()
    process_configs()
    print("Sync complete! Generated configurations, agents, skills, and wikis.")
