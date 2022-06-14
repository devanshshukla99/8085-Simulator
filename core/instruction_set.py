import warnings
from core.flags import flags
from core.util import decompose_byte, twos_complement


class Instructions:
    def __init__(self, op) -> None:
        self.op = op
        self._jump_flag = False
        self._base = 16
        pass

    def _is_jump_opcode(self, opcode) -> bool:
        opcode = opcode.upper()
        if opcode not in ["JNC", "JC", "JZ", "JNZ"]:  # add more later
            return False
        return True

    def _next_addr(self, addr) -> str:
        return format(int(str(addr), 16) + 1, "#06x")

    def _check_carry(self, data_1, data_2, og2, add=True, _AC=True, _CY=True) -> None:
        """
        Method to check both `CY` and `AC` flags.

        `aux_data` are the LSB of the two data to be added
        For example: for `0x11` and `0xae`, `aux_data=["0x1", "0xe"]`
        """
        decomposed_data_1 = decompose_byte(data_1, nibble=True)
        decomposed_data_2 = decompose_byte(data_2, nibble=True)
        carry_data, aux_data = list(zip(decomposed_data_1, decomposed_data_2))

        if _AC:
            flags.AC = False
            if (int(aux_data[0], 16) + int(aux_data[1], 16)) >= 16:
                print("AUX FLAG")
                flags.AC = True

        if not _CY:
            return

        if not add:
            flags.C = False
            if int(str(data_1), 16) < int(str(og2), 16):
                print("CARRY FLAG-")
                flags.CY = True
        return

    def _check_parity(self, data_bin: str) -> None:
        flags.P = False
        _count_1s = data_bin.count("1")
        if not _count_1s % 2:
            flags.P = True
            print("PARITY")
        return

    def _check_sign(self, data_bin: str) -> None:
        flags.S = False
        if int(data_bin[0]):
            flags.S = True
            print("SIGN")
        return

    def _check_zero(self, result: str) -> None:
        flags.Z = False
        if int(result, 2) == 0:
            flags.Z = True
            print("ZERO")
        return

    def _check_flags(self, data_bin, _P=True, _S=True, _Z=True) -> bool:
        if _P:
            self._check_parity(data_bin)
        if _S:
            self._check_sign(data_bin)
        if _Z:
            self._check_zero(data_bin)
        return True

    def _check_flags_and_compute(self, data_1, data_2, add=True, _AC=True, _CY=True, _P=True, _S=True, _Z=True):
        og2 = data_2
        if not add:
            data_2 = twos_complement(str(data_2))

        result = int(str(data_1), 16) + int(str(data_2), 16)
        if result > 255:
            if _CY:
                flags.CY = True
                print("CARRY FLAG+")
            result -= 256
        result_hex = format(result, "#04x")
        data_bin = format(result, "08b")

        self._check_carry(data_1, data_2, og2, add=add, _AC=_AC, _CY=_CY)
        self._check_flags(data_bin, _P=_P, _S=_S, _Z=_Z)
        return result_hex

    def mvi(self, addr: str, data: str) -> bool:
        """
        MoVe Immediate

        Store the immediate `data` into `addr`

        Parameters
        ----------
        addr : `str`
            Address
        data : `str`
            Data
        """
        self.op.memory_write(addr, data)
        return True

    def mov(self, to_addr: str, from_addr: str) -> bool:
        """
        MOVe data `from_addr` to `to_addr`

        Parameters
        ----------
        to_addr : `str`
            To address
        from_addr : `str`
            From address
        """
        data = self.op.memory_read(from_addr)
        self.op.memory_write(to_addr, data)
        return True

    def sta(self, addr: str) -> bool:
        """
        STore Accumulator

        Parameters
        ----------
        addr : `str`
            store the accumulator data in `addr`
        """
        data = self.op.memory_read("A")
        self.op.memory_write(addr, data)
        return True

    def db(self, *args) -> bool:
        """
        Directive to store the data at address location pointed by the ``PC``

        Parameters
        ----------
        *args : `tuple`
        """
        for x in args:
            self.op.super_memory.PC.write(x)
        return True

    def add(self, to_addr, from_addr=None) -> bool:
        """
        Adds `to_addr` with `from_addr`

        Parameters
        ----------
        from_addr : `str`
            From address

        to_addr : `str`
            To address
        """
        if not from_addr:
            from_addr = to_addr
            to_addr = "A"
        from_data = self.op.memory_read(from_addr)
        to_data = self.op.memory_read(to_addr)
        data = self._check_flags_and_compute(from_data, to_data)
        self.op.memory_write(to_addr, data)
        return True

    def sub(self, from_addr: str, to_addr: str = None) -> bool:
        """
        Subtracts `to_addr` from `from_addr` with Borrow

        Parameters
        ----------
        from_addr : `str`
            From address

        to_addr : `str`
            To address
        """
        if not to_addr:
            to_addr = from_addr
            from_addr = "A"
        to_data = self.op.memory_read(to_addr)
        from_data = self.op.memory_read(from_addr)
        result_data = self._check_flags_and_compute(from_data, to_data, add=False)
        self.op.memory_write(from_addr, result_data)
        return True

    def sbb(self, from_addr: str, to_addr: str = None) -> bool:
        """
        Subtracts `to_addr` from `from_addr` with Borrow

        Parameters
        ----------
        from_addr : `str`
            From address

        to_addr : `str`
            To address
        """
        if not to_addr:
            to_addr = from_addr
            from_addr = "A"
        to_data = self.op.memory_read(to_addr)
        from_data = self.op.memory_read(from_addr)
        if flags.CY:
            flags.CY = False
            from_data += 1
        result_data = self._check_flags_and_compute(from_data, to_data, add=False)
        self.op.memory_write(from_addr, result_data)
        return True

    def lxi(self, addr, data) -> bool:
        """
        Load eXtended register

        Parameters
        ----------
        addr : `str`
        data : `str`
        """
        self.op.register_pair_write(addr, data)
        return True

    def inr(self, addr: str) -> bool:
        """
        InCrement Register

        Parameters
        ----------
        addr : `str`, `hex`
        """
        data = self.op.memory_read(addr)
        data_to_write = self._check_flags_and_compute(data, "0x01", _CY=False)
        self.op.memory_write(addr, data_to_write)
        return True

    def inx(self, addr: str) -> bool:
        """
        InCrement eXtended register

        Parameters
        ----------
        addr : `str`

        Note
        ----
        The flags are not at all affected by the execution of this instruction.
        """
        data = self.op.register_pair_read(addr)
        data_to_write = format(int(data, 16) + 1, "#06x")
        self.op.register_pair_write(addr, data_to_write)
        return True

    def dcr(self, addr: str) -> bool:
        """
        DeCrement Register

        Parameters
        ----------
        addr : `str`, `hex`
        """
        data = self.op.memory_read(addr)
        data_to_write = self._check_flags_and_compute(data, "0x01", add=False, _CY=False)
        self.op.memory_write(addr, data_to_write)
        return True

    def dcx(self, addr: str) -> bool:
        """
        DeCrement eXtended register
        Decrements the `addr` register pair.

        Parameters
        ----------
        addr : `str`, (`B`, `D`, `H`)

        The flags are not at all affected by the execution of this instruction.
        """
        data = self.op.register_pair_read(addr)
        data_to_write = format(int(data, 16) - 1, "#06x")
        self.op.register_pair_write(addr, data_to_write)
        return True

    def lhld(self, addr: str) -> bool:
        """
        Loads the data from `addr` into HL pair.

        Parameters
        ----------
        addr : `str`, hex
        """
        data_1 = self.op.memory_read(addr)
        nxt_addr = format(int(addr, 16) + 1, "#06x")
        data_2 = self.op.memory_read(nxt_addr)
        self.op.memory_write("H", data_2)
        self.op.memory_write("L", data_1)
        return True

    def xchg(self, *args) -> bool:
        """
        eXChanGes the data stored in HL and DE pairs.
        """
        data_1 = self.op.register_pair_read("H")
        data_2 = self.op.register_pair_read("D")
        self.op.register_pair_write("D", data_1)
        self.op.register_pair_write("H", data_2)
        return True

    def dad(self, addr: str) -> bool:
        """
        Adds the HL and `addr` pair and store the result in HL.

        Parameters
        ----------
        addr : `str` (rp, `B`, `D`, `H`)

        Note
        ----
        `DAD` only affects the `CY` flag

        """
        data_1 = self.op.register_pair_read(addr)
        data_2 = self.op.register_pair_read("H")
        addition = int(data_1, 16) + int(data_2, 16)

        # check `CY` flag
        if addition > int("0xffff", 16):
            addition = addition - (int("0xffff", 16) + 1)
            flags.CY = True

        addition = format(addition, "#06x")
        self.op.register_pair_write("H", addition)
        return True

    def jnc(self, label, *args, **kwargs) -> bool:
        """
        Jump if Not Carry
        """
        bounce_to_label = kwargs.get("bounce_to_label")
        if not flags.CY:
            return bounce_to_label(label)
        return True

    def jc(self, label, *args, **kwargs) -> bool:
        """
        Jump if Carry
        """
        bounce_to_label = kwargs.get("bounce_to_label")
        if flags.CY:
            return bounce_to_label(label)
        return True

    def jz(self, label, *args, **kwargs) -> bool:
        """
        Jump if Zero
        """
        bounce_to_label = kwargs.get("bounce_to_label")
        if flags.Z:
            return bounce_to_label(label)
        return True

    def jnz(self, label, *args, **kwargs) -> bool:
        """
        Jump if Not Zero
        """
        bounce_to_label = kwargs.get("bounce_to_label")
        if not flags.Z:
            return bounce_to_label(label)
        return True

    def shld(self, addr: str) -> bool:
        """
        Store HL pair data

        Parameters
        ----------
        addr : `str`
            Address
        """
        data_1 = self.op.memory_read("H")
        data_2 = self.op.memory_read("L")
        self.op.memory_write(addr, data_2)
        nxt_addr = format(int(addr, 16) + 1, "#06x")
        self.op.memory_write(nxt_addr, data_1)
        return True

    def ora(self, addr: str) -> bool:
        """
        OR logical instruction

        Parameters
        ----------
        addr : `str`
            Address
        """
        data_1 = int(self.op.memory_read("A"))
        data_2 = int(self.op.memory_read(addr))
        result = format(data_1 | data_2, "#04x")
        self.op.memory_write("A", result)
        self._check_flags(format(int(result, self._base), "08b"))
        return True

    def ral(self) -> bool:
        """
        <--CY--A7----A0<---<-
        |                   |
        ->------------------>
        """
        data = self.op.memory_read("A")
        data_bin = list(format(int(str(data), 16), "08b"))
        rolled_data_bin = []

        for i in range(0, len(data_bin[:-1])):
            rolled_data_bin.append(data_bin[i + 1])

        # CY into new LSB
        rolled_data_bin.insert(8, str(int(flags.CY)))
        # MSB into CY
        flags.CY = bool(int(data_bin[0]))

        rolled_data_bin = "".join(rolled_data_bin)
        data_new = format(int(rolled_data_bin, 2), "#02x")
        self.op.memory_write("A", data_new)
        return True

    def rlc(self) -> bool:
        """
        CY<---A7----A0<---<-
            |              |
            ->------------->
        """
        data = self.op.memory_read("A")
        data_bin = list(format(int(str(data), 16), "08b"))
        rolled_data_bin = []

        for i in range(0, len(data_bin[:-1])):
            rolled_data_bin.append(data_bin[i + 1])

        # CY into new LSB
        rolled_data_bin.insert(8, str(int(data_bin[0])))
        # MSB into CY
        flags.CY = bool(int(data_bin[0]))

        rolled_data_bin = "".join(rolled_data_bin)
        data_new = format(int(rolled_data_bin, 2), "#02x")
        self.op.memory_write("A", data_new)
        return True

    def cmp(self, addr) -> bool:
        """
        CoMPareAccumulator
        CMP is same as SUB except it doesn't save the result!

        CMP R; R = A, B, C, D, E, H, L, or M

        A < R --> `CY` is set; `Z is reset
        A = R --> `CY` is reset; `Z` is set
        A > R --> `CY` and `Z` are reset

        ** Check the condition of other flags in this instruction **

        Parameters
        ----------
        addr : `str`
            Address
        """
        warnings.warn("** Check the condition of other flags in this instruction **")
        data_1 = self.op.memory_read("A")
        data_2 = self.op.memory_read(addr)

        if int(str(data_1), 16) > int(str(data_2), 16):
            flags.CY = True
            flags.Z = False
        elif int(str(data_1), 16) < int(str(data_2), 16):
            flags.CY = False
            flags.Z = False
        else:
            flags.CY = False
            flags.Z = True
        return True

    def push(self, addr: str) -> bool:
        """
        PUSH rp
        rp = BC, DE, HL, or PSW

        Pushs the register pair into the stack.

        Parameters
        ----------
        addr : `str`
            Address
        """
        data_1 = self.op.register_pair_read(addr)
        return self.op.super_memory.SP.write(data_1)

    def pop(self, addr: str) -> bool:
        """
        POP rp
        rp = BC, DE, HL, or PSW

        Pushs a register pair from the stack and store it in `addr`

        Parameters
        ----------
        addr : `str`
            Address
        """
        data_1 = self.op.super_memory.SP.read()
        return self.op.register_pair_write(addr, data_1)

    def hlt(self) -> bool:
        raise StopIteration

    pass
