# LabelZone Frontend

中文文档：[`README.zh-CN.md`](README.zh-CN.md)

The frontend is a Vue 3 + TypeScript + Element Plus application. It defaults to Chinese, can switch to English at runtime, and uses CJK-capable font fallbacks so screenshots preserve Chinese text when the host has CJK fonts installed.

## Commands

```bash
npm ci
npm run dev
npm test
npm run build
npm run smoke
```

## Docker build

From the repository root:

```bash
docker build -f frontend/Dockerfile -t labelzone-frontend:local .
docker run --rm -p 8080:80 labelzone-frontend:local
```

The Nginx configuration proxies `/api/` requests to the `backend` service in Docker Compose.
