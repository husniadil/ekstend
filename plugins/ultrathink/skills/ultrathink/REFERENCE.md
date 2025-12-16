# UltraThink CLI Reference

Complete documentation for the UltraThink sequential thinking CLI.

## CLI Options

### Required

| Option      | Short | Description                                                                                                                       |
| ----------- | ----- | --------------------------------------------------------------------------------------------------------------------------------- |
| `--thought` | `-t`  | Your current thinking step. Can include: analytical steps, revisions, questions, realizations, hypothesis generation/verification |
| `--total`   | `-n`  | Estimated total thoughts needed (can adjust as you progress)                                                                      |

### Session Management

| Option             | Short | Description                                                                  |
| ------------------ | ----- | ---------------------------------------------------------------------------- |
| `--session-id`     | `-s`  | Session identifier. Omit to create new session, provide to continue existing |
| `--thought-number` | -     | Override auto-numbering (auto-assigned if omitted)                           |

### Confidence & Metadata

| Option                | Short | Description                                                                                                |
| --------------------- | ----- | ---------------------------------------------------------------------------------------------------------- |
| `--confidence`        | `-c`  | Confidence level 0.0-1.0. Low (0.3-0.6): exploratory. Medium (0.6-0.8): reasoned. High (0.8-1.0): verified |
| `--uncertainty-notes` | -     | Explanation for doubts or concerns                                                                         |
| `--outcome`           | -     | What was achieved or expected                                                                              |

### Revision & Branching

| Option          | Description                                |
| --------------- | ------------------------------------------ |
| `--is-revision` | Mark as revision of previous thought       |
| `--revises`     | Which thought number is being reconsidered |
| `--branch-from` | Thought number to branch from              |
| `--branch-id`   | Identifier for the new branch              |

### Assumptions

| Option          | Description                                          |
| --------------- | ---------------------------------------------------- |
| `--assumptions` | JSON array of assumption objects                     |
| `--depends-on`  | JSON array of assumption IDs this thought depends on |
| `--invalidates` | JSON array of assumption IDs proven false            |

### Control Flow

| Option          | Description                                     |
| --------------- | ----------------------------------------------- |
| `--needs-more`  | Flag if more thoughts needed beyond estimate    |
| `--next-needed` | Override auto-assignment of next_thought_needed |

## Response Schema

```json
{
  "session_id": "uuid-string",
  "thought_number": 1,
  "total_thoughts": 5,
  "next_thought_needed": true,
  "branches": [],
  "thought_history_length": 1,
  "confidence": null,
  "uncertainty_notes": null,
  "outcome": null,
  "all_assumptions": {},
  "risky_assumptions": [],
  "falsified_assumptions": [],
  "unresolved_references": [],
  "cross_session_warnings": []
}
```

| Field                    | Type        | Description                                   |
| ------------------------ | ----------- | --------------------------------------------- |
| `session_id`             | string      | UUID to continue session                      |
| `thought_number`         | int         | Current position (1-indexed)                  |
| `total_thoughts`         | int         | Estimated total                               |
| `next_thought_needed`    | bool        | Whether to continue thinking                  |
| `branches`               | string[]    | Active branch IDs                             |
| `thought_history_length` | int         | Total thoughts processed                      |
| `confidence`             | float\|null | 0.0-1.0 if provided                           |
| `all_assumptions`        | object      | Map of assumption ID to assumption object     |
| `risky_assumptions`      | string[]    | IDs of critical + low confidence + unverified |
| `falsified_assumptions`  | string[]    | IDs proven false                              |
| `unresolved_references`  | string[]    | Cross-session refs that couldn't be resolved  |
| `cross_session_warnings` | string[]    | Warnings from cross-session operations        |

## Assumption Schema

```json
{
  "id": "A1",
  "text": "The assumption text",
  "critical": true,
  "confidence": 1.0,
  "verifiable": false,
  "evidence": null,
  "verification_status": null
}
```

| Field                 | Type   | Required | Default | Description                                     |
| --------------------- | ------ | -------- | ------- | ----------------------------------------------- |
| `id`                  | string | Yes      | -       | Unique ID like "A1", "A2"                       |
| `text`                | string | Yes      | -       | The assumption being made                       |
| `critical`            | bool   | No       | true    | If false, does reasoning collapse?              |
| `confidence`          | float  | No       | 1.0     | 0.0-1.0 confidence in assumption                |
| `verifiable`          | bool   | No       | false   | Can be verified through testing?                |
| `evidence`            | string | No       | null    | Why you believe this                            |
| `verification_status` | string | No       | null    | "unverified", "verified_true", "verified_false" |

## Examples

### Basic Session

```bash
# Step 1 - start
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Define the problem: need to optimize slow API" -n 3

# Step 2 - continue
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Identify cause: N+1 query in user list" -n 3 -s SESSION_ID

# Step 3 - conclude
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Solution: add eager loading for user relations" -n 3 -s SESSION_ID
```

### Revision

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Actually, the issue is not N+1 but missing index" -n 5 \
  --is-revision --revises 2 -s SESSION_ID
```

### Branching

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Alternative: use caching instead of query optimization" -n 5 \
  --branch-from 2 --branch-id "cache-approach" -s SESSION_ID
```

### Working with Assumptions

```bash
# Create assumption
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Assuming Redis is available for caching" -n 5 \
  --assumptions '[{"id":"A1","text":"Redis is available","critical":true}]'

# Depend on assumption
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Design cache layer using Redis" -n 5 \
  --depends-on '["A1"]' -s SESSION_ID

# Invalidate assumption
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Redis not available, need alternative" -n 5 \
  --invalidates '["A1"]' -s SESSION_ID
```

### Full Assumption Object

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Assuming the API works" -n 3 \
  --assumptions '[{"id":"A1","text":"API is available","critical":true,"confidence":0.8,"verifiable":true}]'
```

### Cross-Session References

```bash
# Session 1: Create assumption
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Redis will work" -n 3 \
  --assumptions '[{"id":"A1","text":"Redis latency < 5ms"}]'
# Returns session_id: "abc-123"

# Session 2: Reference from session 1
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Building on previous assumption" -n 3 \
  --depends-on '["abc-123:A1"]'
```

### Scripting with jq

```bash
# Capture session_id
SESSION=$(uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Start analysis" -n 5 | jq -r '.session_id')

# Continue
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Continue analysis" -n 5 -s "$SESSION"

# Check if more thoughts needed
CONTINUE=$(uv run ${CLAUDE_PLUGIN_ROOT}/skills/ultrathink/ultrathink.py -t "Step" -n 5 -s "$SESSION" | jq -r '.next_thought_needed')
```

## Session Persistence

Sessions are persisted to: `<tempdir>/ultrathink/sessions/`

Find your temp directory:

```bash
python3 -c "import tempfile; print(tempfile.gettempdir())"
```

Session ID constraints:

- Alphanumeric characters, hyphens, underscores only
- Maximum 128 characters

## Error Responses

Errors output JSON to stderr with exit code 1:

```json
{
  "error": "validation_error",
  "details": [{ "loc": ["thought"], "msg": "field required" }]
}
```

```json
{
  "error": "value_error",
  "message": "Cannot depend on assumption A1: assumption not found"
}
```

## Limitations

- **Cross-session invalidation not supported**: Attempting to invalidate `session-x:A1` produces warning
- **No assumption copying**: Cross-session refs track dependencies only, don't copy assumptions
