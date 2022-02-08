"""
Instructions -- 256
------------

Registers -- 6
---------
A/PSW 0x 00 00
BC 0x 00 00
DE 0x 00 00
HL 0x 00 00
SP 0x 00 00
PC 0x 00 00

Flags -- 6
-----
Z
S
P
C
AC
PC

ALU
clock
Control unit
I/O
"""

from src.exceptions import OPCODENotFound
from src.controller import Controller
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.console import Console


def make_layout():
    layout = Layout(name="main")

    layout["main"].split(
        Layout(name="side"), Layout(name="body", ratio=2), splitter="row",
    )
    layout["side"].split(Layout(name="registers"), Layout(name="flags"))
    layout["body"].split(Layout(name="cmd_area", ratio=2), Layout(name="memory"))
    return layout


def main():
    console = Console()
    # layout = make_layout()
    prompt = Prompt()
    # with Live(prompt, console=console) as live:
    controller = Controller()

    while True:
        try:
            command = prompt.ask("[bold][red]Input>[/]")
            if not command:
                continue
            elif command == "quit" or command == "exit":
                exit(-1)
            elif command[0] == "/":
                if command == "/inspect":
                    console.print(controller.op.inspect())
                    continue
                else:
                    # ! REMOVE THIS LATER
                    console.print(eval(command[1:]))
            else:
                try:
                    controller.parse_and_call(command)
                except OPCODENotFound:
                    console.print_exception(extra_lines=2)
        except KeyboardInterrupt:
            print("")

        except EOFError:
            console.log("[red]Exiting...[/]")
            exit(-1)

        except Exception:
            console.print_exception(extra_lines=2)


if __name__ == "__main__":
    main()
