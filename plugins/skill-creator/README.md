# Skill Creator (Claude Code Skill)

A guide for creating effective skills that extend Claude's capabilities with specialized knowledge, workflows, or tool integrations.

## Features

- Step-by-step skill creation guidance
- Best practices for context management
- Progressive disclosure design patterns
- Scripts for initializing, validating, and packaging skills

## Usage

This skill is automatically invoked when you ask Claude to create or update a skill. You can also use the utility scripts directly:

```bash
# Initialize a new skill
uv run ${CLAUDE_PLUGIN_ROOT}/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>

# Validate a skill
uv run ${CLAUDE_PLUGIN_ROOT}/skills/skill-creator/scripts/quick_validate.py <path/to/skill-folder>

# Package a skill for distribution
uv run ${CLAUDE_PLUGIN_ROOT}/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

## Documentation

See [skills/skill-creator/SKILL.md](skills/skill-creator/SKILL.md) for complete documentation including:

- Core principles (concise design, degrees of freedom)
- Anatomy of a skill
- 6-step skill creation process
- Reference documentation for workflows and output patterns

## License

Apache License 2.0 - See [LICENSE.txt](LICENSE.txt) for details.

## Credits

Originally created by [Anthropic](https://github.com/anthropics/skills).
