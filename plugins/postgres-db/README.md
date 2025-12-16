# postgres-db

A Claude Code plugin for accessing PostgreSQL databases via CLI.

## Features

- Query execution (SELECT, INSERT, UPDATE, DELETE)
- Schema exploration (list databases, tables, schemas, describe tables)
- Credential management from user input or config files (.env, docker-compose.yml)
- Safety confirmations for destructive operations
- Production database warnings
- Credential protection (passwords never shown in output)

## Installation

```bash
claude plugin install postgres-db@ekstend
```

## Prerequisites

PostgreSQL CLI client must be installed on your system:

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
apt install postgresql-client

# Check installation
psql --version
```

## Usage

Simply ask Claude to work with your PostgreSQL database:

- "Connect to my PostgreSQL database"
- "Show all tables in the database"
- "Find users with email containing gmail"
- "Update the status of order #123"

Claude will ask for credentials or a config file path before connecting.

## Safety

- Destructive operations (DROP, DELETE, UPDATE, TRUNCATE) require confirmation
- Password is never echoed to terminal or logged
- Production databases trigger warnings
