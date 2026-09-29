# YouTube Game Scout

通过 CDP 自动化抓取 YouTube 订阅频道，识别新游戏发现信号。

## 快速开始

### 1. 启动 Chrome 远程调试

```bash
# macOS
open -a "Google Chrome" --args --remote-debugging-port=18800

# Windows
chrome.exe --remote-debugging-port=18800

# Linux
google-chrome --remote-debugging-port=18800
```

### 2. 安装依赖

```bash
npm install -g ws
```

### 3. 运行抓取

```bash
NODE_PATH=$HOME/.npm-global/lib/node_modules \
  node scripts/cdp_game_scout.js
```

### 4. 分析结果

```bash
python3 scripts/analyze_game_discovery.py
```

## 目录结构

```
youtube-game-scout/
├── SKILL.md           # 技能说明文档
├── README.md          # 本文件
└── scripts/
    ├── cdp_game_scout.js      # CDP 抓取脚本
    └── analyze_game_discovery.py  # 信号分析器
```

## 信号评分

目标：挖掘热门的又热又新的游戏，进行 SEO 流量站套利。

| 分数 | 类型 | 说明 |
|------|------|------|
| 15-20 | 高确定性 | 新发布 + 强信号 |
| 8-14 | 中确定性 | 上升期 / 跟随内容 |
| 0-7 | 低确定性 | 老游戏 / 弱信号 |

## 适用场景

- YouTube 订阅频道批量分析
- 游戏发现 SEO 内容调研
- Roblox/Steam/itch.io 新游戏监控
