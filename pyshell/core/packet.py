from typing import Union
import json

class Packet:
    def __init__(self, action: str, data: dict):
        self.action: str = action
        self.data: dict = data

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
            case "input_request":
                return InputRequestPacket(**data)
            case "input_response":
                return InputResponsePacket(**data)
            case "ack":
                return AckPacket(**data)
            case _:
                raise ValueError(f"Invalid action: {data['action']}")

class ExecPacket(Packet):
    def __init__(self, code: str):
        super().__init__("exec", {"code": code})

class OutputPacket(Packet):
    def __init__(self, stdout: str, stderr: str):
        super().__init__("output", {"stdout": stdout, "stderr": stderr})

class InputRequestPacket(Packet):
    def __init__(self, prompt: str):
        super().__init__("input_request", {})

class InputResponsePacket(Packet):
    def __init__(self, response: str):
        super().__init__("input_response", {"response": response})

class ErrorPacket(Packet):
    def __init__(self, exception: Exception):
        super().__init__("error", {"exception": str(exception)})

class AckPacket(Packet):
    def __init__(self):
        super().__init__("ack", {})
