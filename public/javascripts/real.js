const socket = new WebSocket('ws://localhost:8765'); // 请替换成你的 WebSocket 服务器地址

// 定义温度数据数组
let datas = {
    'temp': [],
    'co2': [],
    'light': []
}


// 当连接建立时
socket.addEventListener('open', function (event) {
    console.log('Connected to server');
});

// 当收到消息时
socket.addEventListener('message', function (event) {
    console.log('Message from server:', event.data);
    const data = JSON.parse(event.data);
    const { temperature, co2, light } = data;
    const temperatureData = parseInt(temperature);
    const co2Data = parseInt(co2);
    const lightData = parseInt(light);
    // 更新温度数据
    updateData(temperatureData, 'temp');
    // 更新二氧化碳数据
    updateData(co2Data, 'co2');
    // 更新光照强度数据
    updateData(lightData, 'light');
});

// 当连接关闭时
socket.addEventListener('close', function (event) {
    console.log('Connection closed');
});

// 更新温度数据的函数
function updateData(newData, type) {
    var canvas = document.getElementById(type);
    var ctx = canvas.getContext('2d');
    var scale = 10;
    var unit = '°C';
    var data = [];
    if (type === 'temp') {
        scale = 10;
        unit = '°C';
        datas.temp.push(newData);
        data = datas.temp;
        if (datas.temp.length > 20) {
            datas.temp.shift(); // 移除最旧的数据
        }
    } else if (type === 'co2') {
        scale = 1;
        unit = 'ppm';
        datas.co2.push(newData);
        data = datas.co2;
        if (datas.co2.length > 20) {
            datas.co2.shift(); // 移除最旧的数据
        }
    } else if (type === 'light') {
        scale = 20;
        unit = 'kLux';
        datas.light.push(newData);
        data = datas.light;
        if (datas.light.length > 20) {
            datas.light.shift(); // 移除最旧的数据
        }
    }

    // 绘制折线图
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 绘制坐标轴
    ctx.beginPath();
    ctx.moveTo(30, 10);
    ctx.lineTo(30, canvas.height - 10);
    ctx.lineTo(canvas.width - 10, canvas.height - 10);
    ctx.stroke();

    // 绘制纵坐标刻度
    ctx.fillStyle = 'black';
    for (let i = 0; i <= 5; i++) {
        const y = canvas.height - 10 - i * (canvas.height - 20) / 5;
        ctx.fillText((scale * i) + unit, 5, y + 5); // 在坐标轴上绘制刻度标签
    }

    // 绘制数据折线
    ctx.beginPath();
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 1;
    for (let i = 0; i < data.length; i++) {
        const x = canvas.width - 10 - (data.length - i - 1) * 20; // 横坐标
        const y = canvas.height - 10 - (data[i] - 0) * (canvas.height - 20) / 50; // 纵坐标
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    ctx.stroke();
}


