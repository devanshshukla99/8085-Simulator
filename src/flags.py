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
