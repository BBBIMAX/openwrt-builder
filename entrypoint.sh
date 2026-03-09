#!/bin/bash
# Docker 启动脚本

set -e

cd /openwrt

# 如果需要安装额外软件包
if [ -f /tmp/packages.txt ]; then
    echo "安装额外软件包..."
    while IFS= read -r pkg; do
        [ -z "$pkg" ] && continue
        ./scripts/feeds install -a "$pkg" || true
    done < /tmp/packages.txt
fi

# 保持容器运行或执行编译
if [ "$1" = "shell" ]; then
    exec /bin/bash
elif [ "$1" = "build" ]; then
    shift
    echo "开始编译，参数: $@"
    make -j$(nproc) "$@"
else
    echo "用法:"
    echo "  docker run -it openwrt-builder shell   # 进入交互式shell"
    echo "  docker run openwrt-builder build      # 开始编译"
    exec /bin/bash
fi
