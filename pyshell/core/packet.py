from typing import Union
import json

class Packet:
    def __init__(self, action: str, data: dict):
        self.action: str = action
        self.data: dict = data

    def __repr__(self) -> str:
        return self.json()

    def json(self) -> str:
        return json.dumps({
            "action": self.action,
            "data": self.data
        })

    @classmethod
    def from_json(cls, json_str: str) -> Union["Packet", type["Packet"]]:
        data = json.loads(json_str)
        match data["action"]:
            case "exec":
                return ExecPacket(**data)
            case "output":
                return OutputPacket(**data)
            case "error":
                return ErrorPacket(**data)
            case "input":
                return InputPacket(**data)
            case "ack":
                return AckPacket(**data)
            case "close":
                return ClosePacket(**data)
            case _:
                raise ValueError(f"Invalid action: {data['action']}")

class ExecPacket(Packet):
    def __init__(self, code: str):
        super().__init__("exec", {"code": code})
        self.code = code

class OutputPacket(Packet):
    def __init__(self, stdout: str, stderr: str):
        super().__init__("output", {"stdout": stdout, "stderr": stderr})
        self.stdout = stdout
        self.stderr = stderr

class InputPacket(Packet):
    def __init__(self, stdin: str):
        super().__init__("input", {"stdin": stdin})
        self.stdin = stdin

class ErrorPacket(Packet):
    def __init__(self, exception: str):
        exception = f"PROTOCOL ERROR [USUALLY CRITICAL]: {exception}"
        super().__init__("error", {"exception": exception})
        self.exception = exception

class AckPacket(Packet):
    def __init__(self):
        super().__init__("ack", {})

class ClosePacket(Packet):
    def __init__(self):
        super().__init__("close", {})
