import os
from json import dumps, loads

class ExecutionScope:
    def __init__(self):
        self._globals = {}
        self._locals = {}

    def __repr__(self):
        return f"ExecutionScope(globals={self._globals}, locals={self._locals})"

class ExecutionResult:
    def __init__(self, stdout: str, stderr: str, exceptions: str | None = None):
        self.stdout: str = stdout
        self.stderr: str = stderr
        self.exceptions: str = exceptions or ""

    def json(self) -> str:
        return dumps({
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exceptions": self.exceptions
        })

    def print(self) -> None:
        print("stdout:", self.stdout)
        print("stderr:", self.stderr)
        print("exceptions:", self.exceptions)

    @staticmethod
    def from_json(json: str) -> "ExecutionResult":
        print("json:", json)
        data = loads(json)
        return ExecutionResult(data["stdout"], data["stderr"], data["exceptions"])
