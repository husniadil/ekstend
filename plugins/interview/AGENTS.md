# AGENTS.md

Instructions for AI coding agents working on the interview plugin.

## Overview

The interview plugin provides a deep requirements gathering skill that interviews users through thoughtful, in-depth questions before implementation. The core philosophy is to uncover hidden requirements, edge cases, and trade-offs that users may not initially consider.

## Structure

```
interview/
├── .claude-plugin/
│   └── plugin.json       # Plugin metadata
├── CLAUDE.md             # Redirects to AGENTS.md
├── AGENTS.md             # This file
├── README.md             # Human documentation
└── skills/
    └── interview/
        ├── SKILL.md      # Main skill instructions (DEEPER workflow)
        └── references/
            └── question-categories.md  # Question templates by category
```

## Key Concepts

### CDEEPER Workflow

The skill follows a 7-phase interview workflow:

0. **Contextualize** - Explore codebase to understand existing patterns before asking questions
1. **Discover** - Understand the intent/goal from prompt or plan file
2. **Explore** - Ask probing questions about technical implementation
3. **Edge** - Uncover edge cases, error states, and boundary conditions
4. **Prioritize** - Clarify trade-offs, constraints, and priorities
5. **Experience** - Probe UX/DX considerations and user journeys
6. **Ready** - Confirm completeness and offer to enter plan mode

### Question Philosophy

When modifying this skill, ensure questions are:

- **Non-obvious**: Don't ask what the user already stated
- **Thought-provoking**: Force consideration of overlooked aspects
- **Concrete**: Ask for specific scenarios, not abstract preferences
- **Layered**: Each answer should potentially reveal new question areas

### Anti-Patterns

When modifying this skill, avoid:

- Surface-level questions (things obvious from the prompt)
- Yes/no questions (prefer open-ended or scenario-based)
- Overwhelming users with too many questions at once (batch 1-4)
- Skipping to plan mode too early
- Ignoring context from previous answers

## Development Guidelines

- Keep SKILL.md focused on the core workflow
- Reference files should contain question templates and examples
- All changes should reinforce the "deep dive" philosophy
- Test by using the skill on real feature requests
- Questions should adapt based on domain (frontend, backend, infra, etc.)
