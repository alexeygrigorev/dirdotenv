#!/usr/bin/env python3
"""Demo script that reads environment variables loaded by dirdotenv."""

import os


def main():
    """Display environment variables that should be loaded by dirdotenv."""
    print("=== Environment Variables Demo ===\n")
    
    env_vars = [
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "API_PORT",
        "DEBUG",
        "REDIS_HOST",
        "REDIS_PORT",
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var:
                display_value = value[:5] + "..." if len(value) > 5 else "***"
            else:
                display_value = value
            print(f"{var}: {display_value}")
        else:
            print(f"{var}: (not set)")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
