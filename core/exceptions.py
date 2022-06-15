class SyntaxError(Exception):
    def __init__(self, msg="invalid syntax") -> None:
        """Exception raised on a syntax error."""
        super().__init__(msg)


class OPCODENotFound(Exception):
    def __init__(self, msg="invalid opcode") -> None:
        """Exception raised when an invalid opcode is encountered."""
        super().__init__(msg)


class MemoryLimitExceeded(Exception):
    def __init__(self, msg="Memory limit exceeded") -> None:
        """Exception raised when the memory limit is exceeded."""
        super().__init__(msg)


class InvalidMemoryAddress(Exception):
    def __init__(self, msg="Invalid memory address") -> None:
        """Exception raised when the provided memory address is invalid."""
        super().__init__(msg)


class ValueErrorHexRequired(ValueError):
    def __init__(self, value: str, msg="invalid valid; only hex supported!") -> None:
        """Exception raised when the provided value is not in hexadecimal format."""
        super().__init__(f"{msg}({value})")
