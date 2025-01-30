import re
from ..settings import SOCKET_DIR
from .packet import Packet, ExecPacket, OutputPacket, ErrorPacket, AckPacket, InputPacket, ClosePacket
from typing import Union
from pathlib import Path
import asyncio
from asyncio import StreamReader, StreamWriter, IncompleteReadError
import socket

"""
Non-blocking socket class for asyncio.
"""
class AsyncioSocket:
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader = reader
        self.writer = writer
    def close(self) -> None:
        self.writer.close()
    async def sendall(self, data: bytes) -> None:
        self.writer.write(data)
        await self.writer.drain()
    async def recv(self, buffsize: int = 4096) -> bytes | None:
        try:
            return await self.reader.read(buffsize)
        except IncompleteReadError:
            pass
    @classmethod
    async def connect(cls, sock_path: Path) -> "AsyncioSocket":
        reader, writer = await asyncio.open_unix_connection(str(sock_path))
        return cls(reader, writer)
    @classmethod
    async def accept(cls, sock_path: Path) -> "AsyncioSocket":
        reader, writer = await asyncio.open_unix_server()
        return cls(reader, writer)

class PyshSocket:
    def __init__(self, sock_name: str, listen=False) -> None:
        self.sock_name = sock_name
        self.sock_path: Path = PyshSocket.path_from_name(sock_name)
        self._listen = listen
        self.sock = self.create_sock(listen)
        self._other_sock: socket.socket | None = None

    @staticmethod
    def path_from_name(sock_name: str) -> Path:
        return SOCKET_DIR / f"pysh-{sock_name}.sock"

    def create_sock(self, listen: bool) -> socket.socket:
        sock: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if listen:
            # ensure directory exists
            if not SOCKET_DIR.exists():
                SOCKET_DIR.mkdir()
            # remove existing socket file
            if self.sock_path.exists():
                self.sock_path.unlink()
            sock.bind(str(self.sock_path))
            sock.listen(1)
        sock.setblocking(False)
        return sock

    @property
    def connected(self) -> bool:
        sock = self.sock if not self._listen else self._other_sock
        if sock is None:
            return False
        try:
            # Check if the socket file descriptor is valid
            sock.getpeername()
        except socket.error:
            return False
        return sock.fileno() != -1

    def accept(self) -> bool:
        if not self._listen:
            raise AttributeError("Cannot accept on a non-listening socket.")
        try:
            self._other_sock, _ = self.sock.accept()
            print("handler connect", self.connected)
            return True
        except BlockingIOError:
            pass
        return False

    def connect(self) -> None:
        if self._listen:
            raise AttributeError("Cannot connect on a listening socket.")
        if not self.sock_path.exists():
            raise FileNotFoundError(f"Socket file {self.sock_path} does not exist.")
        self.sock.connect(str(self.sock_path))
        print("client connect", self.connected)

    def disconnect(self) -> None:
        try:
            self.send(ClosePacket())
        except Exception:
            pass
        if self._other_sock is not None:
            self._other_sock.close()
            self._other_sock = None

    def send(self, packet: Packet) -> None:
        self.sock.sendall(packet.json().encode())

    def send_ack(self) -> None:
        """
        Send an AckPacket.
        """
        self.send(AckPacket())

    def await_ack(self) -> None:
        """
        Wait for an AckPacket.
        """
        while True:
            packet = self.recv()
            if isinstance(packet, AckPacket):
                return

    def recv(self) -> Union[Packet, type[Packet], None]:
        if not self.connected:
            raise ConnectionError("Socket is not connected.")
        try:
            data: bytes = self.sock.recv(1024)
        except BlockingIOError:
            return

        if data:
            return Packet.from_json(data.decode())
        return

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass
        if self._listen:
            self.sock_path.unlink()
