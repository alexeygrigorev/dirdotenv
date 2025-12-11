# dirdotenv

Like direnv, but works with both .envrc and .env files.

## Features

- ✅ Supports `.env` files with the format `KEY=value`
- ✅ Supports `.envrc` files with the format `export KEY=value`
- ✅ Shell integration with bash, zsh, fish and pwsh
- ✅ Use `uvx dirdotenv` to run it without installation or install easily with `uv tool install dirdotenv`
- ✅ Cross-platform, written in Python 

## Installation

### Using uv

```bash
uv tool install dirdotenv
```

Now it's available as `dirdotenv` command.

Then update your `.bashrc` or equivalent:

```bash
eval "$(dirdotenv hook bash)"
```

See [Shell Integration](#shell-integration) for other shells

### Using uvx

Run without installation

```bash
eval "$(uvx dirdotenv hook bash)"
```

### Using pip

```bash
pip install dirdotenv
```

### Development

When developing:

```bash
git clone git@github.com:alexeygrigorev/dirdotenv.git
cd dirdotenv
uv sync

# assuming you cloned to ~/git/dirdotenv/
alias dirdotenv="uv run --project ~/git/dirdotenv/ python -m dirdotenv"
eval "$(dirdotenv hook bash)"
```

## Shell Integration

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
Invoke-Expression ((dirdotenv hook powershell) -join "`n")
```

### How Shell Integration Works

Once configured, the shell integration provides direnv-like behavior:

1. **Entering a directory**: When you `cd` into a directory with `.env` or `.envrc` files, the variables are automatically loaded and displayed with a `+` prefix
   ```
   $ cd myproject
   dirdotenv: +API_KEY +DATABASE_URL +PORT
   ```

2. **Subdirectory inheritance**: Child directories inherit variables from parent directories but can override them
   ```
   myproject/
     .env          # API_KEY=parent_value
     backend/
       .env        # API_KEY=child_value, DB_HOST=localhost
   
   $ cd myproject
   dirdotenv: +API_KEY
   
   $ cd backend
   dirdotenv: +API_KEY +DB_HOST  # API_KEY is overridden, DB_HOST is new
   ```

3. **Leaving a directory**: When you leave a directory tree, variables that were set are automatically unloaded and displayed with a `-` prefix
   ```
   $ cd ..  # leaving myproject tree
   dirdotenv: -API_KEY -DATABASE_URL -PORT
   ``` 

## Advanced usage

### Show help

```bash
# Display usage information
dirdotenv
dirdotenv --help
```

### Load environment variables from current directory

Note: this is not recommended to use directly - use hooks instead.


```bash
# Output export commands for your shell (use --export to prevent accidental exposure)
eval "$(dirdotenv --export)"
```

### Load environment variables from a specific directory

```bash
eval "$(dirdotenv /path/to/directory --export)"
```

### Specify shell format

```bash
# For bash/zsh (default)
eval "$(dirdotenv --export --shell bash)"

# For fish shell
dirdotenv --export --shell fish | source

# For PowerShell
Invoke-Expression ((dirdotenv --export --shell powershell) -join "`n")
```

### Execute a command with loaded environment variables

```bash
# Run a command with the environment variables loaded
dirdotenv --exec python script.py
dirdotenv --exec node app.js
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
