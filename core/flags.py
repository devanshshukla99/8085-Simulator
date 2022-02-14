import textwrap


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

    def _set_property(self, key):
        return property(fget=lambda: self._flags.__getitem__(key), fset=lambda val: self._flags.__setitem__(key, val))

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
            C = {self.CY}
            AC = {self.AC}
            S = {self.S}
            P = {self.P}
            Z = {self.Z}
            """
        )

    CY = property(fget=lambda self: self._flags.get("CY"), fset=lambda self, val: self._flags.__setitem__("CY", val))
    P = property(fget=lambda self: self._flags.get("P"), fset=lambda self, val: self._flags.__setitem__("P", val))
    AC = property(fget=lambda self: self._flags.get("AC"), fset=lambda self, val: self._flags.__setitem__("AC", val))
    Z = property(fget=lambda self: self._flags.get("Z"), fset=lambda self, val: self._flags.__setitem__("Z", val))
    S = property(fget=lambda self: self._flags.get("S"), fset=lambda self, val: self._flags.__setitem__("S", val))

    pass


flags = Flags()
