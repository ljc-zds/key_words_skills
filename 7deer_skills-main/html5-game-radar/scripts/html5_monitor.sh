#!/bin/bash
#===========================================================
# HTML5 Game Radar — 主监控脚本
# 用途：多源抓取 HTML5 新游戏，输出结构化 JSON
# 
# 使用方式：
#   ./html5_monitor.sh
#
# 输出：
#   /tmp/html5_radar_output.json
#===========================================================

SKILL_DIR="$HOME/.openclaw/workspaces/automation-publisher/skills/html5-game-radar"
OUTPUT_FILE="/tmp/html5_radar_output.json"
DATE=$(date '+%Y-%m-%d %H:%M')

echo "🎮 HTML5 Game Radar 启动 | $DATE"
echo "========================================"

#===========================================================
# Source functions
#===========================================================
SCRIPT_DIR="$SKILL_DIR/scripts"

if [ -f "$SCRIPT_DIR/itch_scraper.py" ]; then
    echo "[1/5] 抓取 itch.io..."
    python3 "$SCRIPT_DIR/itch_scraper.py" >> /tmp/itch_output.json 2>&1
    ICH_COUNT=$(cat /tmp/itch_output.json 2>/dev/null | grep -c '"title"' || echo 0)
    echo "   → 发现 $ICH_COUNT 个游戏"
fi

if [ -f "$SCRIPT_DIR/reddit_monitor.py" ]; then
    echo "[2/5] 扫描 Reddit r/webgames..."
    python3 "$SCRIPT_DIR/reddit_monitor.py" >> /tmp/reddit_output.json 2>&1
    REDDIT_COUNT=$(cat /tmp/reddit_output.json 2>/dev/null | grep -c '"title"' || echo 0)
    echo "   → 发现 $REDDIT_COUNT 篇相关帖子"
fi

echo "[3/5] Google Trends 信号收集..."
if [ -f "$SCRIPT_DIR/google_trends_check.py" ]; then
    python3 "$SCRIPT_DIR/google_trends_check.py" >> /tmp/trends_output.json 2>&1
fi

echo "[4/5] X/Twitter 信号收集..."
echo "   → 需人工触发 browser 工具抓取 X 搜索"

echo "[5/5] 信号评分..."
if [ -f "$SCRIPT_DIR/signal_scorer.py" ]; then
    python3 "$SCRIPT_DIR/signal_scorer.py" \
        --itch /tmp/itch_output.json \
        --reddit /tmp/reddit_output.json \
        --trends /tmp/trends_output.json \
        --output "$OUTPUT_FILE"
fi

echo "========================================"
echo "✅ 完成！输出：$OUTPUT_FILE"
cat "$OUTPUT_FILE"
