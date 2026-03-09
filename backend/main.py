"""
OpenWrt 固件编译后端
基于 FastAPI
"""
import os
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ============== 配置 ==============
DATABASE_URL = "sqlite:///./firmware.db"
FIRMWARE_DIR = Path("./firmwares")
FIRMWARE_DIR.mkdir(exist_ok=True)

# ============== 数据库 ==============
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BuildTask(Base):
    __tablename__ = "build_tasks"
    
    id = Column(String, primary_key=True)
    device = Column(String)
    device_model = Column(String)
    packages = Column(Text)
    config = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    logs = Column(Text, default="")
    firmware_url = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# ============== 数据模型 ==============
class BuildRequest(BaseModel):
    device: str
    deviceModel: str
    selectedPackages: List[str]
    customPackages: str = ""
    removePackages: str = ""
    proxy: str = ""
    luciPort: str = "80"
    luciUser: str = "root"
    luciPassword: str
    theme: str = "argon"
    kernelVersion: str = "6.6"
    enableDocker: bool = False
    enableIPv6: bool = False
    enableWiFi: bool = False
    ssid: str = "OpenWrt"
    wifiPassword: str = ""
    bypassMode: bool = False
    bypassGateway: str = ""
    bypassDNS: str = ""
    pppoeEnabled: bool = False
    pppoeUser: str = ""
    pppoePassword: str = ""
    hostname: str = "OpenWrt"
    rootSize: str = "512"
    imageType: str = "efi"
    swapEth0: bool = False
    makeEml: bool = False

class BuildResponse(BaseModel):
    taskId: str
    success: bool
    message: str = ""

# ============== 应用 ==============
app = FastAPI(title="OpenWrt Builder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 辅助函数 ==============
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_config(form: BuildRequest) -> str:
    """生成 OpenWrt .config 配置文件"""
    config_lines = [
        "# OpenWrt Configuration",
        f"CONFIG_TARGET_{form.device.upper()}=y",
        f"CONFIG_TARGET_{form.device.upper()}_DEVICE_{form.deviceModel.replace(' ', '_').replace('-', '_')}=y",
        "# LuCI",
        "CONFIG_PACKAGE_luci=y",
    ]
    
    # 添加软件包
    for pkg in form.selectedPackages:
        if pkg.startswith('-'):
            config_lines.append(f"# CONFIG_PACKAGE_{pkg[1:]} is not set")
        else:
            config_lines.append(f"CONFIG_PACKAGE_{pkg}=y")
    
    # 主题
    config_lines.append(f"CONFIG_PACKAGE_luci-theme-{form.theme}=y")
    
    # Docker
    if form.enableDocker:
        config_lines.extend([
            "CONFIG_PACKAGE_docker=y",
            "CONFIG_PACKAGE_dockerd=y",
            "CONFIG_PACKAGE_luci-app-docker=y",
        ])
    
    # IPv6
    if form.enableIPv6:
        config_lines.append("CONFIG_IPV6=y")
    
    # WiFi
    if form.enableWiFi:
        config_lines.extend([
            "CONFIG_PACKAGE_kmod-mac80211=y",
            "CONFIG_PACKAGE_wpad-openssl=y",
        ])
    
    return "\n".join(config_lines)

async def run_build(task_id: str, config: str):
    """执行编译任务"""
    db = SessionLocal()
    try:
        task = db.query(BuildTask).filter(BuildTask.id == task_id).first()
        if not task:
            return
        
        # 更新状态
        task.status = "building"
        task.logs = "🚀 开始编译...\n"
        db.commit()
        
        # 模拟编译过程（实际应该调用 GitHub Actions 或本地编译）
        logs = []
        steps = [
            "📦 拉取 OpenWrt 源码...",
            "🔧 应用配置文件...",
            "📥 下载软件包...",
            "🛠️ 编译内核...",
            "🔨 编译软件包...",
            "📦 生成固件镜像...",
            "✅ 编译完成!",
        ]
        
        for i, step in enumerate(steps):
            await asyncio.sleep(2)  # 模拟编译时间
            task.logs += f"{step}\n"
            db.commit()
        
        # 生成假固件URL（实际应该返回真实URL）
        task.firmware_url = f"/api/download/{task_id}/openwrt-x86-64-generic-squashfs-combined-efi.img.gz"
        task.status = "completed"
        task.completed_at = datetime.now()
        db.commit()
        
    except Exception as e:
        task.status = "failed"
        task.logs += f"\n❌ 编译失败: {str(e)}"
        db.commit()
    finally:
        db.close()

# ============== API 路由 ==============
@app.get("/")
async def root():
    return {"message": "OpenWrt Builder API", "version": "1.0.0"}

@app.post("/api/build", response_model=BuildResponse)
async def create_build_task(
    request: BuildRequest,
    background_tasks: BackgroundTasks,
    db = None
):
    """创建新的编译任务"""
    task_id = str(uuid.uuid4())[:8]
    
    # 创建任务记录
    db = SessionLocal()
    try:
        config = generate_config(request)
        
        task = BuildTask(
            id=task_id,
            device=request.device,
            device_model=request.deviceModel,
            packages=json.dumps(request.selectedPackages),
            config=config,
            status="pending"
        )
        db.add(task)
        db.commit()
        
        # 启动后台编译
        background_tasks.add_task(run_build, task_id, config)
        
        return BuildResponse(
            taskId=task_id,
            success=True,
            message="编译任务已创建"
        )
    finally:
        db.close()

@app.get("/api/status/{task_id}")
async def get_build_status(task_id: str):
    """获取编译状态"""
    db = SessionLocal()
    try:
        task = db.query(BuildTask).filter(BuildTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "taskId": task.id,
            "status": task.status,
            "logs": task.logs,
            "firmware": {
                "efi": task.firmware_url,
                "legacy": task.firmware_url
            } if task.firmware_url else None,
            "createdAt": task.created_at.isoformat() if task.created_at else None,
            "completedAt": task.completed_at.isoformat() if task.completed_at else None
        }
    finally:
        db.close()

@app.get("/api/tasks")
async def list_tasks(limit: int = 10):
    """列出最近的编译任务"""
    db = SessionLocal()
    try:
        tasks = db.query(BuildTask).order_by(
            BuildTask.created_at.desc()
        ).limit(limit).all()
        
        return {
            "tasks": [
                {
                    "id": t.id,
                    "device": t.device,
                    "deviceModel": t.device_model,
                    "status": t.status,
                    "createdAt": t.created_at.isoformat() if t.created_at else None
                }
                for t in tasks
            ]
        }
    finally:
        db.close()

@app.get("/api/devices")
async def list_devices():
    """获取支持的设备列表"""
    return {
        "devices": [
            {
                "id": "x86_64",
                "name": "x86_64 软路由",
                "models": ["Generic x86/64", "ROCK Pi S", "NUC"]
            },
            {
                "id": "rockchip",
                "name": "Rockchip",
                "models": ["Rock Pi 4C", "NanoPi R2S", "NanoPi R4S", "OrangePi 5"]
            },
            {
                "id": "mediatek",
                "name": "MediaTek",
                "models": ["Xiaomi AX3600", "Xiaomi AX1800", "Redmi AX6"]
            }
        ]
    }

@app.get("/api/packages")
async def list_packages():
    """获取可选的软件包列表"""
    return {
        "packages": {
            "network": [
                {"id": "luci-app-passwall", "name": "PassWall"},
                {"id": "luci-app-openclash", "name": "OpenClash"},
                {"id": "luci-app-homeproxy", "name": "HomeProxy"},
                {"id": "luci-app-ssr-plus", "name": "SSR-Plus"},
                {"id": "luci-app-v2rayA", "name": "v2rayA"},
                {"id": "luci-app-zerotier", "name": "ZeroTier"},
                {"id": "luci-app-frpc", "name": "FRP"}
            ],
            "download": [
                {"id": "luci-app-aria2", "name": "Aria2"},
                {"id": "luci-app-qbittorrent", "name": "qBittorrent"},
                {"id": "luci-app-transmission", "name": "Transmission"},
                {"id": "luci-app-thunder", "name": "Thunder"}
            ],
            "storage": [
                {"id": "luci-app-samba4", "name": "Samba"},
                {"id": "luci-app-webdav", "name": "WebDAV"},
                {"id": "luci-app-aliyundrive-webdav", "name": "阿里云盘"},
                {"id": "luci-app-rclone", "name": "Rclone"}
            ],
            "adblock": [
                {"id": "luci-app-adguardhome", "name": "AdGuardHome"},
                {"id": "luci-app-adbyby-plus", "name": "Adbyby"},
                {"id": "luci-app-smartdns", "name": "SmartDNS"},
                {"id": "luci-app-mosdns", "name": "MosDNS"}
            ],
            "system": [
                {"id": "luci-app-ttyd", "name": "Web终端"},
                {"id": "luci-app-netdata", "name": "Netdata"},
                {"id": "luci-app-timedreboot", "name": "定时重启"},
                {"id": "luci-app-wol", "name": "网络唤醒"},
                {"id": "luci-app-ddns", "name": "DDNS"},
                {"id": "luci-app-diskman", "name": "磁盘管理"}
            ],
            "theme": [
                {"id": "luci-theme-argon", "name": "Argon"},
                {"id": "luci-theme-material", "name": "Material"},
                {"id": "luci-theme-argon-mod", "name": "Argon增强"},
                {"id": "luci-theme-kucat", "name": "KuCat"},
                {"id": "luci-theme-darkmatter", "name": "Dark"}
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
