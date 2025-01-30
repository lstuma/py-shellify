from .protocol import PyshSocket
from .handler import Handler
from .packet import Packet, ExecPacket, OutputPacket, ClosePacket, ErrorPacket, AckPacket, InputPacket
import rich
import asyncio
import sys
import socket
import os

class Client:
    def __init__(self):
        self.owner_pid = os.getppid()
        Client.ensure_handler(self.owner_pid)
        self.sock: PyshSocket = PyshSocket(str(self.owner_pid))

    async def execute(self, code: str) -> None:
        """
        Execute the given code on the server and handle stdin/stdout/stderr.
        """
        self.sock.connect()
        if not self.sock.connected:
            raise ConnectionError("Could not connect to server.")

        exec_packet = ExecPacket(code)
        self.sock.send(exec_packet)
        self.sock.await_ack()

        loop = asyncio.get_event_loop()
        loop.create_task(self._read_output())
        loop.create_task(self._send_input())

    async def _read_output(self):
        """
        Continously read output from the server and print it to the console.
        """
        while True:
            packet = self.sock.recv()
            if not packet:
                continue
            if isinstance(packet, OutputPacket):
                print(packet.stdout, end="", file=sys.stdout)
                print(packet.stderr, end="", file=sys.stderr)
            elif isinstance(packet, ErrorPacket):
                rich.print(f"[bold red]{packet.exception}[/]")
            elif isinstance(packet, ClosePacket):
                self.sock.disconnect()
            else:
                print(f"Invalid packet received from server: {repr(packet)}")

    async def _send_input(self):
        """
        Continously read input from the console and send it to the server.
        """
        while True:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input)
            input_packet = InputPacket(user_input)
            self.sock.send(input_packet)
            self.sock.await_ack()



    @staticmethod
    def ensure_handler(owner_pid: int | None = None) -> None:
        owner_pid = owner_pid or os.getppid()
        socket_path = PyshSocket.path_from_name(str(owner_pid))
        if socket_path.exists():
            return
        # start a new handler
        Handler.fork(owner_pid)

    def close(self):
        self.sock.disconnect()

    @classmethod
    def execute_code(cls, code: str):
        client = cls()
        asyncio.run(client.execute(code))
        client.close()
