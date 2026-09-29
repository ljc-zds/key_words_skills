#!/usr/bin/env python3
"""
Reddit r/webgames HTML5 游戏监测
调用 reddit-research skill 的 CLI 抓取新帖
"""

import json
import subprocess
import re
import sys
from datetime import datetime

REDDIT_SCRIPT = "$HOME/.openclaw/workspaces/automation-publisher/skills/reddit-research-but-free/scripts/reddit.ts"

def run_reddit_cli(args: list) -> str:
    """运行 reddit.ts CLI"""
    cmd = ["npx", "tsx", REDDIT_SCRIPT] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/Users/zirer/.openclaw/workspaces/automation-publisher/skills/reddit-research-but-free/scripts"
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"[ERROR] {e}"

def extract_posts(raw_output: str) -> list:
    """从 reddit.ts 输出解析帖子"""
    posts = []
    lines = raw_output.strip().split('\n')
    
    # 解析 reddit.ts 的 markdown 输出格式
    # 格式: [⬆️ N] Title | r/sub | by u/author | X hours ago
    post_block = []
    in_block = False
    
    for line in lines:
        # 检测到帖子开始（包含 ⬆️ 或 ↑ 则为帖子行）
        if '⬆️' in line or '⬆' in line:
            if post_block:
                posts.append('\n'.join(post_block))
            post_block = [line]
            in_block = True
        elif in_block:
            post_block.append(line)
            # 遇到空行或下一个帖子开始，结束当前块
            if line.strip() == '' or ('⬆️' in line or '⬆' in line) and len(post_block) > 1:
                posts.append('\n'.join(post_block))
                post_block = []
                in_block = False
    
    if post_block:
        posts.append('\n'.join(post_block))
    
    return posts

def parse_post(post_text: str) -> dict:
    """解析单个帖子"""
    result = {
        'title': '',
        'upvotes': 0,
        'comments': 0,
        'author': '',
        'time': '',
        'url': '',
        'sub': 'webgames',
        'raw': post_text
    }
    
    lines = post_text.split('\n')
    for line in lines:
        # 解析 upvotes
        upvotes_match = re.search(r'[⬆️⬆]\s*(\d+)', line)
        if upvotes_match:
            result['upvotes'] = int(upvotes_match.group(1))
        
        # 解析时间
        time_match = re.search(r'(\d+)\s*(hour|day|minute|week|month)', line, re.I)
        if time_match:
            result['time'] = f"{time_match.group(1)} {time_match.group(2)}"
        
        # 解析作者
        author_match = re.search(r'by\s+u/(\w+)', line, re.I)
        if author_match:
            result['author'] = author_match.group(1)
        
        # 解析 URL
        url_match = re.search(r'https?://[^\s\)]+', line)
        if url_match:
            result['url'] = url_match.group(0)
    
    # 第一行通常是标题
    first_line = lines[0] if lines else ''
    # 移除 upvote 部分，保留标题
    title = re.sub(r'^[⬆️⬆]\s*\d+\s*', '', first_line).strip()
    # 移除 sub 和 author 信息
    title = re.sub(r'\s*\|\s*r/\w+\s*\|\s*by.*$', '', title)
    result['title'] = title
    
    return result

def filter_html5_related(post: dict) -> bool:
    """过滤与 HTML5/浏览器游戏相关的帖子"""
    if not post['title']:
        return False
    
    keywords = [
        'html5', 'html 5', 'browser game', 'web game',
        'itch.io', 'no download', 'play in browser',
        'free to play', 'online game', 'unblocked',
        'io game', '.io', 'crazy games', 'miniclip',
        'kongregate', 'armor games', 'gamepix',
        'new game', 'just released', 'first look'
    ]
    
    title_lower = post['title'].lower()
    return any(kw.lower() in title_lower for kw in keywords)

def main():
    output = []
    
    print("[Reddit Monitor] 正在扫描 r/webgames...")
    
    # 方法1: 获取 hot 帖子里找新的
    print("  → 获取 hot 帖子...")
    hot_output = run_reddit_cli(["hot", "webgames", "--limit", "50"])
    hot_posts = extract_posts(hot_output)
    
    # 方法2: 获取最新帖子
    print("  → 获取最新帖子...")
    new_output = run_reddit_cli(["new", "webgames", "--limit", "30"])
    new_posts = extract_posts(new_output)
    
    all_posts = hot_posts + new_posts
    
    print(f"  → 解析 {len(all_posts)} 个帖子...")
    
    for post_text in all_posts:
        post = parse_post(post_text)
        if filter_html5_related(post):
            output.append(post)
    
    # 去重（按标题）
    seen = set()
    unique_output = []
    for post in output:
        if post['title'] not in seen:
            seen.add(post['title'])
            unique_output.append(post)
    
    # 按 upvotes 排序
    unique_output.sort(key=lambda x: x['upvotes'], reverse=True)
    
    print(f"  → 发现 {len(unique_output)} 个 HTML5 相关帖子")
    
    # 输出 JSON
    with open('/tmp/reddit_output.json', 'w') as f:
        json.dump(unique_output, f, indent=2, ensure_ascii=False)
    
    # 打印 Top 5
    print("\n🏆 Top 5 HTML5 游戏讨论：")
    for i, post in enumerate(unique_output[:5], 1):
        print(f"  {i}. [{post['upvotes']}⬆] {post['title'][:50]}...")
        print(f"     r/webgames | by u/{post['author']} | {post['time']}")

if __name__ == '__main__':
    main()
