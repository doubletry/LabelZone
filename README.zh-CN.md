# LabelZone 标注平台

English documentation: [`README.md`](README.md)

LabelZone 是面向企业私有化环境的中英文双语图片标注平台。当前版本包含 FastAPI 后端、Vue + Element Plus 前端、SQLite 数据库持久化、本地文件存储，以及 RustFS/S3 兼容对象存储适配器。

## 功能

- 企业 OAuth2/OIDC 单点登录配置入口
- 中文/英文双语界面
- 通过 `LABELZONE_DATABASE_URL` 接入 SQLite 数据库
- 默认本地存储，可切换到 RustFS 兼容对象存储
- 数据集、图片、标注、导出、训练任务 API
- 单标签分类校验
- 矩形框和多边形实例分割标注结构
- COCO/YOLO 风格导出任务接口
- 可与独立 GPU 训练服务对接的训练队列接口

## 环境要求

- 后端使用 Python 3.12+
- 前端使用 Node.js 24+
- 容器部署需要 Docker 和 Compose

## 快速启动

### 后端

```bash
cd backend
python -m pip install -e '.[test]'
LABELZONE_DATABASE_URL=sqlite:////tmp/labelzone.sqlite3 \
LABELZONE_LOCAL_STORAGE_ROOT=/tmp/labelzone-files \
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm ci
npm run dev
```

### 最小化 Docker 部署

```bash
docker compose up --build -d
curl 'http://localhost:8000/api/health?locale=zh-CN'
# 浏览器打开 http://localhost:8080
```

该命令会启动：

- 后端：`http://localhost:8000`
- 前端：`http://localhost:8080`
- Docker 卷 `labelzone-data`，保存 `/data/db/labelzone.sqlite3` 和本地上传文件

### 使用 RustFS 的 Docker 部署

```bash
export RUSTFS_IMAGE=rustfs/rustfs:<pinned-version>
export LABELZONE_RUSTFS_ACCESS_KEY=<access-key>
export LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
export LABELZONE_RUSTFS_BUCKET=labelzone
docker compose -f docker-compose.yml -f docker-compose.rustfs.yml up --build -d
```

生产环境上线前，请创建专用 RustFS 凭据，通过环境变量或密钥管理系统注入，并检查桶策略和网络暴露方式。

## 数据库接入

后端当前支持 SQLite 数据库 URL：

```bash
LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3
```

应用启动时会自动创建数据表，用于保存数据集、图片、标注、导出任务和训练任务。Docker 部署时请持久化 `/data/db`，并定期备份 SQLite 文件。

## RustFS 接入

设置以下变量即可使用 RustFS/S3 兼容对象存储：

```bash
LABELZONE_STORAGE_BACKEND=rustfs
LABELZONE_RUSTFS_ENDPOINT=http://rustfs:9000
LABELZONE_RUSTFS_BUCKET=labelzone
LABELZONE_RUSTFS_ACCESS_KEY=labelzone
LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
LABELZONE_RUSTFS_SECURE=false
```

适配器会通过 S3 `put_object` 写入上传图片和导出文件，并将返回 URI 保存为 `rustfs://bucket/key`。

## 测试和冒烟测试

```bash
cd backend && pytest && python scripts/smoke_test.py
cd frontend && npm test && npm run build && npm run smoke
```

## 更多文档

- [`docs/architecture.md`](docs/architecture.md) / [`docs/architecture.zh-CN.md`](docs/architecture.zh-CN.md)
- [`docs/deployment.md`](docs/deployment.md) / [`docs/deployment.zh-CN.md`](docs/deployment.zh-CN.md)
