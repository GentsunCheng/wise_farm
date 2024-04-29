// 创建 WebSocket 连接
const socket = new WebSocket('ws://localhost:8765'); // 请替换成你的 WebSocket 服务器地址

// 当连接建立时
socket.addEventListener('open', function (event) {
    console.log('Connected to server');
});

// 当收到消息时
socket.addEventListener('message', function (event) {
    console.log('Message from server:', event.data);
});

// 当连接关闭时
socket.addEventListener('close', function (event) {
    console.log('Connection closed');
});