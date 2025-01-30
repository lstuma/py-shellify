from ..settings import SOCKET_DIR
from .packet import Packet, ExecPacket, OutputPacket, ErrorPacket, AckPacket, InputRequestPacket, InputResponsePacket
from typing import Union
from pathlib import Path
import socket

class PyshSocket:
    def __init__(self, sock_name: str, listen=False) -> None:
        self.sock_name = sock_name
        self.sock_path: Path = SOCKET_DIR / f"pysh-{sock_name}.sock"
        self._listen = listen
        self.sock = self.create_sock(listen)

    def create_sock(self, listen: bool) -> socket.socket:
        if listen:
            # ensure directory exists
            if not SOCKET_DIR.exists():
                SOCKET_DIR.mkdir()
            # remove existing socket file
            if self.sock_path.exists():
                self.sock_path.unlink()
            # create socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(str(self.sock_path))
            sock.setblocking(False)
            sock.listen(1)
            return sock
        else:
            if not self.sock_path.exists():
                raise FileNotFoundError(f"Socket file {self.sock_path} does not exist.")
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            return sock

    def accept(self) -> socket.socket | None:
        if not self._listen:
            raise AttributeError("Cannot accept on a non-listening socket.")
        try:
            client_sock, _ = self.sock.accept()
            return client_sock
        except BlockingIOError:
            pass

    def connect(self) -> None:
        if self._listen:
            raise AttributeError("Cannot connect on a listening socket.")
        self.sock.connect(str(self.sock_path))

    def send(self, packet: Packet) -> None:
        self.sock.sendall(packet.json().encode())

    def recv(self) -> Union[Packet, type[Packet], None]:
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            return

        if data:
            return Packet.from_json(data.decode())
        return

    def close(self) -> None:
        self.sock.close()
        if self._listen:
            self.sock_path.unlink()
