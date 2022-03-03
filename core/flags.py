import textwrap

from core.memory import Hex


class JumpFlag:
    def __init__(self, label: str, counter: str, command, *args, **kwargs) -> None:
        self._label = label.upper()
        self._counter = Hex(str(counter), _bytes=2)
        self._command = command
        self._endpoint = ""

    def __repr__(self) -> str:
        return f"<command:{self._command} label:{self._label} counter:{self._counter} endpoint:{self._endpoint}>"

    def __eq__(self, val: object) -> bool:
        return self._label == val.upper()

    def __bool__(self) -> bool:
        return bool(self._label)

    def match(self, label: str) -> bool:
        return label.upper() == self._label

    def upper(self) -> str:
        return self._label.upper()

    pass


class Flags:
    """
    C = Carry
    AC = Auxillary Carry
    S = Sign
    P = Parity
    Z = Zero
    """

    def __init__(self) -> None:
        self._flags = {
            "CY": False,  # D0
            "P": False,  # D2
            "AC": False,  # D4
            "Z": False,  # D6
            "S": False,  # D7
        }

    def __repr__(self):
        return self.inspect()

    def __getitem__(self, key):
        return self._flags[key]

    def __setitem__(self, key, val):
        self._flags[key] = val

    def set_flags(self, flags_dict):
        for key, val in flags_dict.items():
            self._flags.__setitem__(key, val)
        return True

    def todict(self):
        return self._flags

    def items(self):
        return self._flags.items()

    def reset(self):
        for _k in self._flags.keys():
            self._flags.__setitem__(_k, False)
        return True

    def inspect(self):
        return textwrap.dedent(
            f"""
            Flags
            -----
            CY = {self.CY}
            P = {self.P}
            AC = {self.AC}
            Z = {self.Z}
            S = {self.S}
            """
        )

    CY = property(fget=lambda self: self._flags.get("CY"), fset=lambda self, val: self._flags.__setitem__("CY", val))
    P = property(fget=lambda self: self._flags.get("P"), fset=lambda self, val: self._flags.__setitem__("P", val))
    AC = property(fget=lambda self: self._flags.get("AC"), fset=lambda self, val: self._flags.__setitem__("AC", val))
    Z = property(fget=lambda self: self._flags.get("Z"), fset=lambda self, val: self._flags.__setitem__("Z", val))
    S = property(fget=lambda self: self._flags.get("S"), fset=lambda self, val: self._flags.__setitem__("S", val))

    pass


flags = Flags()
