#!/usr/bin/env python3
"""
Google Trends 游戏信号检测
检查当前上升中的游戏相关搜索词
"""

import json
import re
import sys
from datetime import datetime
from typing import Optional

def check_google_autocomplete(game_name: str) -> dict:
    """
    模拟 Google 搜索量检查
    通过搜索建议判断热度级别
    """
    return {
        'game': game_name,
        'has_suggestions': True,  # 有自动补全 = 有搜索量
        'estimated_volume': 'medium'
    }

def parse_google_search_results(html_content: str, game_name: str) -> dict:
    """
    从 Google 搜索结果页分析竞争度
    结果数量 < 50000 = 低竞争
    结果数量 > 200000 = 高竞争
    """
    result_count_match = re.search(r'约([\d,]+)个?结果', html_content)
    if result_count_match:
        count_str = result_count_match.group(1).replace(',', '')
        try:
            result_count = int(count_str)
        except:
            result_count = 0
    else:
        result_count = 0
    
    return {
        'result_count': result_count,
        'competition': 'low' if result_count < 50000 else 'medium' if result_count < 200000 else 'high'
    }

def evaluate_seo_opportunity(
    has_autocomplete: bool,
    result_count: int,
    has_wiki: bool,
    has_official_site: bool
) -> tuple:
    """
    判断 SEO 套利机会
    """
    score = 0
    signals = []
    
    if has_autocomplete:
        score += 2
        signals.append("有搜索补全（搜索量确认）")
    
    if result_count == 0:
        score += 4
        signals.append("极低竞争（< 5万结果）")
    elif result_count < 50000:
        score += 3
        signals.append("低竞争（< 5万结果）")
    elif result_count < 200000:
        score += 1
        signals.append("中等竞争")
    else:
        score -= 1
        signals.append("高竞争（> 20万结果）")
    
    if has_wiki:
        score += 1
        signals.append("有 Wikipedia（流量精准）")
    
    if has_official_site:
        score += 1
        signals.append("有官网（商业价值高）")
    
    verdict = "✅ 套利窗口" if score >= 5 else "⚠️ 谨慎进入" if score >= 3 else "❌ 竞争饱和"
    
    return score, verdict, signals

def main():
    # 已知的新游戏列表（由 itchio/reddit 扫描得到）
    # 这个脚本主要验证这些游戏的 SEO 潜力
    
    # 预设检测的游戏关键词
    # 实际使用时由 itchio 或 reddit 扫描结果传入
    game_queries = [
        # 这些应该由上层脚本从文件读取
    ]
    
    output = []
    
    # 从 stdin 或文件读取游戏列表
    try:
        with open('/tmp/itch_output.json', 'r') as f:
            itch_games = json.load(f)
        for g in itch_games[:10]:  # 只检查 Top 10
            game_queries.append(g.get('title', ''))
    except:
        pass
    
    try:
        with open('/tmp/reddit_output.json', 'r') as f:
            reddit_games = json.load(f)
        for g in reddit_games[:10]:
            title = g.get('title', '')
            # 从标题提取可能的游戏名
            if any(kw in title.lower() for kw in ['html5', 'browser game', 'itch.io']):
                continue  # 跳过非游戏名标题
            game_queries.append(title)
    except:
        pass
    
    print(f"[Google Trends] 正在检查 {len(game_queries)} 个游戏的 SEO 潜力...")
    
    # 注意：这里需要人工通过 browser 工具验证
    # 脚本输出的是结构化的验证框架
    for query in game_queries:
        result = {
            'query': query,
            'checked_at': datetime.now().isoformat(),
            'note': '需要通过 browser 工具验证 Google 搜索量和竞争度',
            'check_url': f"https://www.google.com/search?q={query.replace(' ', '+')}+game+online+free",
            'estimated_score': 0,
            'verdict': '⚠️ 待验证'
        }
        output.append(result)
    
    # 输出
    with open('/tmp/trends_output.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已生成 {len(output)} 个游戏的 SEO 检查清单")
    print("   请使用 browser 工具访问 check_url 验证搜索量和竞争度")
    print("\n📋 检查清单：")
    for r in output[:5]:
        print(f"   - {r['query']}: {r['check_url']}")

if __name__ == '__main__':
    main()
