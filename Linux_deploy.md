# LinkScanner Linux 云服务器部署文档

> 版本：v1.0
> 适用系统：Ubuntu 22.04 / 24.04 LTS（Debian 系同理）
> 部署架构：单机 Nginx + Systemd + Uvicorn（前后端同源部署）
> 编写日期：2025

---

## 目录

1. [部署架构说明](#1-部署架构说明)
2. [环境要求](#2-环境要求)
3. [服务器初始化](#3-服务器初始化)
4. [代码上传](#4-代码上传)
5. [后端部署](#5-后端部署)
6. [前端修复与构建](#6-前端修复与构建)
7. [Nginx 配置](#7-nginx-配置)
8. [HTTPS 配置（可选）](#8-https-配置可选)
9. [防火墙与安全加固](#9-防火墙与安全加固)
10. [部署验证](#10-部署验证)
11. [日常运维](#11-日常运维)
12. [常见问题排查](#12-常见问题排查)
13. [附录](#13-附录)

---

## 1. 部署架构说明

### 1.1 整体架构

```
                用户浏览器
                     │
                     ▼
        ┌───────────────────────────┐
        │   Nginx (:80 / :443)      │
        │   ├─ /      → 前端静态文件  │
        │   └─ /api   → 反向代理      │
        └───────────────────────────┘
                     │
                     ▼ 127.0.0.1:8000
        ┌───────────────────────────┐
        │  FastAPI + Uvicorn        │
        │  Systemd 守护, 开机自启    │
        │  仅监听本机, 不对外暴露     │
        └───────────────────────────┘
```

### 1.2 设计要点

| 设计决策 | 理由 |
|---|---|
| 前后端**同源**部署（同一 Nginx 域名） | 彻底规避 CORS 问题，浏览器视为同源请求 |
| 后端仅监听 `127.0.0.1:8000` | 外部无法直接访问后端端口，安全性更高 |
| 前端构建产物由 Nginx 直接托管 | 静态资源性能最佳，且能正确处理 SPA 路由 |
| 使用 Systemd 而非 `nohup` / `screen` | 开机自启、崩溃自动重启、日志统一管理 |
| `dist/` 在本地/服务器构建后上传 | 服务器无需安装 Node.js，运行环境更精简 |

### 1.3 为什么不需要 Docker

本项目在线推理仅加载单个 LightGBM 模型，依赖清晰、无多服务编排需求。使用 Systemd 原生部署：
- 内存占用更低（省去 Docker daemon）
- 排障链路更短（直接 `journalctl` 看日志）
- 迁移成本可接受（仅需复制 `/opt/mudsw` 目录）

---

## 2. 环境要求

### 2.1 服务器配置

| 项目 | 最低配置 | 推荐配置 |
|---|---|---|
| CPU | 1 核 | 2 核 |
| 内存 | 2 GB | 4 GB |
| 磁盘 | 20 GB | 40 GB SSD |
| 带宽 | 1 Mbps | 3 Mbps+ |

> 在线推理仅使用 LightGBM，**无需 GPU**。

### 2.2 软件版本

| 软件 | 版本要求 | 用途 |
|---|---|---|
| Ubuntu | 22.04 LTS 或 24.04 LTS | 操作系统 |
| Python | 3.10+ | 后端运行 |
| Nginx | 1.18+ | 反向代理 + 静态文件 |
| Node.js | 18 LTS（仅构建时，可在本地执行） | 前端构建 |
| OpenSSL | 系统自带 | HTTPS 证书 |

### 2.3 部署前准备清单

- [ ] 一台已开通的云服务器（含公网 IP）
- [ ] 服务器 root 或 sudo 权限账号
- [ ] 项目源码压缩包（`mudsw.zip` 或 `mudsw.tar.gz`）
- [ ] 训练好的模型文件 `model/lgbm_best.model`
- [ ] （可选）已备案域名 + SSL 证书
- [ ] 一个 CSV 测试样例文件（含 `url` 列）

---

## 3. 服务器初始化

### 3.1 登录服务器

```bash
ssh root@<你的服务器公网IP>
# 或使用密钥
ssh -i ~/.ssh/your_key.pem root@<你的服务器公网IP>
```

### 3.2 更新系统并安装基础依赖

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    python3 python3-venv python3-pip \
    nginx \
    git curl wget unzip \
    build-essential libssl-dev \
    ufw
```

### 3.3 校验版本

```bash
python3 --version       # 应 ≥ 3.10
nginx -v                # 应 ≥ 1.18
git --version
```

### 3.4 创建部署目录

```bash
sudo mkdir -p /opt/mudsw
sudo mkdir -p /var/www/linkscanner
sudo chown -R $USER:$USER /opt/mudsw
sudo chown -R $USER:$USER /var/www/linkscanner
```

> 若使用非 root 用户部署，将 `$USER` 替换为实际用户名。

---

## 4. 代码上传

### 4.1 方式一：从 Git 仓库克隆（推荐）

```bash
cd /opt/mudsw
git clone <你的仓库地址> .
```

### 4.2 方式二：从本地上传压缩包

**本地执行：**
```bash
# 打包项目（排除无关文件）
tar --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
    --exclude='.venv' -czf mudsw.tar.gz mudsw/

# 上传
scp mudsw.tar.gz root@<服务器IP>:/opt/
```

**服务器执行：**
```bash
cd /opt
tar -xzf mudsw.tar.gz
mv mudsw/* /opt/mudsw/
rm -rf mudsw mudsw.tar.gz
```

### 4.3 目录结构确认

上传完成后，检查关键目录：

```bash
cd /opt/mudsw
ls -la
# 应看到 backend/ 和 frontend/ 两个目录

ls backend/
# 应包含：app/ model/ data/ requirements.txt 等

ls backend/model/
# 必须存在：lgbm_best.model
```

> ⚠️ **关键校验**：如果 `backend/model/lgbm_best.model` 不存在，后端启动必然失败。

---

## 5. 后端部署

### 5.1 创建 Python 虚拟环境

```bash
cd /opt/mudsw/backend
python3 -m venv .venv
source .venv/bin/activate
```

### 5.2 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **优化提示**：如果 `requirements.txt` 已分为「在线服务依赖」和「训练依赖」两部分，生产环境可**仅安装第一部分**，能显著减小依赖体积、加快部署。若使用国内服务器，可加国内镜像源：
> ```bash
> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
> ```

### 5.3 本地快速验证

在切换为 Systemd 之前，先在虚拟环境中手动启动一次，确认能正常运行：

```bash
cd /opt/mudsw/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

看到类似 `Uvicorn running on http://127.0.0.1:8000` 输出即为成功。
按 `Ctrl + C` 停止，进入下一步。

> 若启动报错「`model/lgbm_best.model` 找不到」，说明当前工作目录不在 `backend/` 下。**必须保证在 `backend/` 目录内启动**。

### 5.4 创建专用系统用户（可选但推荐）

```bash
sudo useradd -r -s /usr/sbin/nologin -d /opt/mudsw linkscanner
sudo chown -R linkscanner:linkscanner /opt/mudsw/backend
```

> 如果为了方便后续修改代码（如 `git pull`），也可以直接用你自己的用户运行，此时请把后面 Systemd 配置中的 `User=www-data` 改为你的用户名。

### 5.5 创建 Systemd 服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/linkscanner.service
```

内容如下：

```ini
[Unit]
Description=LinkScanner FastAPI Backend
Documentation=https://github.com/your/repo
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/mudsw/backend
Environment="PATH=/opt/mudsw/backend/.venv/bin"
ExecStart=/opt/mudsw/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=linkscanner

# 安全加固（可选）
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ReadWritePaths=/opt/mudsw/backend

[Install]
WantedBy=multi-user.target
```

**关键配置说明：**

| 配置项 | 说明 |
|---|---|
| `WorkingDirectory` | **必须**是 `backend/` 的绝对路径，因为代码中使用了 `model/lgbm_best.model` 等相对路径 |
| `ExecStart` | 直接指向虚拟环境中的 uvicorn，**不要**使用 `source` 激活 |
| `--host 127.0.0.1` | 只监听本机，外部无法访问 8000 端口，安全由 Nginx 兜底 |
| `--workers 2` | 根据 CPU 核数调整，推荐 `2 × CPU核数 + 1`，但要考虑内存 |
| `Restart=always` | 崩溃后自动重启 |
| `User=www-data` | 以非 root 运行，降低提权风险。请确保该用户对 `backend/` 目录有读写权限 |

### 5.6 授予目录权限

若使用 `www-data` 运行：

```bash
sudo chown -R www-data:www-data /opt/mudsw/backend
sudo chmod -R 755 /opt/mudsw/backend
```

> 注意：项目 `predict()` 流程中会写入临时文件 `detect_single_muti.csv`，因此 `backend/` 目录需要**写权限**。

### 5.7 启用并启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable linkscanner
sudo systemctl start linkscanner
sudo systemctl status linkscanner
```

看到 `Active: active (running)` 即为成功。

### 5.8 验证后端

```bash
curl -X POST http://127.0.0.1:8000/api/detect_url \
  -H "Content-Type: application/json" \
  -d '{"url":"http://www.baidu.com"}'
```

期望返回类似：

```json
{"url":"http://www.baidu.com","isMalicious":false}
```

如果报错，查看日志：

```bash
sudo journalctl -u linkscanner -n 100 --no-pager
```

---

## 6. 前端修复与构建

### 6.1 修复 UploadCSV.jsx 的硬编码地址 ⚠️ 关键步骤

这是**上线前必须修复**的问题。项目原代码在 `UploadCSV.jsx` 中硬编码了 `http://localhost:8000`，生产环境下浏览器会尝试访问用户自己电脑的 8000 端口，导致 `Failed to fetch` 或 CORS 报错。

#### 6.1.1 定位问题

```bash
cd /opt/mudsw/frontend/src/components
grep -n "localhost:8000" UploadCSV.jsx
grep -n "127.0.0.1:8000" UploadCSV.jsx
```

应看到类似：
```
12:  const response = await fetch('http://localhost:8000/api/upload_csv', {
```

#### 6.1.2 修改为相对路径

**修改前：**
```jsx
const response = await fetch('http://localhost:8000/api/upload_csv', {
  method: 'POST',
  body: formData,
});
```

**修改后：**
```jsx
const response = await fetch('/api/upload_csv', {
  method: 'POST',
  body: formData,
});
```

若使用 axios：
```jsx
// 前
await axios.post('http://localhost:8000/api/upload_csv', formData);
// 后
await axios.post('/api/upload_csv', formData);
```

#### 6.1.3 全局排查其他硬编码

```bash
cd /opt/mudsw/frontend/src
grep -rn "localhost:8000" .
grep -rn "127.0.0.1:8000" .
```

理想结果：**无任何输出**。

#### 6.1.4 检查 Vite 代理配置（开发环境用）

确认 `frontend/vite.config.js` 中 `server.proxy` 的 target 与后端实际端口一致（默认应为 `http://localhost:8000`）。生产环境走 Nginx，与此配置无关。

### 6.2 安装 Node.js（仅在服务器构建时需要）

> 推荐在**本地构建后上传 `dist/`**，服务器端可跳过此步。

```bash
# 安装 NodeSource 官方源
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 校验
node -v    # ≥ v18
npm -v
```

国内服务器加速：

```bash
npm config set registry https://registry.npmmirror.com
```

### 6.3 构建前端

```bash
cd /opt/mudsw/frontend
npm install
npm run build
```

构建完成后，产物位于 `frontend/dist/`。

### 6.4 部署静态文件

```bash
sudo rm -rf /var/www/linkscanner/*
sudo cp -r /opt/mudsw/frontend/dist/* /var/www/linkscanner/
sudo chown -R www-data:www-data /var/www/linkscanner
sudo chmod -R 755 /var/www/linkscanner
```

---

## 7. Nginx 配置

### 7.1 创建站点配置

```bash
sudo nano /etc/nginx/sites-available/linkscanner
```

内容如下：

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com;   # 替换为域名或公网IP

    # 前端静态文件根目录
    root /var/www/linkscanner;
    index index.html;

    # 访问日志
    access_log /var/log/nginx/linkscanner.access.log;
    error_log  /var/log/nginx/linkscanner.error.log;

    # 上传大小限制（CSV 可能较大）
    client_max_body_size 50M;

    # 前端 SPA 路由（React Router 刷新不 404）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存（可选，提升性能）
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 反向代理到 FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;

        # 基础转发头
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 上传/下载相关
        proxy_request_buffering off;
        proxy_buffering off;

        # 超时（批量推理耗时可能较长）
        proxy_connect_timeout 60s;
        proxy_send_timeout    300s;
        proxy_read_timeout    300s;
    }

    # （可选）暴露 Swagger 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }
}
```

### 7.2 关键配置说明

| 配置 | 作用 |
|---|---|
| `try_files $uri $uri/ /index.html` | React SPA 刷新不 404 的核心 |
| `client_max_body_size 50M` | 上传 CSV 超过默认 1M 时不会被 Nginx 拦截 |
| `proxy_pass http://127.0.0.1:8000/api/;` | **注意末尾 `/api/`**，与 location 保持后缀一致，避免路径丢失 |
| `proxy_read_timeout 300s` | 批量 CSV 推理耗时较长，避免 504 |
| 静态资源缓存 `Cache-Control` | 减少重复请求，但**部署新版本时需考虑加版本号或强制刷新** |

### 7.3 启用配置

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/linkscanner /etc/nginx/sites-enabled/

# 移除默认站点（避免冲突）
sudo rm -f /etc/nginx/sites-enabled/default

# 语法检查
sudo nginx -t

# 重载
sudo systemctl reload nginx
```

若输出 `syntax is ok` 和 `test is successful`，说明配置无误。

---

## 8. HTTPS 配置（可选）

### 8.1 前置条件

- 已备案域名
- 域名 A 记录已解析到服务器公网 IP

### 8.2 使用 Certbot 申请免费证书

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

按提示操作，Certbot 会自动：
1. 校验域名所有权
2. 申请 Let's Encrypt 证书
3. 修改 Nginx 配置，开启 443 端口并做 80→443 跳转
4. 注册自动续期定时任务

### 8.3 验证自动续期

```bash
sudo certbot renew --dry-run
```

### 8.4 手动指定证书（如使用商业证书）

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate     /etc/nginx/ssl/your-domain.crt;
    ssl_certificate_key /etc/nginx/ssl/your-domain.key;

    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # …… 其余 location 配置同 7.1
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}
```

---

## 9. 防火墙与安全加固

### 9.1 配置 UFW 防火墙

```bash
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS（若启用）
sudo ufw enable
sudo ufw status
```

> ⚠️ **不要开放 8000 端口**，Uvicorn 只监听 127.0.0.1，外网本就无法访问，但关闭更保险。

### 9.2 收紧后端 CORS 配置

虽然同源部署下 CORS 不会触发，但仍建议把 `app/main.py` 中的 `allow_origins=["*"]` 改为具体域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

修改后重启后端：

```bash
sudo systemctl restart linkscanner
```

### 9.3 SSH 安全建议

- 禁用 root 密码登录，改用密钥
- 修改 `/etc/ssh/sshd_config` 中 `PermitRootLogin prohibit-password`
- 可选：安装 `fail2ban` 防御暴力破解

```bash
sudo apt install -y fail2ban
sudo systemctl enable --now fail2ban
```

### 9.4 系统更新

```bash
# 安装自动安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 10. 部署验证

### 10.1 后端独立验证

```bash
# 本机调用（绕过 Nginx）
curl -X POST http://127.0.0.1:8000/api/detect_url \
  -H "Content-Type: application/json" \
  -d '{"url":"http://www.baidu.com"}'
```

### 10.2 通过 Nginx 验证

```bash
# 单条 URL
curl -X POST http://your-domain.com/api/detect_url \
  -H "Content-Type: application/json" \
  -d '{"url":"http://www.baidu.com"}'

# CSV 上传（构造测试文件）
echo "url" > /tmp/test.csv
echo "http://www.baidu.com" >> /tmp/test.csv
echo "http://malicious-example.xyz/evil" >> /tmp/test.csv
curl -X POST http://your-domain.com/api/upload_csv \
  -F "file=@/tmp/test.csv" \
  -o /tmp/results.csv
cat /tmp/results.csv
```

期望输出：
```
URL,Malicious
http://www.baidu.com,No
http://malicious-example.xyz/evil,Yes
```

### 10.3 浏览器端验证

1. 打开 `http://your-domain.com`（或 `https://`）
2. **单条检测**：输入 `www.baidu.com` → 点击 Analyze URL → 应显示 `Safe`
3. **CSV 上传**：上传含 `url` 列的 CSV → 应自动下载 `results.csv`
4. **F12 控制台检查**：
   - 无红色 CORS 报错
   - `Network` 面板中 `upload_csv` 请求 URL 为 `http://your-domain.com/api/upload_csv`（**无 :8000 端口**）

### 10.4 上线检查清单

- [ ] `systemctl status linkscanner` 显示 `active (running)`
- [ ] `systemctl is-enabled linkscanner` 显示 `enabled`
- [ ] `curl http://127.0.0.1:8000/api/detect_url` 返回正常
- [ ] 浏览器访问域名显示前端页面
- [ ] 单条 URL 检测返回结果
- [ ] CSV 上传成功并下载 `results.csv`
- [ ] F12 控制台无 CORS 错误
- [ ] `sudo ufw status` 仅开放 22/80/443
- [ ] 重启服务器后服务能自动拉起（`sudo reboot` 后重新验证）

---

## 11. 日常运维

### 11.1 服务管理命令

```bash
# 查看状态
sudo systemctl status linkscanner

# 重启
sudo systemctl restart linkscanner

# 停止 / 启动
sudo systemctl stop linkscanner
sudo systemctl start linkscanner

# 查看日志（实时）
sudo journalctl -u linkscanner -f

# 查看最近 200 行
sudo journalctl -u linkscanner -n 200 --no-pager

# 查看今日日志
sudo journalctl -u linkscanner --since today
```

### 11.2 Nginx 管理命令

```bash
# 语法检查
sudo nginx -t

# 重载（不中断连接）
sudo systemctl reload nginx

# 重启
sudo systemctl restart nginx

# 日志
sudo tail -f /var/log/nginx/linkscanner.access.log
sudo tail -f /var/log/nginx/linkscanner.error.log
```

### 11.3 更新后端代码

```bash
cd /opt/mudsw
sudo git pull

cd backend
source .venv/bin/activate
pip install -r requirements.txt   # 依赖有变化时执行

sudo systemctl restart linkscanner
sudo systemctl status linkscanner
```

### 11.4 更新前端代码

```bash
cd /opt/mudsw/frontend
git pull
npm install                       # 依赖有变化时执行
npm run build

sudo rm -rf /var/www/linkscanner/*
sudo cp -r dist/* /var/www/linkscanner/
sudo chown -R www-data:www-data /var/www/linkscanner

# 无需重启 Nginx，但清一下缓存
# 用户侧建议 Ctrl+F5 强刷
```

### 11.5 更换模型文件

```bash
# 上传新模型
scp lgbm_best.model root@server:/tmp/

# 服务器端替换
sudo mv /tmp/lgbm_best.model /opt/mudsw/backend/model/lgbm_best.model
sudo chown www-data:www-data /opt/mudsw/backend/model/lgbm_best.model
sudo systemctl restart linkscanner
```

### 11.6 日志轮转

Systemd journal 默认按大小自动轮转，如需限制：

```bash
sudo nano /etc/systemd/journald.conf
# 设置：
# SystemMaxUse=500M
# SystemMaxFileSize=50M

sudo systemctl restart systemd-journald
```

Nginx 日志轮转由 `/etc/logrotate.d/nginx` 自动管理，无需额外配置。

### 11.7 备份策略

**必备份内容：**

| 路径 | 说明 |
|---|---|
| `/opt/mudsw/backend/model/` | 训练好的模型文件 |
| `/opt/mudsw/backend/app/` | 应用代码 |
| `/opt/mudsw/backend/data/` | 词库等数据 |
| `/etc/nginx/sites-available/linkscanner` | Nginx 配置 |
| `/etc/systemd/system/linkscanner.service` | Systemd 配置 |

**备份示例：**
```bash
tar -czf /backup/linkscanner-$(date +%Y%m%d).tar.gz \
    /opt/mudsw/backend/model \
    /opt/mudsw/backend/app \
    /opt/mudsw/backend/data \
    /etc/nginx/sites-available/linkscanner \
    /etc/systemd/system/linkscanner.service
```

---

## 12. 常见问题排查

### 12.1 后端启动失败：模型文件找不到

**症状：**
```
FileNotFoundError: [Errno 2] No such file or directory: 'model/lgbm_best.model'
```

**原因：** Systemd 中 `WorkingDirectory` 配置错误，或文件确实缺失。

**排查：**
```bash
# 检查文件是否存在
ls -la /opt/mudsw/backend/model/lgbm_best.model

# 检查 Systemd 配置
grep WorkingDirectory /etc/systemd/system/linkscanner.service
```

**修复：** 确保 `WorkingDirectory=/opt/mudsw/backend`（绝对路径）。

### 12.2 前端报 `Failed to fetch` 或 CORS 错误

**症状：** 控制台报 `Cross-Origin Request Blocked... Access-Control-Allow-Origin 缺少标头`。

**原因：** `UploadCSV.jsx` 或其它组件仍有硬编码 `http://localhost:8000` 或 `http://<公网IP>:8000`。

**排查：**
```bash
cd /opt/mudsw/frontend/src
grep -rn "localhost:8000" .
grep -rn ":8000" .
```

**修复：** 改为相对路径 `/api/upload_csv`，**重新 `npm run build` 并复制 dist**。
验证：F12 → Network → 请求 URL 应不含端口号。

### 12.3 上传 CSV 时 Nginx 返回 413

**症状：** `413 Request Entity Too Large`

**修复：** 在 Nginx 站点配置中加大：
```nginx
client_max_body_size 50M;
```
然后 `sudo systemctl reload nginx`。

### 12.4 批量 CSV 推理超时 504

**症状：** 大批量 CSV 上传时 Nginx 返回 504 Gateway Timeout。

**修复：** 加大代理超时：
```nginx
proxy_read_timeout 300s;
proxy_send_timeout 300s;
```
或在前端提示用户拆分文件上传。

### 12.5 后端 502 Bad Gateway

**原因：** Uvicorn 未运行 / 崩溃 / 端口冲突。

**排查：**
```bash
sudo systemctl status linkscanner
sudo journalctl -u linkscanner -n 100 --no-pager
sudo ss -tulnp | grep 8000
```

**修复：** 查看日志定位具体错误，重启服务。

### 12.6 上传 CSV 后返回的内容是 HTML 而不是 CSV

**原因：** Nginx 的 `/api/` 路径匹配失败，请求被 `location /` 捕获返回了 `index.html`。

**排查：** 检查 Nginx 站点配置中 `location /api/` 段是否存在且拼写正确。

**修复：** 确保同时存在 `location /` 和 `location /api/`，且 `/api/` 的 `proxy_pass` 结尾有 `/api/`。

### 12.7 临时文件写入失败（Permission denied）

**症状：** 日志中出现写 `detect_single_muti.csv` 失败。

**原因：** Systemd 中运行用户对 `backend/` 目录无写权限。

**修复：**
```bash
sudo chown -R www-data:www-data /opt/mudsw/backend
sudo chmod -R u+w /opt/mudsw/backend
sudo systemctl restart linkscanner
```

### 12.8 重启服务器后服务未启动

**排查：**
```bash
systemctl is-enabled linkscanner   # 应输出 enabled
```

**修复：**
```bash
sudo systemctl enable linkscanner
```

### 12.9 端口 80 被占用

**排查：**
```bash
sudo ss -tulnp | grep ':80'
```

**常见占用者：** Apache、默认 Nginx 站点。停止相关服务或删除默认站点：
```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl reload nginx
```

---

## 13. 附录

### 13.1 关键文件路径速查

| 内容 | 路径 |
|---|---|
| 项目根目录 | `/opt/mudsw` |
| 后端代码 | `/opt/mudsw/backend/app` |
| 模型文件 | `/opt/mudsw/backend/model/lgbm_best.model` |
| 虚拟环境 | `/opt/mudsw/backend/.venv` |
| 前端源码 | `/opt/mudsw/frontend/src` |
| 前端构建产物 | `/opt/mudsw/frontend/dist` |
| 前端部署目录 | `/var/www/linkscanner` |
| Systemd 服务 | `/etc/systemd/system/linkscanner.service` |
| Nginx 配置 | `/etc/nginx/sites-available/linkscanner` |
| Nginx 访问日志 | `/var/log/nginx/linkscanner.access.log` |
| Nginx 错误日志 | `/var/log/nginx/linkscanner.error.log` |
| 后端日志 | `journalctl -u linkscanner` |

### 13.2 一键健康检查脚本

创建 `/opt/mudsw/healthcheck.sh`：

```bash
#!/bin/bash

echo "===== 系统时间 ====="
date

echo ""
echo "===== Systemd 服务状态 ====="
systemctl is-active linkscanner && systemctl is-enabled linkscanner

echo ""
echo "===== 端口监听 ====="
ss -tulnp | grep -E ':80|:443|:8000'

echo ""
echo "===== 后端本地探活 ====="
curl -s -X POST http://127.0.0.1:8000/api/detect_url \
  -H "Content-Type: application/json" \
  -d '{"url":"http://www.baidu.com"}' \
  -w "\nHTTP %{http_code}\n"

echo ""
echo "===== 通过 Nginx 探活 ====="
curl -s -o /dev/null -w "首页 HTTP %{http_code}\n" http://localhost/

echo ""
echo "===== Nginx 配置检查 ====="
sudo nginx -t

echo ""
echo "===== 磁盘使用 ====="
df -h /opt /var

echo ""
echo "===== 内存使用 ====="
free -h

echo ""
echo "===== 服务最近 20 条日志 ====="
sudo journalctl -u linkscanner -n 20 --no-pager
```

赋予执行权限：
```bash
chmod +x /opt/mudsw/healthcheck.sh
/opt/mudsw/healthcheck.sh
```

### 13.3 快速重启全部服务

```bash
sudo systemctl restart linkscanner
sudo systemctl reload nginx
```

### 13.4 完整部署流程（TL;DR）

```bash
# 1. 初始化
sudo apt update && sudo apt install -y python3 python3-venv nginx git ufw

# 2. 上传代码到 /opt/mudsw

# 3. 后端
cd /opt/mudsw/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. 修复 UploadCSV.jsx 中的硬编码地址

# 5. 前端构建
cd /opt/mudsw/frontend
npm install && npm run build
sudo cp -r dist/* /var/www/linkscanner/

# 6. 配置 Systemd 服务
sudo nano /etc/systemd/system/linkscanner.service
sudo systemctl daemon-reload && sudo systemctl enable --now linkscanner

# 7. 配置 Nginx
sudo nano /etc/nginx/sites-available/linkscanner
sudo ln -s /etc/nginx/sites-available/linkscanner /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 8. 防火墙
sudo ufw allow 22,80,443/tcp && sudo ufw enable

# 9. 验证
curl http://<你的域名或IP>/api/detect_url \
  -X POST -H "Content-Type: application/json" \
  -d '{"url":"http://www.baidu.com"}'
```

### 13.5 版本记录

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2025 | 初版，含前后端同源部署、Systemd 守护、Nginx 反代、HTTPS 可选配置 |

---

**文档结束**

如有部署疑问，请先按第 12 章「常见问题排查」逐项检查，90% 的问题都在其中。若仍无法解决，请提供以下信息便于定位：

1. `sudo systemctl status linkscanner` 的完整输出
2. `sudo journalctl -u linkscanner -n 100 --no-pager` 的完整输出
3. 浏览器 F12 → Network 面板中失败请求的截图（含请求 URL、状态码、响应头）