# UltraThink CLI (Claude Code Skill)

A CLI tool for sequential thinking and problem-solving.

> **Note:** This is the **Claude Code Skill** version of [UltraThink MCP Server](https://github.com/husniadil/ultrathink).
> It provides the same sequential thinking capabilities as a standalone CLI tool that can be used as a Claude Code skill.

## Features

- Sequential thinking with session management
- Confidence scoring (0.0-1.0 scale)
- Assumption tracking with dependencies
- Branching and revision support
- Session persistence (survives across CLI invocations)
- Cross-platform temp directory storage

## Usage

```bash
# Show help
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py --help

# Start a new thinking session
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py --thought "Let me analyze this problem..." --total 5

# Short form
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "First step" -n 5

# Continue session (use session_id from previous output)
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Second step" -n 5 -s <session-id>

# With confidence
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "I believe X is correct" -n 3 -c 0.8
```

## Documentation

See [SKILL.md](skills/ultrathink/SKILL.md) for complete documentation including:

- All CLI options
- Assumption tracking
- Branching and revision
- Response schema
- Examples

## License

MIT

## Credits

Based on [UltraThink MCP Server](https://github.com/husniadil/ultrathink), which is a Python port of the [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) by Anthropic.
