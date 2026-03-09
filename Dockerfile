FROM ubuntu:22.04

LABEL maintainer="OpenWrt Builder"
LABEL description="OpenWrt 编译环境"

# 设置环境
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 安装编译依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    libncurses5-dev \
    libncursesw5-dev \
    libssl-dev \
    python3 \
    python3-pip \
    python3-venv \
    flex \
    bison \
    patch \
    autoconf \
    automake \
    libtool \
    pkg-config \
    gawk \
    gettext \
    unzip \
    xz-utils \
    rsync \
    file \
    qemu-utils \
    subversion \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /openwrt

# 克隆 OpenWrt 源码
RUN git clone --depth 1 --branch v23.05 https://github.com/openwrt/openwrt.git . || \
    git clone --depth 1 --branch v23.05 https://gitee.com/mirrors/openwrt.git .

# 初始化和更新 feeds
RUN ./scripts/feeds update -a

# 暴露端口
EXPOSE 8080

# 启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
