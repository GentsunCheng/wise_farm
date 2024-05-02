var createError = require('http-errors');
var compression = require('compression')
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
const fs = require('fs');
const os = require('os');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

var app = express();


function getServerIP() {
  const interfaces = os.networkInterfaces();
  // 遍历网络接口
  for (const interfaceName in interfaces) {
    // 如果是以 eth 开头的接口名（通常是 Ethernet 接口）
    if (interfaceName.startsWith('WLAN') || interfaceName.startsWith('eth') || interfaceName.startsWith('end')) {
      const interfaceInfo = interfaces[interfaceName];
      // 遍历接口的详细信息
      for (const interfaceDetail of interfaceInfo) {
        // 如果是 IPv4 地址且不是回环地址
        if (interfaceDetail.family === 'IPv4' && !interfaceDetail.internal) {
          return interfaceDetail.address;
        }
      }
    }
  }
  return null;
}
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use((req, res, next) => {
  console.log(req.originalUrl)
  if (req.originalUrl === '/javascripts/real.js' || req.originalUrl === '/javascripts/history.js' || req.originalUrl === 'javascripts/control.js') { // 检查请求路径
    // 读取替换内容
    const filePath = path.join(__dirname, 'public' + req.originalUrl);
    let fileContent = fs.readFileSync(filePath, 'utf8');
    // 将 {{ip}} 替换为服务器 IP 地址
    const serverIP = getServerIP();
    fileContent = fileContent.replace('{{ip}}', serverIP);
    // 发送替换后的文件内容
    res.set('Content-Type', 'text/javascript'); // 设置响应头
    res.send(fileContent);
  } else {
    next(); // 如果不是目标路由，继续下一个中间件
  }
});

app.use(compression());
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/users', usersRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
