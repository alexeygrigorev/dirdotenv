# dirdotenv

Like direnv, but works with both .envrc and .env files.

## Features

- ✅ Supports `.env` files with the format `KEY=value`
- ✅ Supports `.envrc` files with the format `export KEY=value`
- ✅ Works with single quotes, double quotes, or no quotes
- ✅ Supports comments (lines starting with `#`)
- ✅ Can export environment variables for your shell
- ✅ Can execute commands with loaded environment variables

## Installation

```bash
pip install -e .
```

## Usage

### Load environment variables from current directory

```bash
# Output export commands for your shell
dirdotenv

# Use with eval to load variables into your current shell
eval "$(dirdotenv)"
```

### Load environment variables from a specific directory

```bash
dirdotenv /path/to/directory
```

### Execute a command with loaded environment variables

```bash
# Run a command with the environment variables loaded
dirdotenv --exec python script.py
dirdotenv --exec node app.js
```

### Specify shell format

```bash
# For bash/zsh (default)
dirdotenv --shell bash

# For fish shell
dirdotenv --shell fish
```

## File Format Examples

### `.env` file

```env
OPENAI_API_KEY='my-key'
DATABASE_URL="postgres://localhost/mydb"
API_PORT=8080

# This is a comment
DEBUG=true
```

### `.envrc` file

```bash
export OPENAI_API_KEY='my-key'
export DATABASE_URL="postgres://localhost/mydb"
export API_PORT=8080

# This is a comment
export DEBUG=true
```

## Priority

When both `.env` and `.envrc` files exist in the same directory:
1. Variables from `.env` are loaded first
2. Variables from `.envrc` override any duplicate keys from `.env`

## License

MIT
