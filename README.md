## 概要
### 見た目
![最新の投稿](https://github.com/namoron/Diary/assets/105638744/6c9b44e7-96fc-47bc-8617-cb16633f037a)
最新の投稿

![full](https://github.com/namoron/Diary/assets/105638744/e6b54fb7-9ef6-4b7c-aa47-5e8a3010cd1c)
全体の投稿

![edit](https://github.com/namoron/Diary/assets/105638744/11cb321e-1e58-4236-bcd6-a9be1fff8b2b)
編集画面

![login](https://github.com/namoron/Diary/assets/105638744/748100c2-aff4-409a-95cc-d4c7cd332bdd)
ログイン画面



## 立ち上げ方法
nginx をセットアップ
### /etc/nginx/nginx.conf 
```nginx
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;


server {
    client_max_body_size 20M;
    listen 8080;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:9876/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;
    }
}

}
````
sudo service nginx start で起動もしくはインストール

sudo docker compose up --build でアプリを起動

