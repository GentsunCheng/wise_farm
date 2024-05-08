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
    createTable(data); // 调用创建表格函数并传入数据
});

function createTable(data) {
    const mainDiv = document.querySelector('.main');
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // 创建表头
    const headerRow = document.createElement('tr');
    const th1 = document.createElement('th');
    th1.textContent = '表名';
    const th2 = document.createElement('th');
    th2.textContent = '数据';
    headerRow.appendChild(th1);
    headerRow.appendChild(th2);
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // 遍历数据，创建表格内容
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            const value = data[key];
            const row = document.createElement('tr');
            const cell1 = document.createElement('td');
            cell1.textContent = key;
            const cell2 = document.createElement('td');
            cell2.textContent = value;
            row.appendChild(cell1);
            row.appendChild(cell2);

            // 创建按钮并绑定点击事件
            const button = document.createElement('button');
            button.textContent = key; // 按钮文本内容是日期
            button.addEventListener('click', function() {
                detail(value); // 点击按钮执行 detail 函数，并传入相应参数
            });

            // 将按钮添加到单元格中
            const cell3 = document.createElement('td');
            cell3.appendChild(button);
            row.appendChild(cell3);

            tbody.appendChild(row);
        }
    }
    table.appendChild(tbody);
    mainDiv.appendChild(table);
}

function detail(data) {
    console.log('Detail function executed with data:', data);
    // 在这里执行 detail 函数的具体操作，data 是传入的参数，即格式为 "data20xxxxxx" 的字符串
}
