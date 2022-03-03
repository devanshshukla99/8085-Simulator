window.onload = function () {
    console.log("load");
    // reload code contents
    document.getElementById("code").value = localStorage.getItem("code");

    document.getElementById("run").disabled = true;
    document.getElementById("step").disabled = true;

    document.getElementById("assemble").addEventListener("click", function () {
        console.log("assemble")
        const request = new XMLHttpRequest();
        request.open("POST", `/assemble`);
        request.onload = () => {
            const response = request.responseText;
            if (request.status != 200) {
                alert(response)
            }
            else {
                document.getElementById("run").disabled = false
                document.getElementById("step").disabled = false
                document.getElementById("memory-container").innerHTML = response;
                ProgressSideBar(_code, 0)
            }
        };
        var _code = document.getElementById("code").value.trim();
        if (_code) {
            // save code
            localStorage.setItem("code", _code)
            console.log("sent")
            request.send(JSON.stringify(
                {
                    "code": _code,
                    "flags": GetFlags()
                }
            ));
        }
    });

    document.getElementById("run").addEventListener("click", function () {
        console.log("run");
        const request = new XMLHttpRequest();
        request.open("POST", `/run`);
        request.onload = () => {
            const response = request.responseText;
            if (request.status != 200) {
                alert(response);
            }
            else {
                const _resp_dict = JSON.parse(response)
                document.getElementById("registers-flags").innerHTML = _resp_dict["registers_flags"];
                document.getElementById("memory-container").innerHTML = _resp_dict["memory"];
                document.getElementById("assembler-container").innerHTML = _resp_dict["assembler"];
                ProgressSideBar(_code, _code.split("\n").length)
            }
        };
        var _code = document.getElementById("code").value.trim();
        request.send(_code);
    });

    document.getElementById("step").addEventListener("click", function () {
        console.log("step");
        const request = new XMLHttpRequest();
        request.open("POST", `/run-once`);
        request.onload = () => {
            const response = request.responseText;
            if (request.status != 200) {
                AlertProgressSideBar()
                alert(response)
            }
            else {
                const _resp_dict = JSON.parse(response)
                index = _resp_dict["index"];
                document.getElementById("registers-flags").innerHTML = _resp_dict["registers_flags"];
                document.getElementById("memory-container").innerHTML = _resp_dict["memory"];
                document.getElementById("assembler-container").innerHTML = _resp_dict["assembler"];
                document.getElementById("code").value = _code;
                ProgressSideBar(_code, index)
            }
        };
        var _code = document.getElementById("code").value.trim();
        request.send(_code);
    });

    document.getElementById("reset").addEventListener("click", function () {
        console.log("reset")
        const request = new XMLHttpRequest();
        request.open("POST", `/reset`);
        request.onload = () => {
            const response = request.responseText;
            if (request.status != 200) {
                alert(response)
            }
            else {
                const _resp_dict = JSON.parse(response)
                document.getElementById("registers-flags").innerHTML = _resp_dict["registers_flags"];
                document.getElementById("memory-container").innerHTML = _resp_dict["memory"];
                document.getElementById("assembler-container").innerHTML = _resp_dict["assembler"];
                document.getElementById("run").disabled = true
                document.getElementById("step").disabled = true
                document.getElementById("track").textContent = ""

            }
        };
        request.send();
    });
}

function GetFlags() {
    var flags_dict = {}
    document.querySelectorAll(".flag-input").forEach(element => {
        flags_dict[element.id] = element.checked
    });
    return flags_dict
}
function AlertProgressSideBar() {
    var track = document.getElementById("track");
    _track = track.textContent.trim().split("\n")
    _track[_track.length - 1] = "❌\n"
    track.textContent = _track.join("\n")
}
function ProgressSideBar(code, index) {
    var track = document.getElementById("track");
    console.log(index, code, code.split("\n").length)
    track.textContent = ""
    for (let i = 0; i < index; i++) {
        track.textContent += "✔\n"
    }
    if (index < code.split("\n").length) {
        track.textContent += "▶"
    }
}
