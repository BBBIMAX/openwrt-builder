#!/bin/bash
# OpenWrt 编译脚本
# 用法: ./build.sh <设备型号> <配置文件>

set -e

# 配置
OPENWRT_VERSION="23.05"
OPENWRT_DIR="/tmp/openwrt-build"
CONFIG_FILE="${2:-.config}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_deps() {
    log_info "检查编译依赖..."
    
    local deps=("gcc" "g++" "make" "git" "python3" "ncurses" "flex" "bison" "patch" "autoconf" " automake" "libtool")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_warn "缺少依赖: $dep"
        fi
    done
}

# 克隆源码
clone_source() {
    local device="$1"
    log_info "克隆 OpenWrt ${OPENWRT_VERSION} 源码..."
    
    if [ -d "$OPENWRT_DIR" ]; then
        log_warn "源码目录已存在，跳过克隆"
        return
    fi
    
    # 使用中国镜像
    git clone https://github.com/openwrt/openwrt.git -b "v${OPENWRT_VERSION}" "$OPENWRT_DIR" || \
    git clone https://gitee.com/mirrors/openwrt.git -b "v${OPENWRT_VERSION}" "$OPENWRT_DIR"
    
    cd "$OPENWRT_DIR"
    
    # 更新软件包 feeds
    ./scripts/feeds update -a
    ./scripts/feeds install -a
}

# 应用配置
apply_config() {
    local device="$1"
    log_info "应用配置文件: $CONFIG_FILE"
    
    cd "$OPENWRT_DIR"
    
    # 复制配置文件
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" .config
    else
        log_error "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
    
    # 更新配置
    make defconfig
}

# 开始编译
build_firmware() {
    local device="$1"
    local target_name="$2"
    
    log_info "开始编译固件 for $device..."
    log_info "这可能需要 30-60 分钟..."
    
    cd "$OPENWRT_DIR"
    
    # 并行编译 (使用所有CPU核心)
    make -j$(nproc) || make -j1 V=s
    
    log_info "编译完成!"
}

# 清理
clean() {
    log_info "清理编译目录..."
    rm -rf "$OPENWRT_DIR"
    log_info "清理完成"
}

# 显示用法
usage() {
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  build <设备> [配置]   编译固件"
    echo "  clean                清理编译目录"
    echo "  deps                 检查依赖"
    echo ""
    echo "示例:"
    echo "  $0 build x86_64 myconfig"
    echo "  $0 clean"
}

# 主程序
case "$1" in
    build)
        check_deps
        clone_source "$2"
        apply_config "$2"
        build_firmware "$2" "$3"
        ;;
    clean)
        clean
        ;;
    deps)
        check_deps
        ;;
    *)
        usage
        ;;
esac
