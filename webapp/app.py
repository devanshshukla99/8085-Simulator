from flask import Flask, render_template, request, Response, make_response
from src.controller import Controller
from src.flags import flags
from src.exceptions import OPCODENotFound

CLEAR_TOKEN = "batman"
app = Flask(__name__, static_folder="static")
controller = Controller()


@app.route("/reset", methods=["POST"])
def reset():
    global controller
    controller.reset()
    return {
        "registers_flags": render_template(
            "render_registers_flags.html", registers=controller.op.super_memory._registers_todict(), flags=flags
        ),
        "memory": render_template("render_memory.html", memory=controller.op.memory),
    }


@app.route("/assemble", methods=["POST"])
def assemble():
    global controller
    commands = request.data
    if commands:
        try:
            controller.parse_all(commands.decode())
            return render_template("render_memory.html", memory=controller.op.memory)
        except OPCODENotFound:
            pass
    return make_response("Record not found", 400)


@app.route("/run", methods=["POST"])
def run():
    global controller
    print(controller.ready)
    if controller.ready:
        try:
            controller.run()
            return render_template(
                "render_registers_flags.html", registers=controller.op.super_memory._registers_todict(), flags=flags
            )
        except OPCODENotFound:
            pass
    return make_response("Record not found", 400)


@app.route("/", methods=["GET"])
def main():
    global controller
    controller = Controller()
    return render_template(
        "index.html",
        memory=controller.op.memory,
        registers=controller.op.super_memory._registers_todict(),
        flags=flags,
    )
