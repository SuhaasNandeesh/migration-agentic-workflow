#!/usr/bin/env python3
"""
Sync Script for CLI Agentic Workflow
------------------------------------
This script reads the master configuration, agents, and skills from the
`opencode` directory and translates them into the native formats required
by both `gemini-cli` and `claude-cli`.

Usage:
    python3 sync-cli-agents.py

Run this script anytime you add, modify, or delete an agent or skill
in the `opencode` folder to ensure your Gemini and Claude CLI environments
remain up-to-date.
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

# Target directories
GEMINI_ROOT = os.path.join(BASE_DIR, "gemini-cli")
GEMINI_AGENTS_DIR = os.path.join(GEMINI_ROOT, ".gemini", "agents")
GEMINI_SKILLS_DIR = os.path.join(GEMINI_ROOT, ".gemini", "skills")

CLAUDE_ROOT = os.path.join(BASE_DIR, "claude-cli")
CLAUDE_AGENTS_DIR = os.path.join(CLAUDE_ROOT, ".claude", "agents")
CLAUDE_CMDS_DIR = os.path.join(CLAUDE_ROOT, ".claude", "commands")

PI_ROOT = os.path.join(BASE_DIR, "pi-cli")
PI_AGENTS_DIR = os.path.join(PI_ROOT, ".pi", "prompts")
PI_SKILLS_DIR = os.path.join(PI_ROOT, ".pi", "skills")

def setup_directories():
    # Clear out old generated agent/skill folders
    for d in [GEMINI_AGENTS_DIR, GEMINI_SKILLS_DIR, CLAUDE_AGENTS_DIR, CLAUDE_CMDS_DIR, PI_AGENTS_DIR, PI_SKILLS_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

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
    res = f"---\nname: {name}\ndescription: \"{desc}\"\ntools: Read, Write, Bash, Glob, Grep\nmodel: sonnet\n---\n"
    return res

def build_pi_frontmatter(name, fm):
    desc = fm.get('description', '')
    res = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
    return res

def process_agents():
    agent_files = glob.glob(os.path.join(OPENCODE_DIR, "agents", "*.md"))
    for filepath in agent_files:
        name = os.path.basename(filepath).replace('.md', '')
        fm, body = parse_md(filepath)
        
        gemini_body = body
        claude_body = body
        pi_body = body
        
        # Inject CLI-specific delegation logic to the supervisor
        if name == "supervisor":
            gemini_body += "\n\n## CLI-Specific Autonomous Delegation (Gemini CLI)\n"
            gemini_body += "To invoke a subagent autonomously, you MUST use the `@<agent-name>` syntax in your prompt (e.g., `@code-reviewer please review the generated files`).\n"
            gemini_body += "To utilize a skill, ensure you request it via standard prompt interaction or slash commands like `/skills <skill-name>` if available.\n"
            
            claude_body += "\n\n## CLI-Specific Autonomous Delegation (Claude Code CLI)\n"
            claude_body += "To invoke a subagent autonomously, you MUST use the `Bash` tool to run the Claude CLI (e.g., `claude --agent code-reviewer \"Please review the generated files\"`).\n"
            claude_body += "To utilize a skill/command, invoke the custom slash command `/<skill-name>` natively or run `claude /<skill-name>` via the Bash tool.\n"

            pi_body += "\n\n## CLI-Specific Autonomous Delegation (pi.dev)\n"
            pi_body += "To invoke a subagent autonomously, you MUST use `/<agent-name>` to expand its Prompt Template (e.g., `/code-reviewer`).\n"
            pi_body += "To utilize a skill, load it when your tasks match its description or invoke it directly if supported.\n"

        gemini_fm = build_gemini_frontmatter(name, fm)
        with open(os.path.join(GEMINI_AGENTS_DIR, f"{name}.md"), 'w') as f:
            f.write(gemini_fm + gemini_body)
            
        claude_fm = build_claude_frontmatter(name, fm)
        with open(os.path.join(CLAUDE_AGENTS_DIR, f"{name}.md"), 'w') as f:
            f.write(claude_fm + claude_body)

        pi_fm = build_pi_frontmatter(name, fm)
        with open(os.path.join(PI_AGENTS_DIR, f"{name}.md"), 'w') as f:
            f.write(pi_fm + pi_body)

def process_skills():
    skill_dirs = glob.glob(os.path.join(OPENCODE_DIR, "skills", "*"))
    for skill_dir in skill_dirs:
        if not os.path.isdir(skill_dir): continue
        name = os.path.basename(skill_dir)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_file): continue
        
        fm, body = parse_md(skill_file)
        desc = fm.get('description', '')
        
        # Gemini Skill (nested folder with SKILL.md)
        gemini_skill_dir = os.path.join(GEMINI_SKILLS_DIR, name)
        os.makedirs(gemini_skill_dir, exist_ok=True)
        gemini_fm = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
        with open(os.path.join(gemini_skill_dir, "SKILL.md"), 'w') as f:
            f.write(gemini_fm + body)
            
        # Claude Command (standalone md file)
        claude_fm = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
        with open(os.path.join(CLAUDE_CMDS_DIR, f"{name}.md"), 'w') as f:
            f.write(claude_fm + body)
            
        # Pi Skill (nested folder with SKILL.md)
        pi_skill_dir = os.path.join(PI_SKILLS_DIR, name)
        os.makedirs(pi_skill_dir, exist_ok=True)
        pi_fm = f"---\nname: {name}\ndescription: \"{desc}\"\n---\n"
        with open(os.path.join(pi_skill_dir, "SKILL.md"), 'w') as f:
            f.write(pi_fm + body)

def process_configs():
    # 1. Process AGENTS.md
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

    # 2. Process opencode.json
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

if __name__ == "__main__":
    print("Starting sync from opencode to gemini-cli, claude-cli, and pi-cli...")
    setup_directories()
    process_agents()
    process_skills()
    process_configs()
    print("Sync complete! Generated configurations, agents, and skills.")
