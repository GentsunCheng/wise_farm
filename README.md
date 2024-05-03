# 智慧农场
## 硬件设备
VisionFive2  
AD7705  
土壤湿度传感器模块  
光敏电阻传感器模块  
SGP30气体传感器模块  
RGB全彩LED模块  
# nginx配置
```yaml
server {
    listen [::]:80;
    listen 80;

    listen [::]:443 ssl http2;
    listen 443 ssl http2;
    server_name vf2;

    ssl_certificate /etc/ssl/www/example.com/example.com.pem;
    ssl_certificate_key /etc/ssl/www/example.com/example.com.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        rewrite ^/ws/(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:18765;

        proxy_http_version 1.1;
        proxy_read_timeout 360s;
        proxy_redirect off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";    #配置连接为升级连接
        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header REMOTE-HOST $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```