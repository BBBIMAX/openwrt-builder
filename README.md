# OpenWrt 在线定制编译系统

一个类似 openwrt.ai 的 OpenWrt 固件在线定制编译平台。

## 项目架构

```
openwrt-builder/
├── frontend/          # 前端 (Vue 3 + Vite)
├── backend/           # 后端 (FastAPI)
├── scripts/          # 编译脚本
├── docs/             # 文档
└── README.md
```

## 核心功能

### 1. 设备支持
- x86_64 (软路由主流)
- Rockchip (Armbian)
- MediaTek
- Qualcomm
- 更多设备支持...

### 2. 软件包分类
- **网络工具**: PassWall, OpenClash, HomeProxy, SSR-Plus
- **下载工具**: Aria2, qBittorrent, Transmission, Thunder
- **存储相关**: SMB, NFS, WebDAV, 阿里云盘
- **去广告**: AdGuardHome, adbyby-plus
- **智能家居**: HomeAssistant
- **DDNS**: 多种动态域名服务
- **内网穿透**: ZeroTier, TailScale, FRP

### 3. 主题
- Argon, Alpha, Material, NeoBird, KuCat 等

### 4. 高级配置
- 旁路由模式
- Docker 支持
- IPv6 配置
- WiFi 设置
- 端口暴露

## 技术栈

- **前端**: Vue 3 + Vite + TailwindCSS
- **后端**: FastAPI + SQLite/PostgreSQL
- **编译**: GitHub Actions + Docker
- **存储**: 本地存储 / OSS

## 快速开始

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 编译流程

1. 用户在网页选择设备型号、软件包、配置
2. 后端生成 .config 配置文件
3. 调用编译系统（GitHub Actions API）
4. 编译完成后通知用户下载

## License

MIT
