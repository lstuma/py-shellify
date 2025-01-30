from .packet import Packet, AckPacket, ErrorPacket, OutputPacket, ExecPacket, InputPacket, ClosePacket
from .protocol import PyshSocket
from .execution import Executor
from psutil import Process
from typing import Any
import asyncio
from time import sleep
import rich
import os

class Handler:
    def __init__(self, owner_pid: int):
        self.owner: Process = Process(owner_pid)
        self.sock_name = str(owner_pid)

        self.sock: PyshSocket = PyshSocket(self.sock_name, listen=True)
        self.executor: Executor = Executor()

    async def execute(self, code: str) -> None:
        """
        Executes the given code while communicating with the client.
        """
        # start code execution
        asyncio.create_task(self.executor.execute(code))
        while not self.executor.done:
            # send output to client
            stdout, stderr = self.executor._stdout.getvalue(), self.executor._stderr.getvalue()
            self.sock.send(OutputPacket(stdout, stderr))
            self.sock.await_ack()
            # receive data from client
            packet = self.sock.recv()
            if not packet:
                continue
            match(packet.action):
                case "input":
                    self.executor._input_queue.put_nowait(packet.stdin)
                    self.sock.send_ack()
                case "close":
                    self.sock.disconnect()
                    return
                case _:
                    packet = ErrorPacket(f"only input or close allowed: received {packet.action}")
                    self.sock.send(packet)
                    self.sock.disconnect()

    def run(self):
        while self.owner.is_running():
            if not self.sock.connected:
                self.sock.accept()
            else:
                try:
                    packet = self.sock.recv()
                    if not packet:
                        continue
                    match(packet.action):
                        case "exec":
                            asyncio.run(self.execute(packet.code))
                        case "close":
                            self.sock.disconnect()
                        case _:
                            packet = ErrorPacket(f"only execs allowed: received {packet.action}")
                            self.sock.send_ack()
                    self.sock.disconnect()
                except Exception as e:
                    rich.print(f"[bold red]\\[Handler]Error:[/] {str(e)}")
                    self.sock.disconnect()
        self.sock.close()

    @classmethod
    def fork(cls, owner_pid: int | None = None) -> None:
        """
        Creates a new handler process and runs it.

        :param owner_pid: The process id of the owner process. Defaults to the current parent process.
        """
        owner_pid = owner_pid or os.getppid()
        new_pid = os.fork()
        if new_pid == 0:
            # run handler in child process
            handler = cls(owner_pid)
            handler.run()
            exit(0)
        # wait for new process to start
        sleep(0.1)
