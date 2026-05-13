# LabelZone 部署指南

English documentation: [`deployment.md`](deployment.md)

本文说明最小化部署、数据库接入、RustFS 接入、Docker 镜像编译部署和运行验证步骤。

## 1. 不使用 Docker 的最小化本地部署

后端：

```bash
cd backend
python -m pip install -e '.[test]'
LABELZONE_DATABASE_URL=sqlite:////tmp/labelzone/labelzone.sqlite3 \
LABELZONE_LOCAL_STORAGE_ROOT=/tmp/labelzone/files \
LABELZONE_STORAGE_BACKEND=local \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 5173
```

验证：

```bash
curl 'http://localhost:8000/api/health?locale=zh-CN'
curl 'http://localhost:8000/api/storage/health?locale=zh-CN'
```

## 2. 最小化 Docker Compose 部署

```bash
docker compose up --build -d
docker compose ps
curl 'http://localhost:8000/api/health?locale=zh-CN'
```

浏览器打开 `http://localhost:8080` 使用界面。后端 SQLite 文件位于 `/data/db/labelzone.sqlite3`，本地文件位于 `/data/files`，二者都保存在 `labelzone-data` Docker 卷中。

## 3. 手动编译 Docker 镜像

```bash
docker build -f backend/Dockerfile -t labelzone-backend:local .
docker build -f frontend/Dockerfile -t labelzone-frontend:local .
```

手动运行：

```bash
docker network create labelzone || true
docker volume create labelzone-data

docker run -d --name labelzone-backend --network labelzone \
  -p 8000:8000 \
  -v labelzone-data:/data \
  -e LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3 \
  -e LABELZONE_LOCAL_STORAGE_ROOT=/data/files \
  -e LABELZONE_STORAGE_BACKEND=local \
  labelzone-backend:local

docker run -d --name labelzone-frontend --network labelzone \
  -p 8080:80 \
  labelzone-frontend:local
```

## 4. 数据库接入

设置 SQLite URL：

```bash
LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3
```

运维注意事项：

- 持久化 SQLite 文件所在目录。
- 升级前备份 SQLite 文件。
- 做文件系统复制时，先停止后端或使用 SQLite 安全备份工具。
- 应用启动时会自动创建缺失的数据表。

## 5. RustFS 接入

使用 RustFS Compose 覆盖文件：

```bash
export LABELZONE_RUSTFS_ACCESS_KEY=<access-key>
export LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
export LABELZONE_RUSTFS_BUCKET=labelzone
docker compose -f docker-compose.yml -f docker-compose.rustfs.yml up --build -d
```

也可以接入已有 RustFS 服务：

```bash
LABELZONE_STORAGE_BACKEND=rustfs
LABELZONE_RUSTFS_ENDPOINT=http://rustfs.example.internal:9000
LABELZONE_RUSTFS_BUCKET=labelzone
LABELZONE_RUSTFS_ACCESS_KEY=<access-key>
LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
LABELZONE_RUSTFS_SECURE=false
```

生产切流前请先准备 RustFS：

1. 创建 `LABELZONE_RUSTFS_BUCKET` 指定的桶。
2. 创建仅允许读写该桶的服务账号。
3. 将凭据保存到密钥管理系统，不要提交到源码仓库。
4. 通过 `/api/storage/health` 检查存储状态。
5. 上传一张小测试图并创建导出，确认产物 URI 为 `rustfs://...`。

## 6. 离线/私有化部署清单

- 编译并保存镜像：`docker save labelzone-backend:local labelzone-frontend:local -o labelzone-images.tar`。
- 如果部署主机不能访问互联网，请提前镜像 Python wheels 和 npm packages。
- 提前拉取或镜像 `docker-compose.rustfs.yml` 使用的 RustFS 镜像。
- 为 `/data/db`、`/data/files` 和 RustFS 数据目录挂载持久化卷。
- 通过兼容 pydantic-settings 嵌套环境变量的 `LABELZONE_OAUTH2_PROVIDERS` 配置 OAuth2 身份提供方。

## 7. 验证命令

```bash
cd backend && pytest && python scripts/smoke_test.py
cd frontend && npm test && npm run build && npm run smoke
curl 'http://localhost:8000/api/health?locale=zh-CN'
curl 'http://localhost:8000/api/storage/health?locale=zh-CN'
```
