from .execution import ExecutionResult, ExecutionScope
from .settings import SOCKET_PREFIX
from psutil import Process
import socket
import sys
import os
from io import StringIO
from json import loads

class Handler:
    def __init__(self, owner_pid: int, socket_name: str | None = None):
        self.owner_pid: int = owner_pid
        self.owner: Process = Process(owner_pid)

        if socket_name is None:
            socket_name = str(owner_pid)
        self.socket_path: str = f"{SOCKET_PREFIX}{socket_name}.sock"
        self.sock: socket.socket = self.create_sock()

        self.scope = ExecutionScope()

    def create_sock(self) -> socket.socket:
        if os.path.exists(self.socket_path):
            raise FileExistsError(f"Socket file {self.socket_path} already exists.")
        if not os.path.exists(os.path.dirname(self.socket_path)):
            os.makedirs(os.path.dirname(self.socket_path))
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.socket_path)
        return sock

    def execute(self, code: str) -> ExecutionResult:
        """
        Executes the given code and returns the result.
        """
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        new_stdout = StringIO()
        new_stderr = StringIO()
        exceptions = None
        try:
            sys.stdout = new_stdout
            sys.stderr = new_stderr
            exec(code, self.scope._globals, self.scope._locals)
        except Exception as e:
            exceptions = str(e)
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        return ExecutionResult(new_stdout.getvalue(), new_stderr.getvalue(), exceptions)

    def run(self):
        self.sock.listen()
        self.sock.setblocking(False)
        client_sock = None
        while self.owner.is_running():
            if not client_sock:
                try:
                    client_sock, client_address = self.sock.accept()
                except BlockingIOError:
                    pass
            else:
                try:
                    data = client_sock.recv(4096)
                    if data:
                        result = self.execute(data.decode())
                        client_sock.send(result.json().encode())
                        client_sock.close()
                        client_sock = None
                except BlockingIOError:
                    pass
                except Exception as e:
                    print("[Handler] Error:", e)
                    client_sock.close()
                    client_sock = None
        self.sock.close()
        os.remove(self.socket_path)

    @classmethod
    def fork(cls, owner_pid: int | None = None, socket_name: str | None = None) -> None:
        """
        Creates a new handler process and runs it.

        :param owner_pid: The process id of the owner process. Defaults to the current parent process.
        """
        owner_pid = owner_pid or os.getppid()
        new_pid = os.fork()
        if new_pid == 0:
            # run handler in child process
            handler = cls(owner_pid, socket_name)
            handler.run()
            sys.exit(0)
