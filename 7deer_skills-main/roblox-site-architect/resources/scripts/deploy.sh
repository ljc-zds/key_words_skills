#!/bin/bash
# deploy.sh — 建站部署脚本
# 用法: bash deploy.sh

set -e

echo "=== Step 1: 安装依赖 ==="
npm install

echo "=== Step 2: 构建项目 ==="
npm run build

echo "=== Step 3: Git 提交 ==="
git add -A
git commit -m "feat: initial site build"
git push

echo "=== 部署完成 ==="
echo "Cloudflare Pages 将自动触发构建"
echo "构建完成后在 Cloudflare Dashboard 绑定自定义域名"
