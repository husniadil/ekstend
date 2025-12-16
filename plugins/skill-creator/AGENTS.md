# AGENTS.md

Instructions for AI coding agents working on this plugin.

## Plugin Overview

This plugin provides guidance for creating effective skills that extend Claude's capabilities. Originally created by Anthropic, adapted for the ekstend marketplace.

## Structure

```
plugins/skill-creator/
  .claude-plugin/plugin.json    # Plugin metadata
  CLAUDE.md                     # Redirects to AGENTS.md
  AGENTS.md                     # This file
  README.md                     # Human documentation
  LICENSE.txt                   # Apache 2.0 license
  skills/
    skill-creator/
      SKILL.md                  # Main skill instructions
      scripts/                  # Utility scripts
        init_skill.py           # Initialize new skill
        quick_validate.py       # Validate skill structure
        package_skill.py        # Package skill for distribution
      references/               # Reference documentation
        workflows.md            # Workflow patterns
        output-patterns.md      # Output format guidance
```

## Development Guidelines

### Code Style

- Python: Follow PEP 8 conventions
- Use type hints where practical
- Run `ruff check` and `ruff format` before committing

### Testing Scripts

```bash
# Initialize a new skill
uv run plugins/skill-creator/skills/skill-creator/scripts/init_skill.py test-skill --path /tmp

# Validate a skill
uv run plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py /path/to/skill

# Package a skill
uv run plugins/skill-creator/skills/skill-creator/scripts/package_skill.py /path/to/skill
```

## Attribution

Originally created by [Anthropic](https://github.com/anthropics/skills) under Apache 2.0 license.
