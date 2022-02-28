window.onload = function () {
    console.log("load")
    // reload code contents
    document.getElementById("code").innerHTML = localStorage.getItem("code")

    document.getElementById("run").disabled = true
    document.getElementById("step").disabled = true


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
            }
        };
        var _code = UnApplyHighlights(ProcessCode(document.getElementById("code").innerHTML))
        if (_code) {
            // save code
            localStorage.setItem("code", UnProcessCode(_code))
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
        console.log("run")
        const request = new XMLHttpRequest();
        request.open("POST", `/run`);
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
            }
        };
        var _code = ProcessCode(document.getElementById("code").innerHTML)
        request.send(UnApplyHighlights(_code));
    });

    document.getElementById("step").addEventListener("click", function () {
        console.log("step")
        const request = new XMLHttpRequest();
        request.open("POST", `/run-once`);
        request.onload = () => {
            const response = request.responseText;
            if (request.status != 200) {
                alert(response)
            }
            else {
                const _resp_dict = JSON.parse(response)
                index = _resp_dict["index"];
                document.getElementById("registers-flags").innerHTML = _resp_dict["registers_flags"];
                document.getElementById("memory-container").innerHTML = _resp_dict["memory"];
                document.getElementById("assembler-container").innerHTML = _resp_dict["assembler"];
                document.getElementById("code").innerHTML = UnProcessCode(ApplyHighlights(_code, index - 1))
                console.log(index)
            }
        };
        var _code = ProcessCode(document.getElementById("code").innerHTML)
        request.send(UnApplyHighlights(_code));
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
                document.getElementById("code").innerHTML = UnApplyHighlights(document.getElementById("code").innerHTML)
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
function ProcessCode(code) {
    code = code.replaceAll("<div>", "\n")
    code = code.replaceAll("</div>", "")
    code = code.replaceAll("<br>", "\n")
    return code
}
function UnProcessCode(code) {
    return code.replaceAll("\n", "<br>")
}
function UnApplyHighlights(code) {
    code = code.replaceAll(/<highlight>/gm, "")
    code = code.replaceAll(/<\/highlight>/gm, "")
    return code.replaceAll("<br>", "\n")
}
function ApplyHighlights(code, index) {
    code = ProcessCode(code)
    code = UnApplyHighlights(code)
    code = code.split("\n")
    if (index < code.length) {
        if (code[index]) {
            code[index] = "<highlight>" + code[index] + "</highlight>"
            return code.join("\n")
        }
    }
    return code.join("\n")
}