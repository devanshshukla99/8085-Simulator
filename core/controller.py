import re
import inspect

from rich.console import Console

from core.exceptions import OPCODENotFound
from core.instruction_set import Instructions
from core.operations import Operations


class Controller:
    def __init__(self, console=None) -> None:
        self.console = console
        if not console:
            self.console = Console()
        # operations
        self.op = Operations()
        # instruction set
        self._jump_flag = False
        self._address_jump_flag = None
        self.instruct_set = Instructions(self.op)
        self.lookup = {
            name.upper(): call
            for name, call in inspect.getmembers(self.instruct_set, inspect.ismethod)
            if "_" not in name
        }
        # callstack
        self._callstack = []
        self.ready = False
        return

    def __repr__(self):
        return f"{self.op.inspect()}\n{self.__callstackrepr__()}"

    def __callstackrepr__(self) -> str:
        return f"<CallStack calls={len(self._callstack)}>"

    def _call(self, func, *args, **kwargs) -> bool:
        return func(*args)

    def inspect(self):
        return self.console.print(self.__repr__())

    def _lookup_opcode_func(self, opcode):
        func = self.lookup.get(opcode)
        if func:
            return func
        raise OPCODENotFound

    @property
    def callstack(self) -> list:
        return self._callstack

    def _addjob(self, func, args: tuple = (), **kwargs) -> bool:
        self._callstack.append((func, args, kwargs))
        return True

    def _parser(self, command):
        command = command.strip()
        if not command:
            return None, None
        if command[0] == "#":  # Directive
            command = command[1:]
        _proc_command = re.split(r",| ", command)
        for _ in range(_proc_command.count("")):
            _proc_command.remove("")
        opcode = _proc_command[0]
        args = _proc_command[1:]
        print(opcode, args)
        return opcode.upper(), args

    def parse(self, command):
        _jnc_flip = False
        opcode, args = self._parser(command)
        if self._jump_flag:
            if opcode == self._jump_flag:
                self._jump_flag = False
                _jnc_flip = True
                _current_pc = str(self.op.super_memory.PC)
                self.op.memory_write(self._address_jump_flag[0], "0x" + _current_pc[4:])
                self.op.memory_write(self._address_jump_flag[1], _current_pc[0:4])
                opcode, args = self._parser(" ".join(args))

        opcode_func = self._lookup_opcode_func(opcode)
        self.op.prepare_operation(opcode, *args)
        self._addjob(opcode_func, args, jnc_flip=_jnc_flip)

        if opcode == "JNC":
            self._jump_flag = (args[0] + ":").upper()
            self._address_jump_flag = [str(self.op.super_memory.PC), str(self.op.super_memory.PC + 1)]
            print(self._address_jump_flag)
            self.op._update_pc("0xff")
            self.op._update_pc("0xff")

        self.ready = True
        return True

    def parse_all(self, commands):
        for command in commands.split("\n"):
            if command:
                self.parse(command)
        return True

    def run_once(self):
        if not self._callstack:
            return False
        try:
            func, args, kwargs = self._callstack.pop(0)
            jnc_flip = kwargs.pop("jnc_flip", False)
            if not jnc_flip:
                if self.instruct_set._jump_flag:
                    print("JUMP ENCOUNTERED")
                    return
            self._call(func, *args, **kwargs)
        except StopIteration:
            pass
        return True

    def run(self):
        for idx, val in enumerate(self._callstack):
            try:
                print(f"{idx} -- {val} ", end="")
                func, args, kwargs = val
                jnc_flip = kwargs.pop("jnc_flip", False)
                if not jnc_flip:
                    if self.instruct_set._jump_flag:
                        print("JUMP ENCOUNTERED")
                        continue
                self._call(func, *args, **kwargs)
            except StopIteration:
                pass
        return True

    def set_flags(self, *args, **kwargs):
        return self.op.flags.set_flags(*args, **kwargs)

    def reset(self) -> None:
        return self.__init__(console=self.console)

    def reset_callstack(self) -> None:
        self._callstack = []
        return True

    pass
