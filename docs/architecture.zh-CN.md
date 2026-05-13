# LabelZone 架构说明

English documentation: [`architecture.md`](architecture.md)

LabelZone 是一个私有化标注平台，包含中英文双语界面、可配置企业 OAuth2 单点登录、SQLite 持久化、本地存储、RustFS/S3 兼容对象存储、数据集导出任务和训练任务队列 API。

## 后端

- FastAPI 提供 `/api/health`、OAuth2 身份提供方发现和登录 URL 生成、存储健康检查、数据集、图片、标注、导出、训练任务等接口。
- SQLite 保存数据集、图片、标注、导出任务和训练任务。API 层通过 `SQLiteRepository` 访问数据库，只要 SQLite 文件被持久化，进程重启后数据仍然存在。
- 标注对象支持单标签分类、矩形框和优先面向实例分割的多边形。
- 训练任务当前作为队列记录持久化。后续生产 GPU Worker 可以基于同样 API 轮询或订阅任务，不需要改变前端契约。

## 数据库模型

通过 `LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3` 配置 SQLite 数据库。应用启动时自动建表：

- `datasets(id, data)`
- `images(id, dataset_id, data)`
- `annotations(image_id, id, data)`
- `exports(id, dataset_id, data)`
- `training_jobs(id, dataset_id, data)`

`data` 字段保存由 Pydantic 模型校验后的 JSON。这样可以让首次私有化部署保持简单，同时保留强校验 API 结构。

## 存储

- `LABELZONE_STORAGE_BACKEND=local` 会把文件保存到 `LABELZONE_LOCAL_STORAGE_ROOT`，返回 `local://...` URI。
- `LABELZONE_STORAGE_BACKEND=rustfs` 会启用基于 boto3 的 RustFS/S3 兼容适配器，返回 `rustfs://bucket/key` URI。
- RustFS 适配器通过 S3 `put_object` 写入上传文件和导出产物，通过 `head_object` 检查对象是否存在。

## 前端

Vue + Element Plus 前端默认中文，可切换英文。CSS 配置了支持 CJK 的字体兜底；只要运行环境安装了合适的中文字体，运行时截图不会出现乱码或方块字。

## 部署拓扑

最小化部署包含两个容器和一个数据卷：

1. `backend`：FastAPI + SQLite + 本地文件存储
2. `frontend`：Nginx 托管的 Vue 静态构建产物，并把 `/api/` 代理到后端
3. `labelzone-data`：持久化 SQLite 文件和上传产物

RustFS 部署会额外增加一个 RustFS 服务，并把后端存储变量切换为 RustFS。

## 验证

运行后端单元测试和冒烟测试：

```bash
cd backend
python -m pip install -e '.[test]'
pytest
python scripts/smoke_test.py
```

运行前端单元测试、构建和冒烟测试：

```bash
cd frontend
npm ci
npm test
npm run build
npm run smoke
```
