#!/bin/bash
# setup-site.sh — 新站点初始化脚本
# 用法: bash setup-site.sh
# 将此脚本放到新项目目录执行

set -e

echo "=== Roblox 游戏站初始化脚本 ==="

# 1. 复制模板文件
echo "=== 复制模板文件 ==="
mkdir -p src/lib src/components src/app public

# 2. 创建项目基础文件
echo "=== 创建项目配置 ==="
cat > package.json << 'EOF'
{
  "name": "roblox-game-site",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "next": "^16.2.4",
    "react": "^19.2.4",
    "react-dom": "^19.2.4"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "^16.2.4",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}
EOF

# 3. 复制配置文件
echo "=== 复制配置文件 ==="
cp postcss.config.mjs ./

# 4. 安装依赖
echo "=== 安装依赖 ==="
npm install

# 5. 创建数据目录
echo "=== 创建数据目录 ==="
mkdir -p src/data
mkdir -p public

echo ""
echo "=== 初始化完成 ==="
echo "下一步:"
echo "1. 编辑 src/data/game.config.json"
echo "2. 编辑 src/data/items.json"
echo "3. 运行 npm run dev 本地预览"
echo "4. 运行 bash scripts/deploy.sh 部署"
