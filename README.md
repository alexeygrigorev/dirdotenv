# dirdotenv

Like direnv, but works with both .envrc and .env files.

## Features

- ✅ Supports `.env` files with the format `KEY=value`
- ✅ Supports `.envrc` files with the format `export KEY=value`
- ✅ Works with single quotes, double quotes, or no quotes
- ✅ Supports comments (lines starting with `#`)
- ✅ Can export environment variables for your shell
- ✅ Can execute commands with loaded environment variables
- ✅ Shell integration for automatic loading (like direnv)
- ✅ Works with uvx for quick execution without installation
- ✅ Supports Bash, Zsh, Fish, and PowerShell

## Installation

### Using pip

```bash
pip install -e .
```

### Using uvx (recommended for quick testing)

```bash
# Run without installation
uvx dirdotenv

# Or with a specific directory
uvx dirdotenv /path/to/project
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

# For PowerShell
dirdotenv --shell powershell
```

## Shell Integration (Automatic Loading)

For automatic loading of environment variables when you enter a directory (like direnv), use the `hook` command:

### Bash

Add to your `~/.bashrc`:

```bash
eval "$(dirdotenv hook bash)"
```

### Zsh

Add to your `~/.zshrc`:

```zsh
eval "$(dirdotenv hook zsh)"
```

### Fish

Add to your `~/.config/fish/config.fish`:

```fish
dirdotenv hook fish | source
```

### PowerShell

Add to your PowerShell profile (run `notepad $PROFILE`):

```powershell
Invoke-Expression (dirdotenv hook powershell)
```

### How Shell Integration Works

Once configured, the shell integration provides direnv-like behavior:

1. **Entering a directory**: When you `cd` into a directory with `.env` or `.envrc` files, the variables are automatically loaded and the key names are displayed
   ```
   $ cd myproject
   dirdotenv: loaded API_KEY DATABASE_URL PORT
   ```

2. **Subdirectory inheritance**: Child directories inherit variables from parent directories but can override them
   ```
   myproject/
     .env          # API_KEY=parent_value
     backend/
       .env        # API_KEY=child_value, DB_HOST=localhost
   
   $ cd myproject
   dirdotenv: loaded API_KEY
   
   $ cd backend
   dirdotenv: loaded API_KEY DB_HOST  # API_KEY is overridden, DB_HOST is new
   ```

3. **Leaving a directory**: When you leave a directory tree, variables that were set are automatically unloaded
   ```
   $ cd ..  # leaving myproject tree
   dirdotenv: unloaded API_KEY DATABASE_URL PORT
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
1. Variables from `.envrc` are loaded first
2. Variables from `.env` override any duplicate keys from `.envrc`

## License

MIT
