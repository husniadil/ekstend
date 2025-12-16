---
name: postgres-db
description: Use this skill when the user asks to connect to, query, access, or work with a PostgreSQL/Postgres database. Also use when the user mentions PostgreSQL tables, schemas, or wants to run SQL queries on Postgres. Supports credentials from user input or config files (.env, docker-compose.yml). IMPORTANT - Always ask user for credentials or credential file location first; never use shell environment variables without explicit user permission.
---

# PostgreSQL CLI

Access and manage PostgreSQL databases using the `psql` command-line client.

## Prerequisites

Verify psql CLI is installed:

```bash
psql --version
```

If not installed, inform user to install it via their package manager.

## Credential Acquisition

**CRITICAL: Never use environment variables from the shell without explicit user permission.**

When credentials are needed, ask the user using AskUserQuestion:

```
How would you like to provide PostgreSQL credentials?

1. Enter credentials manually (host, user, password, database)
2. Read from a file (provide path to .env, docker-compose.yml, or config file)
```

### Option 1: Manual Input

Ask for each field:

- Host (default: localhost)
- Port (default: 5432)
- Username
- Password
- Database name

### Option 2: Read from File

Supported formats:

**.env file:**

```
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=secret
PGDATABASE=myapp
# Also supports: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE
# Also supports: POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
```

**docker-compose.yml:**

```yaml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
      POSTGRES_USER: user
```

**Connection string:**

```
postgresql://user:password@host:port/database
postgres://user:password@host:port/database
```

**.pgpass file** (native PostgreSQL password file):

Location: `~/.pgpass` (Linux/macOS) or `%APPDATA%\postgresql\pgpass.conf` (Windows)

Format (one entry per line):

```
hostname:port:database:username:password
```

Example:

```
localhost:5432:myapp:postgres:secret
*.example.com:5432:*:admin:adminpass
```

Note: File must have permissions `600` (`chmod 600 ~/.pgpass`).

After reading the file, confirm with user before connecting.

## SSL/TLS Connections

For secure connections (especially cloud databases), use `PGSSLMODE`:

```bash
PGPASSWORD=PASSWORD PGSSLMODE=require psql -h HOST -p PORT -U USER -d DATABASE -c "QUERY"
```

SSL modes:
| Mode | Description |
|------|-------------|
| `disable` | No SSL |
| `allow` | Try non-SSL first, then SSL |
| `prefer` | Try SSL first, then non-SSL (default) |
| `require` | SSL required, no certificate verification |
| `verify-ca` | SSL required, verify server certificate |
| `verify-full` | SSL required, verify server certificate and hostname |

For cloud databases (RDS, Cloud SQL, Azure), typically use `require` or `verify-full`.

Connection string with SSL:

```
postgresql://user:password@host:port/database?sslmode=require
```

## Connection Test

Before any operation, test the connection:

```bash
PGPASSWORD=PASSWORD psql -h HOST -p PORT -U USER -d DATABASE -c "SELECT 1" 2>&1
```

Note: Password is passed via `PGPASSWORD` environment variable (set inline for single command).

## Query Execution

### Read Operations (SELECT)

```bash
PGPASSWORD=PASSWORD psql -h HOST -p PORT -U USER -d DATABASE -c "QUERY"
```

Add `LIMIT 100` to large result sets by default. Use `--csv` for CSV output.

### Write Operations (INSERT, UPDATE, DELETE)

**ALWAYS require user confirmation before executing.**

For UPDATE/DELETE, first show affected rows:

```bash
PGPASSWORD=PASSWORD psql ... -c "SELECT COUNT(*) FROM table WHERE condition"
```

Then ask: "This will affect X rows. Proceed? (yes/no)"

## Schema Exploration

### List databases

```bash
PGPASSWORD=PASSWORD psql -h HOST -p PORT -U USER -d DATABASE -c "\l"
```

### List tables

```bash
PGPASSWORD=PASSWORD psql ... -c "\dt"
```

### List tables with schema

```bash
PGPASSWORD=PASSWORD psql ... -c "\dt schema_name.*"
```

### Describe table structure

```bash
PGPASSWORD=PASSWORD psql ... -c "\d table_name"
```

### Show detailed table info (with indexes, constraints)

```bash
PGPASSWORD=PASSWORD psql ... -c "\d+ table_name"
```

### List schemas

```bash
PGPASSWORD=PASSWORD psql ... -c "\dn"
```

### Show create statement

```bash
PGPASSWORD=PASSWORD pg_dump -h HOST -p PORT -U USER -d DATABASE -t table_name --schema-only
```

### List indexes

```bash
PGPASSWORD=PASSWORD psql ... -c "\di"
```

### List functions

```bash
PGPASSWORD=PASSWORD psql ... -c "\df"
```

### List views

```bash
PGPASSWORD=PASSWORD psql ... -c "\dv"
```

### List sequences

```bash
PGPASSWORD=PASSWORD psql ... -c "\ds"
```

### List roles/users

```bash
PGPASSWORD=PASSWORD psql ... -c "\du"
```

## Safety Rules

### Destructive Operations - REQUIRE CONFIRMATION

These operations MUST show a warning and require explicit user confirmation:

| Operation              | Risk Level | Action Before Execute                     |
| ---------------------- | ---------- | ----------------------------------------- |
| `DROP TABLE/DATABASE`  | CRITICAL   | Show what will be dropped, require "yes"  |
| `TRUNCATE TABLE`       | CRITICAL   | Show row count, require "yes"             |
| `DELETE` without WHERE | CRITICAL   | Refuse or require explicit confirmation   |
| `UPDATE` without WHERE | CRITICAL   | Refuse or require explicit confirmation   |
| `DELETE` with WHERE    | HIGH       | Show affected count, require confirmation |
| `UPDATE` with WHERE    | HIGH       | Show affected count, require confirmation |
| `ALTER TABLE`          | MEDIUM     | Describe changes, require confirmation    |

### Password Security

- NEVER echo password to terminal output
- NEVER include password in error messages shown to user
- NEVER print or show the full psql command that contains passwords (including PGPASSWORD=...) to the user
- When executing psql commands, do NOT display the command itself - only show the query results
- Use `PGPASSWORD` env var (set inline for single command only)
- Do not log queries containing passwords

### Production Database Warning

If host contains these patterns, show warning:

- `prod`, `production`, `live`, `master`
- Cloud database hostnames (RDS, Cloud SQL, Azure, etc.)

## Output Formatting

### Default format (aligned tables)

```bash
PGPASSWORD=PASSWORD psql ... -c "QUERY"
```

### CSV format (for data processing)

```bash
PGPASSWORD=PASSWORD psql ... --csv -c "QUERY"
```

### Tuples only (no headers/footers)

```bash
PGPASSWORD=PASSWORD psql ... -t -c "QUERY"
```

### Export to file

```bash
PGPASSWORD=PASSWORD psql ... --csv -c "QUERY" > output.csv
```

### Expanded display (vertical format for wide tables)

```bash
PGPASSWORD=PASSWORD psql ... -x -c "QUERY"
```

## Common Tasks

| User Request           | Query/Command                                                 |
| ---------------------- | ------------------------------------------------------------- |
| "Show all tables"      | `\dt` or `\dt *.*` for all schemas                            |
| "Describe users table" | `\d users` or `\d+ users` for detailed                        |
| "Find user by email"   | `SELECT * FROM users WHERE email LIKE '%pattern%' LIMIT 100`  |
| "Count records"        | `SELECT COUNT(*) FROM table`                                  |
| "Recent records"       | `SELECT * FROM table ORDER BY created_at DESC LIMIT 10`       |
| "List schemas"         | `\dn`                                                         |
| "Show table in schema" | `\dt schema_name.table_name`                                  |
| "Current database"     | `SELECT current_database()`                                   |
| "Current user"         | `SELECT current_user`                                         |
| "List indexes"         | `\di` or `\di table_name`                                     |
| "List functions"       | `\df`                                                         |
| "List views"           | `\dv`                                                         |
| "Show table size"      | `SELECT pg_size_pretty(pg_total_relation_size('table'))`      |
| "Database size"        | `SELECT pg_size_pretty(pg_database_size(current_database()))` |
| "Active connections"   | `SELECT * FROM pg_stat_activity`                              |

## Error Handling

| Error                   | Likely Cause            | Suggestion                 |
| ----------------------- | ----------------------- | -------------------------- |
| password authentication | Wrong credentials       | Verify username/password   |
| database does not exist | Database doesn't exist  | Run `\l` to list databases |
| could not connect       | Host/port issue         | Check host and port        |
| relation does not exist | Wrong table name        | Run `\dt` to list tables   |
| permission denied       | Insufficient privileges | Check user permissions     |
| connection refused      | PostgreSQL not running  | Start PostgreSQL service   |
