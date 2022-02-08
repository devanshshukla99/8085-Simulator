from src.memory import Memory, Registers, Byte, Flags

class Operations:
    def __init__(self) -> None:
        self.memory = Memory(4096, "0x0000")
        self.registers = Registers()
        self.flags = Flags()

        self._registers_list = {
            "A": self.registers.A,
            "PSW": self.registers.PSW,
            "B": self.registers.B,
            "C": self.registers.C,
            "D": self.registers.D,
            "E": self.registers.E,
            "H": self.registers.H,
            "L": self.registers.L,
            "S": self.registers.S,
            "P": self.registers.P,
            "PC": self.registers.PC,
        }
        pass

    def inspect(self):
        return "\n\n".join([self.registers.inspect(), self.flags.inspect(), str(self.memory)])

    def _parse_addr(self, addr):
        print(f"_parse_addr {self._registers_list.get(addr, None)}")
        return self._registers_list.get(addr, None)

    def opcode_fetch(self, opcode) -> None:
        print(f"opcode fetch -- {opcode}")
        pass

    def memory_read(self, addr) -> Byte:
        print(f"memory read {addr}")
        if _parsed_addr := self._parse_addr(addr):
            return _parsed_addr.read()
        return self.memory.get(addr)

    def memory_write(self, addr, data) -> bool:
        print(f"memory write {addr}|{data}")
        if _parsed_addr := self._parse_addr(addr):
            return _parsed_addr.write(data)
        self.memory[addr] = data
        return True

    pass
