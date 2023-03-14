$(document).ready(function () {
    var socket = new webSocket('ws://' + window.location.host + '/ws/' + curDevice + '/');

    socket.onmessage = function (e) {
        var data = JSON.parse(e.data);
        console.log(data);
    };
});