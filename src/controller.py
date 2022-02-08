import re
from src.instruction_set import Instructions
from src.operations import Operations
from src.exceptions import OPCODENotFound


class Controller:
    def __init__(self) -> None:
        self.op = Operations()
        self.instruct_set = Instructions(self.op)
        self.lookup = {
            "MVI": self.instruct_set.mvi,
            "LXI": self.instruct_set.lxi,
            "ADD": self.instruct_set.add,
        }

    def __repr__(self):
        return self.op.inspect()

    def inspect(self):
        return self.op.inspect()

    def _parser(self, command):
        command.strip()
        if not command:
            return None, None
        command = re.split(", |\ ", command)
        opcode = command[0]
        args = command[1:]
        return opcode, args

    def _call(self, opcode, *args, **kwargs) -> None:
        if func := self.lookup.get(opcode.upper()):
            print(args)
            self.op.opcode_fetch(opcode)
            return func(*args, **kwargs)
        raise OPCODENotFound()

    def parse_and_call(self, command):
        opcode, args = self._parser(command)
        print(opcode)
        if not opcode:
            raise OPCODENotFound()
        self._call(opcode, *args)

    pass
