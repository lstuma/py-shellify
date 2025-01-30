from .execution import ExecutionResult
from ..settings import SOCKET_PREFIX
import socket
import os

class Client:
    def __init__(self, socket_name: str | None = None):
        if socket_name is None:
            socket_name = str(os.getppid())
        self.socket_path: str = f"{SOCKET_PREFIX}{socket_name}.sock"
        self.sock: socket.socket = self.create_sock()

    def create_sock(self) -> socket.socket:
        if not os.path.exists(self.socket_path):
            raise FileNotFoundError(f"Socket file {self.socket_path} does not exist.")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        return sock

    def execute(self, code: str) -> ExecutionResult:
        self.sock.connect(self.socket_path)
        self.sock.sendall(code.encode())
        data = self.sock.recv(4096)
        return ExecutionResult.from_json(data.decode())

    def close(self):
        self.sock.close()

    @classmethod
    def execute_code(cls, code: str, socket_name: str | None = None):
        client = cls(socket_name=socket_name)
        result = client.execute(code)
        result.print()
        client.close()
        return result
