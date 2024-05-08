let wsurl;
if (location.protocol === 'https:') {
    wsurl = `wss://${location.host}/ws`;
} else {
    wsurl = `ws://${location.host}/ws`;
}

const socket = new WebSocket(wsurl);

socket.addEventListener('open', function (event) {
    socket.send("history");
    console.log('Connected to server');
});

socket.addEventListener('message', function (event) {
    console.log('Message from server:', event.data);
    const data = JSON.parse(event.data);
});