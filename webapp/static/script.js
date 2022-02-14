window.onload = function () {
    console.log("load")
    // reload code contents
    document.getElementById("code").value = localStorage.getItem("code")

    document.getElementById("run").disabled = true

    document.getElementById("assemble").addEventListener("click", function () {
        console.log("assemble")
        const request = new XMLHttpRequest();
        request.open("POST", `/assemble`);
        request.onload = () => {
            const response = request.responseText;
            console.log(request.status)
            if (request.status != 200) {
                alert(response)
            }
            else {
                document.getElementById("run").disabled = false
                document.getElementById("memory-container").innerHTML = response;
            }
        };
        let _code = document.getElementById("code").value
        if (_code) {
            // save code
            localStorage.setItem("code", _code)
            console.log("sent")
            console.log(JSON.stringify(
                {
                    "code": _code,
                    "flags": GetFlags()
                }
            ))
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
            }
        };
        let _code = document.getElementById("code").value
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
                document.getElementById("run").disabled = true
            }
        };
        request.send();
    });
}
function GetFlags() {
    var flags_dict = {}
    document.querySelectorAll(".flag-input").forEach(element => {
        console.log(element.checked);
        flags_dict[element.id] = element.checked
    });
    return flags_dict

}