FROM debian:stable-slim

RUN set -eux; \
    \
    apt update; \
    apt install nginx -y; \
    apt install python3 -y; \
    apt install python3-pip -y; \
    wget -O \root https://github.com/v2ray/v2ray-core/releases/download/v4.27.0/v2ray-linux-64.zip; \