# interview

A Claude Code plugin for deep requirements gathering through thoughtful, in-depth interviews before implementation.

## Features

- CDEEPER workflow: Contextualize, Discover, Explore, Edge, Prioritize, Experience, Ready
- Codebase exploration before questioning (avoids obvious questions)
- Non-obvious, thought-provoking questions that uncover hidden requirements
- Adaptive questioning based on domain (frontend, backend, infrastructure, etc.)
- Edge case and boundary condition exploration
- Trade-off and priority clarification
- Graceful early-exit with partial requirements summary
- Multi-session support with explicit phase tracking
- Seamless transition to plan mode when interview is complete

## Installation

```bash
claude plugin install interview@ekstend
```

## Usage

Invoke the interview skill when you have a feature or task to implement:

- `/interview` - Start an interview for the current context
- "Interview me about this feature before implementing"
- "Let's deep dive into the requirements for this task"

You can also point to a plan file:

- `/interview plan.md` - Interview based on the plan in plan.md

## Core Philosophy

**Deep Dive, Not Surface Skim**

The goal is to uncover requirements and edge cases the user hasn't explicitly considered. Rather than asking obvious questions about what the user already stated, this skill:

1. Discovers the core intent and goal
2. Probes technical implementation considerations
3. Uncovers edge cases and error states
4. Clarifies trade-offs and priorities
5. Explores UX/DX considerations
6. Confirms completeness before entering plan mode

## Workflow

0. **Contextualize** - Explore codebase for existing patterns
1. **Discover** - Understand intent from prompt or plan file
2. **Explore** - Ask about technical implementation details
3. **Edge** - Uncover edge cases, error states, boundaries
4. **Prioritize** - Clarify trade-offs, constraints, priorities
5. **Experience** - Probe UX/DX and user journeys
6. **Ready** - Confirm completeness, offer plan mode

## Question Categories

Questions span multiple categories:

- **Technical**: Architecture, data flow, integrations, performance
- **Edge Cases**: Error handling, boundary conditions, concurrent access
- **Trade-offs**: Performance vs simplicity, flexibility vs complexity
- **UX/DX**: User journeys, developer experience, API design
- **Security**: Authentication, authorization, data protection
- **Operations**: Deployment, monitoring, rollback strategies
