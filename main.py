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

import textwrap

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Confirm, Prompt

from core.controller import Controller
from core.exceptions import OPCODENotFound


def make_layout():
    layout = Layout(name="main")

    layout["main"].split(
        Layout(name="side"),
        Layout(name="body", ratio=2),
        splitter="row",
    )
    layout["side"].split(Layout(name="registers"), Layout(name="flags"))
    layout["body"].split(Layout(name="cmd_area", ratio=2), Layout(name="memory"))
    return layout


def run(filename):
    console = Console()
    controller = Controller()
    coms = None
    with open(filename, "r") as f:
        coms = f.read()
    coms = coms.split("\n")
    try:
        for command in coms:
            console.log(command)
            if not command:
                continue
            elif command == "quit" or command == "exit":
                exit(-1)
            elif command[0] == "/":
                command = command[1:]
                if hasattr(controller, command):
                    console.log(getattr(controller, command)())
            else:
                try:
                    controller.parse(command)
                except OPCODENotFound:
                    console.print_exception(extra_lines=2)
    except KeyboardInterrupt:
        print("")

    except EOFError:
        console.log("[red]Exiting...[/]")
        exit(-1)

    except Exception:
        console.print_exception(extra_lines=2)
    return


def main():
    console = Console()
    # layout = make_layout()
    prompt = Prompt()
    # with Live(prompt, console=console) as live:
    controller = Controller()

    console.log(
        textwrap.dedent(
            """
            Input>: COMMANDS
            COMMANDS can be:
                /inspect = inpect the memory and registers
                /run = run
                /reset = reset
                [red]OR[/]
                ANY 8085 INSTRUCTION -- example `mvi a, 0x12` etc.
            """
        )
    )
    while True:
        try:
            command = prompt.ask("[bold][red]Input>[/]")
            if not command:
                continue
            elif command == "quit" or command == "exit":
                exit(-1)
            elif command[0] == "/":
                command = command[1:]
                if hasattr(controller, command):
                    console.log(getattr(controller, command)())
                else:
                    console.log("instruction not found")
            else:
                try:
                    controller.parse(command)
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
