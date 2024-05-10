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
    th1.textContent = '编号';
    const th2 = document.createElement('th');
    th2.textContent = '日期';
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

            // 使用正则表达式提取日期部分
            const dateRegex = /data(\d{8})/;
            const match = value.match(dateRegex);
            let dateString = '';
            if (match) {
                dateString = match[1]; // 提取日期部分
            }

            // 创建按钮并绑定点击事件
            const button = document.createElement('button');
            button.classList.add('fluent-button');
            button.textContent = dateString; // 按钮文本是日期字符串

            button.addEventListener('click', function() {
                socket.close();
                detail(value); // 点击按钮执行 detail 函数，并传入相应参数
            });

            // 将按钮添加到单元格中
            const cell2 = document.createElement('td');
            cell2.appendChild(button);

            // 将单元格添加到行中
            row.appendChild(cell1);
            row.appendChild(cell2);

            // 将行添加到 tbody 中
            tbody.appendChild(row);
        }
    }
    // 将 tbody 添加到 table 中
    table.appendChild(tbody);
    // 将 table 添加到 mainDiv 中
    mainDiv.appendChild(table);
}

function detail(data) {
    const detail_socket = new WebSocket(wsurl);
    detail_socket.addEventListener('open', function (event) {
        detail_socket.send(data);
        console.log('Connected to server(detail)');
    });
    detail_socket.addEventListener('message', function (event) {
        console.log('Message from server:', event.data);
        const detail_data = JSON.parse(event.data);

        // 关闭 WebSocket 连接
        detail_socket.close();

        // 创建表格
        createDetailTable(detail_data);
    });
}

function createDetailTable(detail_data) {
    const mainDiv = document.querySelector('.main');
    mainDiv.innerHTML = '';
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');
    const tr = document.createElement('tr');
    const th1 = document.createElement('th');
    th1.textContent = '时间';
    const th2 = document.createElement('th');
    th2.textContent = '温度';
    const th3 = document.createElement('th');
    th3.textContent = 'CO2';
    const th4 = document.createElement('th');
    th4.textContent = '光照';
    tr.appendChild(th1);
    tr.appendChild(th2);
    tr.appendChild(th3);
    tr.appendChild(th4);
    thead.appendChild(tr);
    table.appendChild(thead);
    mainDiv.appendChild(table);

    for (const timestamp in detail_data) {
        if (detail_data.hasOwnProperty(timestamp)) {
            const rowData = detail_data[timestamp];
            const row = document.createElement('tr');

            // 创建单元格并设置时间戳
            const timeCell = document.createElement('td');
            timeCell.textContent = timestamp;
            row.appendChild(timeCell);

            // 遍历该时间戳下的数据
            for (const key in rowData) {
                if (rowData.hasOwnProperty(key)) {
                    // 创建单元格并设置数据值
                    const valueCell = document.createElement('td');
                    valueCell.textContent = rowData[key];
                    row.appendChild(valueCell);
                }
            }

            // 将行添加到表体中
            tbody.appendChild(row);
        }
    }

    // 将表体添加到表格中
    table.appendChild(tbody);

    // 将表格添加到主容器中
    mainDiv.appendChild(table);
}

