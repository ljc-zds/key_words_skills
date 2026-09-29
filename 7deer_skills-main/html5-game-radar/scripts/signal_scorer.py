#!/usr/bin/env python3
"""
HTML5 Game Signal Scorer v2
改用：标题关键词 + 游戏类型 + Reddit信号 + Google竞争度 + X信号

输入: 多源 JSON 数据（itchio/reddit/trends/x_signal）
输出: 按 0-20 分信号评分排序的 JSON 报告
"""

import json
import re
from datetime import datetime
from typing import Optional

# 热门类型关键词（高价值）
HOT_GENRES = {'action', 'adventure', 'survival', 'puzzle', 'horror', 'rpg', 'roguelike', 'multiplayer', 'platformer'}
# 中等类型
MEDIUM_GENRES = {'simulation', 'strategy', 'simulation', 'casual', 'sports', 'racing'}
# Jam/低价值过滤词
JAM_FILTER = {'jam', 'ludum', 'gmtk', 'game jam', 'one game a month', 'oc', 'gamejam'}

def score_title_keywords(title: str) -> int:
    """标题关键词评分 +1~5"""
    title_lower = title.lower()
    score = 0
    
    # 高价值关键词
    high_value = ['new', 'free', 'multiplayer', 'io ', ' online', 'survival', 'roguelike', 'viral']
    for kw in high_value:
        if kw in title_lower:
            score += 2
    
    # 中等价值关键词
    medium_value = ['adventure', 'action', 'horror', 'puzzle', 'rpg', 'platformer', 'multi']
    for kw in medium_value:
        if kw in title_lower:
            score += 1
    
    # 限制上限
    return min(score, 5)

def score_genre(genre: str) -> int:
    """游戏类型评分 +1~3"""
    if not genre:
        return 1
    genre_lower = genre.lower()
    
    if any(g in genre_lower for g in HOT_GENRES):
        return 3
    elif any(g in genre_lower for g in MEDIUM_GENRES):
        return 2
    return 1

def is_jam_game(title: str, dev: str = '') -> bool:
    """过滤 Jam 游戏"""
    text = (title + ' ' + dev).lower()
    return any(f in text for f in JAM_FILTER)

def score_reddit_signal(upvotes: int, comments: int) -> int:
    """Reddit 信号评分 +1~4"""
    score = 0
    if upvotes >= 100:
        score += 3
    elif upvotes >= 50:
        score += 2
    elif upvotes >= 20:
        score += 1
    
    if comments >= 20:
        score += 1
    
    return min(score, 4)

def score_google_competition(result_count: int) -> int:
    """Google 竞争度评分 +1~4（分数越高竞争越低=SEO越好）"""
    if result_count == 0:
        return 4
    elif result_count < 50000:
        return 3
    elif result_count < 200000:
        return 2
    elif result_count < 500000:
        return 1
    return 0

def score_x_signal(mention_count: int) -> int:
    """X/Twitter 信号评分 +1~3"""
    if mention_count >= 3:
        return 3
    elif mention_count >= 2:
        return 2
    elif mention_count >= 1:
        return 1
    return 0

def calculate_total_score(
    title_score: int,
    genre_score: int,
    dev_score: int,
    reddit_score: int,
    google_score: int,
    x_score: int
) -> int:
    """计算总分"""
    return title_score + genre_score + dev_score + reddit_score + google_score + x_score

def get_seo_verdict(score: int) -> tuple:
    """根据分数判断 SEO 行动建议"""
    if score >= 15:
        return "🔥 立即行动", "✅ 套利窗口明确，立即建站/写内容"
    elif score >= 10:
        return "✅ 值得做", "⚠️ 中等信号，写攻略或合集页"
    elif score >= 5:
        return "⚠️ 观察", "📋 加入监控列表，持续跟踪"
    else:
        return "❌ 跳过", "⚪ 竞争已饱和或信号太弱"

def main():
    import argparse
    parser = argparse.ArgumentParser(description='HTML5 Game Signal Scorer v2')
    parser.add_argument('--itch', default='/tmp/itch_output.json', help='itch.io JSON')
    parser.add_argument('--reddit', default='/tmp/reddit_output.json', help='Reddit JSON')
    parser.add_argument('--trends', default='/tmp/trends_output.json', help='Trends JSON')
    parser.add_argument('--x_signal', default='/tmp/x_output.json', help='X signal JSON')
    parser.add_argument('--output', default='/tmp/html5_radar_output.json', help='Output JSON')
    parser.add_argument('--top_n', type=int, default=20, help='输出 Top N')
    args = parser.parse_args()

    all_games = []

    # 1. 处理 itch.io 数据
    try:
        with open(args.itch, 'r') as f:
            itch_data = json.load(f)
        for item in itch_data:
            title = item.get('title', 'Unknown')
            dev = item.get('dev', '')
            genre = item.get('genre', item.get('type', ''))
            
            # 过滤 Jam 游戏
            if is_jam_game(title, dev):
                continue
            
            url = item.get('url', '')
            
            game = {
                'name': title,
                'platform': 'itch.io',
                'dev': dev,
                'genre': genre,
                'url': url,
                'title_score': score_title_keywords(title),
                'genre_score': score_genre(genre),
                'dev_score': 1,  # 暂时默认1
                'reddit_score': 0,
                'google_score': 0,
                'x_score': 0,
                'sources': ['itch.io']
            }
            game['total_score'] = calculate_total_score(
                game['title_score'], game['genre_score'],
                game['dev_score'], game['reddit_score'],
                game['google_score'], game['x_score']
            )
            game['verdict'], game['action'] = get_seo_verdict(game['total_score'])
            all_games.append(game)
    except FileNotFoundError:
        print("[WARN] itch.io 数据文件不存在，跳过")

    # 2. 处理 Reddit 数据
    try:
        with open(args.reddit, 'r') as f:
            reddit_data = json.load(f)
        for item in reddit_data:
            title = item.get('title', 'Unknown')
            upvotes = item.get('upvotes', item.get('score', 0))
            comments = item.get('comments', 0)
            
            # 尝试从标题推断游戏名
            game_name = re.sub(r'\[.*?\]|\(.*?\)', '', title).strip()
            game_name = re.sub(r'(free|online|game|html5|browser)$', '', game_name, flags=re.I).strip()
            
            game = {
                'name': game_name or title,
                'platform': 'Reddit',
                'dev': item.get('author', ''),
                'genre': '',
                'url': item.get('url', ''),
                'title_score': score_title_keywords(game_name) if game_name else 0,
                'genre_score': 1,
                'dev_score': 1,
                'reddit_score': score_reddit_signal(upvotes, comments),
                'google_score': 0,
                'x_score': 0,
                'sources': ['reddit']
            }
            game['total_score'] = calculate_total_score(
                game['title_score'], game['genre_score'],
                game['dev_score'], game['reddit_score'],
                game['google_score'], game['x_score']
            )
            game['verdict'], game['action'] = get_seo_verdict(game['total_score'])
            all_games.append(game)
    except FileNotFoundError:
        print("[WARN] Reddit 数据文件不存在，跳过")

    # 3. 处理 Google Trends/竞争度数据
    try:
        with open(args.trends, 'r') as f:
            trends_data = json.load(f)
        for item in trends_data:
            result_count = item.get('result_count', 0)
            google_score = score_google_competition(result_count)
            
            # 匹配已存在的游戏
            for g in all_games:
                if g['name'].lower() in item.get('query', '').lower():
                    g['google_score'] = google_score
                    g['sources'].append('google')
    except FileNotFoundError:
        print("[WARN] Trends 数据文件不存在，跳过")

    # 4. 处理 X 信号数据
    try:
        with open(args.x_signal, 'r') as f:
            x_data = json.load(f)
        for item in x_data:
            mention_count = item.get('count', 0)
            x_score = score_x_signal(mention_count)
            
            # 匹配已存在的游戏
            for g in all_games:
                if g['name'].lower() in item.get('game', '').lower():
                    g['x_score'] = x_score
                    g['sources'].append('x')
    except FileNotFoundError:
        print("[WARN] X signal 数据文件不存在，跳过")

    # 5. 按分数排序
    all_games.sort(key=lambda x: x['total_score'], reverse=True)
    top_games = all_games[:args.top_n]

    # 6. 生成报告
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_found': len(all_games),
        'top_count': len(top_games),
        'games': top_games,
        'summary': {
            '🔥 立即行动': len([g for g in all_games if g['total_score'] >= 15]),
            '✅ 值得做': len([g for g in all_games if 10 <= g['total_score'] < 15]),
            '⚠️ 观察': len([g for g in all_games if 5 <= g['total_score'] < 10]),
            '❌ 跳过': len([g for g in all_games if g['total_score'] < 5]),
        }
    }

    # 7. 输出
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # 8. 打印摘要
    print(f"\n🎮 HTML5 Game Radar 报告 v2 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print(f"📊 总发现：{report['total_found']} 个游戏/信号")
    print(f"🏆 Top 候选（≥10分）：{len([g for g in all_games if g['total_score'] >= 10])} 个")
    print()
    for label, count in report['summary'].items():
        print(f"  {label}: {count}")
    print()
    print("🏆 Top 10 信号游戏：")
    print("-" * 60)
    for i, g in enumerate(top_games[:10], 1):
        print(f"{i}. [{g['total_score']:2d}分] {g['verdict']} {g['name']}")
        print(f"   类型:{g['genre'] or '未知'} | 标题关键词:{g['title_score']} | 类型分:{g['genre_score']} | Reddit:{g['reddit_score']} | Google:{g['google_score']} | X:{g['x_score']}")
        print(f"   操作：{g['action']}")
        print()

if __name__ == '__main__':
    main()
