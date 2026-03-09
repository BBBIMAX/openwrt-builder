# OpenWrt 在线编译系统 - 部署指南

## 方式一: Docker Compose 部署 (推荐)

```bash
# 克隆项目
git clone https://github.com/your-repo/openwrt-builder.git
cd openwrt-builder

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 方式二: 本地开发

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API 地址: http://localhost:8000

## 方式三: 云端编译 (GitHub Actions)

1. 复制 `.github/workflows/build.yml` 到你的 GitHub 仓库
2. 推送代码到 GitHub
3. 在 Actions 页面手动触发 workflow

## 功能说明

### 支持的设备
- x86_64 (主流软路由)
- Rockchip (开发板)
- MediaTek (部分路由器)
- Qualcomm (部分路由器)

### 支持的软件包
- 代理: PassWall, OpenClash, HomeProxy, SSR-Plus, v2rayA, ZeroTier, TailScale
- 下载: Aria2, qBittorrent, Transmission, Thunder
- 存储: Samba, WebDAV, 阿里云盘, Rclone
- 去广告: AdGuardHome, Adbyby, SmartDNS
- 系统: Web终端, Netdata, 定时重启, 网络唤醒

### 主题
- Argon, Material, KuCat, Dark 等

## 目录结构

```
openwrt-builder/
├── frontend/          # Vue 3 前端
│   ├── src/           # 源代码
│   └── package.json   # 依赖
├── backend/           # FastAPI 后端
│   ├── main.py        # 主程序
│   └── requirements.txt
├── scripts/           # 编译脚本
├── .github/           # GitHub Actions
├── docs/              # 文档
└── docker-compose.yml
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/build | 创建编译任务 |
| GET | /api/status/{task_id} | 获取编译状态 |
| GET | /api/tasks | 任务列表 |
| GET | /api/devices | 支持的设备 |
| GET | /api/packages | 可选软件包 |

## 注意事项

1. 首次编译需要下载源码，约 500MB
2. 编译时间约 30-60 分钟
3. 需要至少 20GB 磁盘空间
4. 建议使用 SSD 以加快编译速度
