# py-shellify (pysh)
Improved shell scripting using Python!

# Usage
```bash
# Run a Python command
pysh "print('Hello, World!')"
```

# How It Works
pysh connects to a handler process that runs the
Python code you write in your shell scripts.
Every handler process has an owner process which it is bound to.
Once this owner process dies, the handler process dies as well.

When running a command using pysh, the command is sent to the handler process
which then runs the command and sends the output back to the shell.
If no handler process is running, pysh will start a new handler process.
