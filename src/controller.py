import re
import inspect
from src.instruction_set import Instructions
from src.operations import Operations
from src.exceptions import OPCODENotFound


class Controller:
    def __init__(self) -> None:
        self.op = Operations()
        self.instruct_set = Instructions(self.op)
        # self.lookup = {
        #     "MVI": self.instruct_set.mvi,
        #     "LXI": self.instruct_set.lxi,
        #     "ADD": self.instruct_set.add,
        # }
        self.lookup = {
            name.upper(): call
            for name, call in inspect.getmembers(self.instruct_set, inspect.ismethod)
            if "_" not in name
        }

    def __repr__(self):
        return self.op.inspect()

    def inspect(self):
        return self.op.inspect()

    def _parser(self, command):
        command.strip()
        if not command:
            return None, None
        command_proc = re.split(",|\ ", command)
        opcode = command_proc[0]
        args = command_proc[1:]
        if "" in args:
            args.remove("")
        if f"{self.instruct_set._jump_flag}:" in opcode:
            print(f"Jump stopped {args}")
            command = command.replace(f"{self.instruct_set._jump_flag}: ", "")
            print(command)
            self.instruct_set._jump_flag = False
            return self._parser(command)
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
        if not self.instruct_set._jump_flag:
            return self._call(opcode, *args)
        else:
            print(f"Jump encountered {self.instruct_set._jump_flag}")

    pass
