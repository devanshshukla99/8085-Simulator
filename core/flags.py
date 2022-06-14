import textwrap

from core.memory import Hex


class JumpFlag:
    def __init__(self, label: str, counter: str, command, *args, **kwargs) -> None:
        """
        Implements jump-flag functionality

        Parameters
        ----------
        label : str
            Jump flag label
        counter : `str`
            Program counter
        command : `str`
            Command
        """
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
        """
        Match the incoming label with instantiated label.

        Parameters
        ----------
        label : `str`
            Incoming label
        """
        return label.upper() == self._label

    def upper(self) -> str:
        """
        Return the instantiated label.

        Returns
        -------
        `str`
        """
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
        """In 8085 the flags are stores in the PSW as ``S Z - AC - P - CY``. This class implements this functionality."""
        self._flags = {
            "CY": False,  # D0
            "P": False,  # D2
            "AC": False,  # D4
            "Z": False,  # D6
            "S": False,  # D7
        }

    def __repr__(self):
        return self.inspect()

    def __getitem__(self, key: str):
        return self._flags[key]

    def __setitem__(self, key: str, val: str):
        self._flags[key] = val

    def set_flags(self, flags_dict: dict):
        """
        Method to set flag according to `flags_dict`

        Parameters
        ----------
        flags_dict : `dict`
        """
        for key, val in flags_dict.items():
            self._flags.__setitem__(key, val)
        return True

    def todict(self):
        """Method to return the flags as `dict`"""
        return self._flags

    def items(self):
        """Method to return the flags as `~dict.items`"""
        return self._flags.items()

    def reset(self):
        """Method to reset the flags."""
        for _k in self._flags.keys():
            self._flags.__setitem__(_k, False)
        return True

    def inspect(self):
        """Method to inspect the flags."""
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
