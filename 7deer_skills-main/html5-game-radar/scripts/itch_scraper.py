#!/usr/bin/env python3
"""
itch.io HTML5 游戏监测
通过 browser 工具提取数据后，此脚本处理并评分
"""

import json
import re
from datetime import datetime

# 预期的 itchio HTML5 页面结构
ITCH_URL = "https://itch.io/games/tag-html5/sort:-created"

def parse_itch_cell(cell_html: str) -> dict:
    """
    从 itchio 游戏卡片 HTML 提取信息
    实际数据由 browser evaluate 注入
    """
    result = {
        'title': '',
        'dev': '',
        'date': '',
        'votes': '0',
        'views': '',
        'url': '',
        'platforms': []
    }
    
    # 提取游戏名
    title_match = re.search(r'class="title"[^>]*>([^<]+)<', cell_html)
    if title_match:
        result['title'] = title_match.group(1).strip()
    
    # 提取开发者
    dev_match = re.search(r'class="creator"[^>]*>([^<]+)<', cell_html)
    if dev_match:
        result['dev'] = dev_match.group(1).strip()
    
    # 提取发布日期
    date_match = re.search(r'class="game_release_date"[^>]*>([^<]+)<', cell_html)
    if date_match:
        result['date'] = date_match.group(1).strip()
    
    # 提取票数
    votes_match = re.search(r'class="vote_count"[^>]*>([^<]+)<', cell_html)
    if votes_match:
        result['votes'] = votes_match.group(1).strip()
    
    return result

def process_browser_data(browser_output: str) -> list:
    """
    处理从 browser evaluate 获得的数据
    格式: JSON 数组 或 纯文本列表
    """
    try:
        # 尝试 JSON 解析
        data = json.loads(browser_output)
        if isinstance(data, list):
            return data
    except:
        pass
    
    # 尝试从文本解析
    # 格式: "Title | Dev | Date | Votes"
    lines = browser_output.strip().split('\n')
    results = []
    
    for line in lines:
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                results.append({
                    'title': parts[0],
                    'dev': parts[1],
                    'date': parts[2],
                    'votes': parts[3],
                    'views': parts[4] if len(parts) > 4 else '',
                    'url': ''
                })
    
    return results

def main():
    print(f"[itch.io Monitor] itch.io HTML5 游戏监测")
    print(f"  目标页面: {ITCH_URL}")
    print()
    print("  注意：此脚本处理 browser 工具提取的数据")
    print("  请先使用 browser 工具：")
    print("    1. navigate → https://itch.io/games/tag-html5/sort:-created")
    print("    2. 滚动 3-5 次收集数据")
    print("    3. evaluate JS 提取游戏列表")
    print()
    print("  提取数据后，运行此脚本处理结果")
    print()
    
    # 尝试从标准输入或文件读取
    input_data = None
    
    try:
        # 优先从文件读取
        with open('/tmp/itch_browser_output.json', 'r') as f:
            input_data = json.load(f)
        print(f"[OK] 从文件加载 {len(input_data)} 个游戏")
    except FileNotFoundError:
        print("[INFO] 未找到 browser 输出文件，使用示例数据演示")
        input_data = [
            {"title": "示例游戏", "dev": "示例开发者", "date": "2 days ago", "votes": "47", "views": "1.2K"},
        ]
    
    results = []
    for item in input_data:
        results.append({
            'title': item.get('title', 'Unknown'),
            'dev': item.get('dev', ''),
            'date': item.get('date', ''),
            'votes': str(item.get('votes', '0')),
            'views': item.get('views', ''),
            'url': item.get('url', ''),
            'platform': 'itch.io'
        })
    
    # 输出
    with open('/tmp/itch_output.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 输出 {len(results)} 个游戏到 /tmp/itch_output.json")
    print("\n🏆 Top 5 最新 HTML5 游戏：")
    for i, g in enumerate(results[:5], 1):
        print(f"  {i}. {g['title']} by {g['dev']}")
        print(f"     发布: {g['date']} | 票数: {g['votes']}")

if __name__ == '__main__':
    main()
