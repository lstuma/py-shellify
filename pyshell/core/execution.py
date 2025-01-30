import time
import asyncio
from typing import Any
import contextlib as ctxlib
from io import StringIO

"""
Scope class for storing execution scope.
"""
class Scope:
    def __init__(self):
        self._data = {"globals": {}, "locals": {}}
    def __getitem__(self, key):
        return self._data[key]
    def keys(self):
        return self._data.keys()
    def __iter__(self):
        return iter(self._data)
    def exec(self, code: str) -> Any:
        return exec(code, **self)

"""
Executor class for execution python code and retrieving output in real time
as well as inserting input any time during execution.
"""
class Executor:
    def __init__(self):
        self.scope = Scope()
        self.running = False

        self._stdout = StringIO()
        self._stderr = StringIO()

        self._input_queue = asyncio.Queue()

    async def execute(self, code: str) -> None:
        """
        Runs the given code and returns the output.
        """
        self.running = True
        # redirect stdout and stderr
        with ctxlib.redirect_stdout(self._stdout), ctxlib.redirect_stderr(self._stderr):
            self.scope._data["globals"]["input"] = self._input_queue.get_nowait
            # run the code
            self.scope.exec(code)
        self.running = False

    @property
    def done(self) -> bool:
        return self.running == False

    @staticmethod
    def __get_new_output(stream: StringIO) -> str:
        """
        Get any new output from the given stream.
        """
        output = stream.getvalue()
        stream.seek(0)
        stream.truncate()
        return output

    def read_stdout(self) -> str:
        """
        Get any new output from the currently running code.
        """
        return Executor.__get_new_output(self.stdout)

    def read_stderr(self) -> str:
        """
        Get any new error output from the currently running code.
        """
        return Executor.__get_new_output(self.stderr)

    def read_output(self) -> tuple[str, str]:
        """
        Get any new output and error output from the currently running code.
        """
        return self.read_stdout(), self.read_stderr()

    def insert_input(self, input: str) -> None:
        """
        Insert input into the currently running code.
        """
        self._input_queue.put_nowait(input)
