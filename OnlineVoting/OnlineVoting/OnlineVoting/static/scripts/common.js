var get_parameters = window.location.hash.split("#");
if (get_parameters.length === 2) {
    var parameters = get_parameters[1].split("=");
    if (parameters.length === 2 && parameters[0] === "token") {
        document.cookie = get_parameters[1];
    }
}
