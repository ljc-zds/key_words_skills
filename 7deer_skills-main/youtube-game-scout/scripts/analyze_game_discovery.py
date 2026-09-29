#!/usr/bin/env python3
"""
Game Discovery Analyzer - Focused on emerging game signals for search arbitrage.
Identifies new games, trending updates, and cross-platform opportunities.

Usage:
    python3 analyze_game_discovery.py INPUT_JSON [--output REPORT.md]
"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ─── Platform Detection ───────────────────────────────────────────────────────

PLATFORM_PATTERNS = {
    'Roblox':   r'\bROBLOX\b|\bRoblox\b',
    'Steam':    r'\b(Steam|STEAM)\b',
    'itch.io':  r'\bitch\.?io\b|\bitch\.io\b',
    'Epic':     r'\bEpic\s+(Games|Store)\b',
    'Mobile':   r'\b(iOS|Android|Mobile)\b',
    'HTML5':    r'\bHTML5\b|\bHTML 5\b|\bWeb\s+Game\b|\bBrowser\s+Game\b',
    'Nintendo': r'\bNintendo\b|\bSwitch\b|\bWii\s*U\b',
}

# ─── Emerging Signal Detection ─────────────────────────────────────────────────

# High-value patterns that indicate NEW / EMERGING content
EMERGING_PATTERNS = [
    (3, r'\bNEW\s+(GAME|UPDATE|MAP|WEAPON|CHARACTER|EVENT|SEASON|MODE)\b'),
    (2, r'\bJUST\s+DROPPED\b'),
    (2, r'\bFIRST\s+LOOK\b'),
    (2, r'\bNEW\s+RELEASE\b'),
    (2, r'\bNEW\b.*\bGAME\b'),
    (2, r'\bEMERGING\b'),
    (2, r'\bRISING\b'),
    (2, r'\bTRENDING\b'),
    (1, r'\bUPDATE\b'),
    (1, r'\bUPDATE\s+CODES\b'),
]

# Genre / mechanic signals
GENRE_PATTERNS = {
    'Simulator':        r'\bSim(ulator|ulation)?\b',
    'Obby':            r'\bObby\b',
    'Brainrot':        r'\bBrain\s*rot\b|\bBrainrot\b',
    'Horror':          r'\bHorror\b|\bScary\b|\bSpooky\b',
    'Tower Defense':   r'\bTower\s*Defense\b|\bTD\b',
    'Survival':        r'\bSurvival\b|\bSurvive\b',
    'Tycoon':          r'\bTycoon\b',
    'RPG/Adventure':   r'\bRPG\b|\bMMORPG\b|\bAdventure\b',
    'FPS/Shooter':     r'\bFPS\b|\bShooter\b|\bCombat\b',
    'Racing':          r'\bRacing\b|\bRace\b',
    'Platformer':      r'\bPlatform(er)?\b',
    'Puzzle':          r'\bPuzzle\b',
    'Card/Battler':    r'\bAutobattler\b|\bDeck\b.*\bBuild\b',
    'Sports':          r'\bSoccer\b|\bFootball\b|\bBasketball\b|\bSports\b',
    'Rhythm':          r'\bRhythm\b|\bMusic\b.*\bGame\b',
}

# ─── Utility Functions ─────────────────────────────────────────────────────────

def get_video_id(url):
    m = re.search(r'[?&]v=([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else ''

def score_signals(title, channel=''):
    """Score how strong a discovery signal this video is (0-20)."""
    score = 0
    t = title + ' ' + channel

    for pts, pat in EMERGING_PATTERNS:
        if re.search(pat, title, re.IGNORECASE):
            score += pts

    # Platform clarity adds confidence
    for platform, pat in PLATFORM_PATTERNS.items():
        if re.search(pat, t, re.IGNORECASE):
            score += 1

    # Genre signals
    for genre, pat in GENRE_PATTERNS.items():
        if re.search(pat, title, re.IGNORECASE):
            score += 1

    # ALL CAPS titles often indicate game names
    if re.search(r'\b[A-Z]{4,}\b', title):
        score += 1

    # "I played / I tried" = personal review, often for newer/indie games
    if re.search(r"\bI\s+(played|tried|spent|got|found|built)\b", title, re.IGNORECASE):
        score += 1

    # "Is it worth" / "Should you" = evaluation content for new games
    if re.search(r'\bWorth\b|\bShould\s+You\b|\bIs\s+It\s+Good\b', title, re.IGNORECASE):
        score += 1

    # Numbers in title (odds, tiers, top X) = ranking/analysis content
    if re.search(r'\b\d+\s*(/|\\|x)\s*\d+\b|\bTop\s*\d+\b|\b\d+\s*(K|M|B)\b', title):
        score += 1

    return min(score, 20)

def looks_game_related(title, channel=''):
    """Basic filter - is this video about games?"""
    t = (title + ' ' + channel).lower()
    keywords = [
        'game', 'play', 'gaming', 'roblox', 'minecraft', 'fortnite',
        'stea', 'simulat', 'rpg', 'fps', 'update', 'walkthrough',
        'guide', 'review', 'tier list', 'speedrun', 'let\'s play',
        'hunter', 'survival', 'battle royale', 'tycoon',
    ]
    return any(k in t for k in keywords)

def extract_game_name(title):
    """Extract the likely game name from a video title."""
    # Remove common prefixes
    t = re.sub(r'^(ROBLOX\s+|NEW\s+|FIRST\s+LOOK\s+|\*NEW\*\s+)', '', title, flags=re.IGNORECASE)
    # Remove trailing activity descriptions
    t = re.sub(r'\s*[\|\-:\>>]\s*(ROBLOX\s+)?.*$', '', t)
    t = re.sub(r'\s*【.*?】\s*$', '', t)
    t = re.sub(r'\s*\(.*?\)\s*$', '', t)
    t = t.strip()
    # Truncate
    if len(t) > 70:
        t = t[:70]
    return t if t else None

def classify_game(title, channel=''):
    """Classify a video's game into structured categories."""
    t = title + ' ' + channel

    platforms = [p for p, pat in PLATFORM_PATTERNS.items() if re.search(pat, t, re.IGNORECASE)]
    genres = [g for g, pat in GENRE_PATTERNS.items() if re.search(pat, title, re.IGNORECASE)]

    game_name = extract_game_name(title)
    is_new = bool(re.search(r'\bNEW\b', title, re.IGNORECASE))
    is_update = bool(re.search(r'\bUPDATE\b', title, re.IGNORECASE))

    return {
        'platforms': platforms or ['Unknown'],
        'genres': genres or ['General'],
        'gameName': game_name,
        'isNew': is_new,
        'isUpdate': is_update,
        'score': score_signals(title, channel),
        'title': title,
        'url': '',
        'videoId': '',
        'channel': channel,
        'views': ''
    }

# ─── Main Analysis ─────────────────────────────────────────────────────────────

def analyze_games(data):
    videos = data.get('videos', [])
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)
    today = now.date()

    # Deduplicate games by normalized name
    seen_games = {}
    all_game_videos = []  # all game-related videos

    for v in videos:
        title = v.get('title', '')
        url = v.get('url', '')
        channel = v.get('channel', '')
        views = v.get('views', '')

        if not looks_game_related(title, channel):
            continue

        video_id = get_video_id(url)
        cls = classify_game(title, channel)
        cls['url'] = url
        cls['videoId'] = video_id
        cls['views'] = views
        all_game_videos.append(cls)

        game_name = cls['gameName'] or title[:40]
        key = re.sub(r'[^a-z0-9]', '', game_name.lower())[:50]

        if key not in seen_games or cls['score'] > seen_games[key].get('score', 0):
            seen_games[key] = cls

    all_games = sorted(seen_games.values(), key=lambda x: x['score'], reverse=True)

    # Categories
    roblox_games = [g for g in all_games if 'Roblox' in g['platforms']]
    steam_games = [g for g in all_games if 'Steam' in g['platforms']]
    indie_games = [g for g in all_games if any(p in g['platforms'] for p in ['itch.io', 'HTML5', 'Epic'])]
    high_signal = [g for g in all_games if g['score'] >= 4]
    new_releases = [g for g in all_games if g['isNew']]
    major_updates = [g for g in all_games if g['isUpdate']]

    return {
        'reportDate': now.strftime('%Y-%m-%d %H:%M'),
        'totalRawVideos': len(videos),
        'totalGameVideos': len(all_game_videos),
        'totalUniqueGames': len(all_games),
        'all_games': all_games,
        'high_signal': high_signal[:15],
        'new_releases': new_releases[:10],
        'major_updates': major_updates[:10],
        'roblox_games': roblox_games[:20],
        'steam_games': steam_games[:10],
        'indie_games': indie_games[:10],
    }

# ─── Report Generator ──────────────────────────────────────────────────────────

def format_report(a):
    lines = []
    now_str = a['reportDate']

    lines.append(f"# 🎮 Game Scout 日报 | {now_str}")
    lines.append("")
    lines.append(f"> **数据**：YouTube 订阅频道 {a['totalRawVideos']} 条原始视频 → {a['totalGameVideos']} 条游戏相关 → 去重 {a['totalUniqueGames']} 款游戏")
    lines.append(f"> **目标**：发现**新游戏 / 爆火信号 / 搜索套利机会**（Roblox / Steam / itch.io / HTML5）")
    lines.append("")

    # ── High Signal Games ──
    lines.append("## 🏆 高置信度新游戏信号（Score ≥ 4）")
    lines.append("")

    if a['high_signal']:
        for i, g in enumerate(a['high_signal'], 1):
            tags = ' '.join([f'`{p}`' for p in g['platforms']])
            genre_tags = ' '.join([f'`{gen}`' for gen in g['genres']])
            new_badge = '🆕' if g['isNew'] else ('🔄' if g['isUpdate'] else '📈')
            lines.append(f"**{i}. {g['gameName']}**")
            lines.append(f"   - 平台：{tags} | 类型：{genre_tags}")
            lines.append(f"   - 信号强度：{g['score']}/20 {new_badge}")
            lines.append(f"   - 「{g['title'][:100]}」")
            if g['channel']: lines.append(f"   - 频道：{g['channel']}")
            lines.append(f"   - https://youtube.com/watch?v={g['videoId']}")
            lines.append("")
    else:
        lines.append("*暂无高置信度信号（订阅频道可能偏向已确立游戏）*")
        lines.append("")

    # ── New Releases ──
    lines.append("---")
    lines.append("")
    lines.append("## 🆕 新游戏 / 首发内容")
    lines.append("")

    if a['new_releases']:
        for g in a['new_releases'][:8]:
            tags = ', '.join(g['platforms'])
            lines.append(f"**🆕 {g['gameName']}** ({tags})")
            lines.append(f"   「{g['title'][:90]}」")
            lines.append(f"   - 频道：{g['channel']} | 信号：{g['score']}")
            lines.append("")
    else:
        lines.append("*今日订阅频道无明确首发内容*")
        lines.append("")

    # ── Roblox ──
    lines.append("---")
    lines.append("")
    lines.append("## 🔴 Roblox 重点信号（高信号 + 新更新）")
    lines.append("")

    roblox_interesting = [g for g in a['roblox_games'] if g['score'] >= 3]
    if roblox_interesting:
        for g in roblox_interesting[:10]:
            badge = '🆕' if g['isNew'] else ('🔄' if g['isUpdate'] else '📈')
            lines.append(f"**{badge} {g['gameName']}**")
            lines.append(f"   「{g['title'][:85]}」")
            lines.append(f"   - {g['channel']} | 信号:{g['score']}")
            lines.append("")
    else:
        lines.append("*Roblox 内容信号偏弱*")
        lines.append("")

    # ── Steam ──
    lines.append("---")
    lines.append("")
    lines.append("## 💻 Steam / 独立游戏")
    lines.append("")

    if a['steam_games']:
        for g in a['steam_games'][:8]:
            lines.append(f"**{g['gameName']}**")
            lines.append(f"   「{g['title'][:85]}」")
            lines.append(f"   - {g['channel']}")
            lines.append("")
    else:
        lines.append("*订阅频道 Steam 覆盖偏少，建议补充独立游戏向油管频道*")

    lines.append("")

    # ── Indie ──
    if a['indie_games']:
        lines.append("---")
        lines.append("")
        lines.append("## 🕹️ itch.io / HTML5 / 独立游戏")
        lines.append("")
        for g in a['indie_games'][:6]:
            platforms = ', '.join(g['platforms'])
            lines.append(f"**{g['gameName']}** ({platforms})")
            lines.append(f"   「{g['title'][:85]}」")
            lines.append("")

    # ── Platform Stats ──
    lines.append("---")
    lines.append("")
    lines.append("## 📊 平台覆盖统计")
    lines.append("")

    platform_count = {}
    for g in a['all_games']:
        for p in g['platforms']:
            platform_count[p] = platform_count.get(p, 0) + 1

    for p, cnt in sorted(platform_count.items(), key=lambda x: -x[1]):
        bar = '▓' * min(cnt, 20)
        lines.append(f"`{p:10}` {bar} {cnt}")

    lines.append("")

    # ── Complete List ──
    lines.append("---")
    lines.append("")
    lines.append("## 🔍 完整游戏清单（按信号强度排序，前 25）")
    lines.append("")

    for i, g in enumerate(a['all_games'][:25], 1):
        score = g['score']
        bar = '🟢' * min(score, 5) + '⚪' * max(0, 5 - min(score, 5))
        tags = '/'.join(g['platforms'])
        lines.append(f"`{bar}` **{g['gameName']}** [{tags}]")
        lines.append(f"   「{g['title'][:70]}」 — {g['channel']}")

    lines.append("")
    lines.append("---")
    lines.append(f"*Game Scout v2 | {now_str}*")

    return '\n'.join(lines)

# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    input_path = '/tmp/yt_games_final.json'
    output_path = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--output':
            i += 1
            if i < len(args):
                output_path = args[i]
        elif not arg.startswith('-'):
            input_path = arg
        i += 1

    with open(input_path) as f:
        data = json.load(f)

    analysis = analyze_games(data)
    report = format_report(analysis)

    if output_path:
        Path(output_path).write_text(report)
        print(f"Saved: {output_path}", file=sys.stderr)
    else:
        print(report)
