# LabelZone 前端

English documentation: [`README.md`](README.md)

前端使用 Vue 3、TypeScript 和 Element Plus。界面默认中文，运行时可以切换英文，并配置了支持 CJK 的字体兜底，确保宿主机安装中文字体时运行截图不会出现中文乱码或方块字。

## 命令

```bash
npm ci
npm run dev
npm test
npm run build
npm run smoke
```

## Docker 编译

在仓库根目录运行：

```bash
docker build -f frontend/Dockerfile -t labelzone-frontend:local .
docker run --rm -p 8080:80 labelzone-frontend:local
```

Nginx 配置会把 `/api/` 请求代理到 Docker Compose 中名为 `backend` 的服务。
