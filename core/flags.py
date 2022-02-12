import textwrap


class Flags:
    """
    C = Carry
    AC = Auxillary Carry
    S = Sign
    P = Parity
    Z = Zero
    """

    C: bool = False
    AC: bool = False
    S: bool = False
    P: bool = False
    Z: bool = False

    def items(self):
        return {"C": self.C, "AC": self.AC, "S": self.S, "P": self.P, "Z": self.Z,}.items()

    def reset(self):
        self.C = False
        self.AC = False
        self.S = False
        self.P = False
        self.Z = False
        return True

    def inspect(self):
        return textwrap.dedent(
            f"""
            Flags
            -----
            C = {self.C}
            AC = {self.AC}
            S = {self.S}
            P = {self.P}
            Z = {self.Z}
            """
        )

    pass


flags = Flags()
