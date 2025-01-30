from .settings import SOCKET_PREFIX
from .execution import ExecutionResult
from .handler import Handler
from .client import Client
import time
import os

def ensure_handler(self, socket_name: str | None = None) -> None:
    """
    Ensure that a handler is running.
    """
    if socket_name is None:
        socket_name = str(os.getppid())
    socket_path = f"{SOCKET_PREFIX}{socket_name}.sock"
    if os.path.exists(socket_path):
        print("Handler already running.")
        return

    # start a new handler
    Handler.fork(socket_name=socket_name)
    time.sleep(0.1)

def execute(code: str) -> ExecutionResult:
    # ensure handler is running
    owner_pid = os.getppid()
    socket_name = str(owner_pid)
    ensure_handler(socket_name)
    # execute code and return result
    return Client.execute_code(code, socket_name=socket_name)
