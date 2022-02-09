import re
import json
import inspect
import warnings
from src.instruction_set import Instructions
from src.operations import Operations
from src.exceptions import OPCODENotFound


class Controller:
    def __init__(self) -> None:
        self.op = Operations()
        self.instruct_set = Instructions(self.op)
        self.lookup = {
            name.upper(): call
            for name, call in inspect.getmembers(self.instruct_set, inspect.ismethod)
            if "_" not in name
        }
        self._set_opcodes()
        return

    def __repr__(self):
        return self.op.inspect()

    def _set_opcodes(self):
        opcodes = None
        with open("src/opcodes.json", "r") as f:
            opcodes = json.load(f)
        print(opcodes)
        opcode_keys = list(opcodes.keys())
        print(opcode_keys)
        for key in opcode_keys:
            if callback := self.lookup.get(key, None):
                self.instruct_set._set_opcode(callback, opcodes.get(key))
                continue
            warnings.warn(f"opcode {key} not defined")
        return True

    def inspect(self):
        return self.op.inspect()

    def _parser(self, command):
        command.strip()
        if not command:
            return None, None
        command_proc = re.split(",|\ ", command)
        if "" in command_proc:
            command_proc.remove("")
        print(command_proc)
        opcode = command_proc[0]
        args = command_proc[1:]
        if f"{self.instruct_set._jump_flag}:" in opcode:
            print(f"Jump stopped {args}")
            command = command.replace(f"{self.instruct_set._jump_flag}: ", "")
            print(command)
            self.instruct_set._jump_flag = False
            return self._parser(command)
        return opcode, args

    def _call(self, command, opcode, *args, **kwargs) -> None:
        if func := self.lookup.get(opcode.upper()):
            print(args)
            self.op.opcode_fetch(func, command, *args, **kwargs)
            return func(*args, **kwargs)
        raise OPCODENotFound()

    def parse_and_call(self, command):
        if command[0] == "#":  # Directive
            command = command[1:]
        opcode, args = self._parser(command)
        print(opcode)
        if not opcode:
            raise OPCODENotFound()
        if not self.instruct_set._jump_flag:
            return self._call(command, opcode, *args)
        else:
            print(f"Jump encountered {self.instruct_set._jump_flag}")

    pass
