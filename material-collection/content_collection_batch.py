#!/usr/bin/env python3
"""
Google + YouTube 关键词素材批量收集脚本
========================================

两种使用模式：

【模式 1】单关键词（适合临时跑一个）
    python content_collection_batch.py --query "farever classes"

【模式 2】批量模式（接上一章 ChatGPT 生成的 keywords.json）
    python content_collection_batch.py --keywords-json keywords.json

    会读取 keywords.json 里所有分类下的所有关键词，
    对每个关键词生成一个独立的 md 文件，输出到 --output-dir 目录下。

技术选型：
    - Google 搜索：Serper API（SERPER_API_KEY）
    - Google 网页正文：Jina Reader（JINA_API_KEY，推荐）
    - YouTube 搜索：yt-dlp
    - YouTube 字幕：youtube-transcript-api
    - 代理：从 .env 读取青果网络代理池配置

依赖：
    pip install requests beautifulsoup4 yt-dlp youtube-transcript-api

输出文件结构（批量模式，按分类做子目录）：
    keywords-materials/
        classes/
            farever-classes.md
        codes/
            farever-codes.md
        tier-list/
            farever-tier-list.md
        ...

许可证：MIT
"""

import argparse
import json
import os
import random
import re
import subprocess
import sys
import time
from urllib.parse import quote

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("缺少依赖：requests / beautifulsoup4", file=sys.stderr)
    print("请运行：pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    from youtube_transcript_api import YouTubeTranscriptApi, RequestBlocked, IpBlocked
except ImportError:
    print("缺少依赖：youtube-transcript-api", file=sys.stderr)
    print("请运行：pip install youtube-transcript-api", file=sys.stderr)
    sys.exit(1)


# 视为 IP 被封的错误类型，触发换 IP 重试
IP_BLOCKED_ERRORS = (RequestBlocked, IpBlocked, ConnectionError, TimeoutError)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

COLLECTION_STATS = {
    "google_success": 0,
    "google_failed": 0,
    "youtube_candidates": 0,
    "youtube_filtered": 0,
    "youtube_success": 0,
    "youtube_failed": 0,
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ENV_FILE = os.path.join(SCRIPT_DIR, ".env")


def load_env_file(path=DEFAULT_ENV_FILE):
    """读取脚本目录下的 .env；已存在的环境变量优先。"""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)


def proxy_from_env():
    """按 游戏站高级业务班 .env 字段拼出代理 URL。"""
    if os.getenv("USE_PROXY", "false").lower() != "true":
        return None
    host = os.getenv("TUNNEL_HOST", "")
    port = os.getenv("TUNNEL_PORT", "")
    user = os.getenv("TUNNEL_USER", "")
    password = os.getenv("TUNNEL_PASS", "")
    if not all([host, port, user, password]):
        print("代理已开启，但 TUNNEL_HOST/PORT/USER/PASS 配置不完整", file=sys.stderr)
        return None
    proxy_format = os.getenv("TUNNEL_PROXY_FORMAT", "plain").lower()
    if proxy_format == "tagged":
        channel_prefix = os.getenv("TUNNEL_CHANNEL_PREFIX", "channel")
        ttl = os.getenv("TUNNEL_TTL", "60")
        return f"http://{user}:{password}:{channel_prefix}-default:{ttl}@{host}:{port}"
    return f"http://{user}:{password}@{host}:{port}"


def requests_proxies(proxy):
    """把单个代理 URL 转成 requests 使用的代理配置。"""
    if not proxy:
        return None
    return {"http": proxy, "https": proxy}


def search_google(query, count=2, proxy=None):
    """通过 Serper API 搜索 Google。"""
    api_key = os.getenv("SERPER_API_KEY", "")
    if not api_key:
        print("  缺少 SERPER_API_KEY，无法搜索 Google", file=sys.stderr)
        return []
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": max(count, 2)},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  Serper 搜索失败：{type(e).__name__}: {e}", file=sys.stderr)
        return []
    results = []
    seen = set()
    for item in response.json().get("organic", []):
        link = item.get("link", "")
        if not link or link in seen:
            continue
        seen.add(link)
        results.append({"title": item.get("title", ""), "url": link})
        if len(results) >= count:
            break
    return results


def extract_webpage(result, proxy=None):
    """优先通过 Jina Reader 提取网页正文，无 Key 时回退本地清洗。"""
    jina_key = os.getenv("JINA_API_KEY", "")
    if jina_key:
        try:
            response = requests.get(
                f"https://r.jina.ai/{quote(result['url'], safe=':/?=&%')}",
                headers={"Authorization": f"Bearer {jina_key}", "Accept": "text/plain"},
                timeout=60,
            )
            response.raise_for_status()
            content = response.text.strip()
            if content:
                return {**result, "content": content}
        except requests.RequestException as e:
            print(f"  Jina Reader 失败，回退本地提取：{type(e).__name__}: {e}", file=sys.stderr)

    try:
        response = requests.get(
            result["url"],
            headers=DEFAULT_HEADERS,
            proxies=requests_proxies(proxy),
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return {**result, "content": f"[网页正文提取失败：{type(e).__name__}: {e}]"}

    soup = BeautifulSoup(response.text, "html.parser")
    for node in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
        node.decompose()
    container = soup.find("article") or soup.find("main") or soup.body or soup
    blocks = []
    for node in container.find_all(["h1", "h2", "h3", "p", "li"]):
        text = " ".join(node.get_text(" ", strip=True).split())
        if len(text) >= 30:
            blocks.append(text)
    content = "\n\n".join(dict.fromkeys(blocks))
    if not content:
        content = "[网页没有提取到可读正文]"
    return {**result, "content": content}


def collect_google(query, count, proxy=None):
    """完成 Google 搜索与网页正文提取。"""
    print(f"  [Google 搜索] {query}", file=sys.stderr)
    results = search_google(query, count=count, proxy=proxy)
    print(f"  [Google 搜索] 找到 {len(results)} 个候选网页", file=sys.stderr)
    pages = []
    for index, result in enumerate(results, 1):
        print(f'  [Google {index}/{len(results)}] {result["title"]}', file=sys.stderr)
        pages.append(extract_webpage(result, proxy=proxy))
        if index < len(results):
            time.sleep(random.uniform(1, 2))
    return pages


def slugify(text):
    """把关键词/分类名转成文件名安全的 slug（小写、连字符分隔）"""
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "untitled"


def infer_topic(keyword):
    """从关键词推断游戏主题名（取第一个英文单词）。

    例：farever classes → farever
        100 waves later tier list → 100
        anime card collection codes → anime
    """
    parts = (keyword or "").lower().split()
    return parts[0] if parts else ""


def parse_duration_seconds(duration_string):
    """把 yt-dlp 返回的 HH:MM:SS / MM:SS 时长转成秒"""
    if not duration_string:
        return 0
    parts = str(duration_string).split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return 0
    seconds = 0
    for n in nums:
        seconds = seconds * 60 + n
    return seconds


def filter_by_duration(videos, max_duration):
    """过滤掉超过最大时长（秒）的视频；全过滤掉则保留时长最短的 1 个（兜底）"""
    if not videos:
        return []
    kept = [v for v in videos if parse_duration_seconds(v.get("duration_string")) <= max_duration]
    if kept:
        return kept
    return sorted(videos, key=lambda v: parse_duration_seconds(v.get("duration_string")))[:1]


# topic 相关性过滤用的英文停用词
_TOPIC_STOPWORDS = {"the", "that", "this", "with", "from", "into", "and", "for", "your"}


def filter_by_topic(videos, topic_name):
    """按 topic 名过滤视频标题，丢弃标题不含 topic（或 topic 核心实词）的视频。

    用于剔除搜关键词时混进来的无关 MV / 同名其他游戏 / 整活视频。
    """
    if not topic_name or not videos:
        return videos

    topic_lower = topic_name.lower()
    topic_nospace = topic_lower.replace(" ", "")
    topic_words = topic_lower.split()
    core_tokens = (
        [w for w in topic_words if len(w) >= 4 and w not in _TOPIC_STOPWORDS]
        if len(topic_words) > 2 else []
    )

    kept = []
    for v in videos:
        title = (v.get("title") or "").lower()
        title_nospace = title.replace(" ", "")
        if topic_lower in title or topic_nospace in title_nospace:
            kept.append(v)
        elif core_tokens and any(tok in title for tok in core_tokens):
            kept.append(v)
        else:
            print(f'    🗑️ 主题过滤: "{(v.get("title") or "")[:60]}" (不含 "{topic_name}")', file=sys.stderr)
    return kept


def search_videos(query, count, proxy=None, extra_search=10):
    """用 yt-dlp 搜索视频，按播放量降序返回前 count 个"""
    search_count = count + extra_search
    search_query = f"ytsearch{search_count}:{query}"

    cmd = [
        "yt-dlp",
        search_query,
        "--skip-download",
        "--dump-json",
        "--no-warnings",
        "--ignore-errors",
        "--flat-playlist",
    ]
    if proxy:
        cmd.extend(["--proxy", proxy])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, check=False
        )
    except subprocess.TimeoutExpired:
        print("  yt-dlp 搜索超时（120s）", file=sys.stderr)
        return []
    except FileNotFoundError:
        print("未找到 yt-dlp，请先安装：pip install yt-dlp", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0 and not result.stdout:
        print(f"  yt-dlp 报错：{result.stderr[:500]}", file=sys.stderr)
        return []

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        videos.append({
            "id": data.get("id", ""),
            "title": data.get("title", ""),
            "channel": data.get("uploader", "") or data.get("channel", ""),
            "duration_string": data.get("duration_string", ""),
            "view_count": data.get("view_count", 0) or 0,
        })

    videos.sort(key=lambda x: x["view_count"], reverse=True)
    return videos[:count]


def fetch_transcript(video_id, lang="zh-Hans", proxy=None, max_retries=5):
    """拉取视频字幕，IP 被封时换 channel 名重试"""
    languages_map = {
        "zh-Hans": ["zh-Hans", "zh", "zh-CN", "en"],
        "en": ["en", "zh-Hans", "zh"],
    }
    languages = languages_map.get(lang, [lang, "en"])

    for attempt in range(max_retries):
        try:
            import requests
            session = requests.Session()
            session.headers.update({"User-Agent": "Mozilla/5.0"})
            if proxy:
                proxy_url = proxy
                if "channel-" in proxy_url:
                    unique_tag = f"yt-{video_id[:6]}-{attempt}-{random.randint(1000, 9999)}"
                    proxy_url = proxy_url.replace("channel-", f"channel-{unique_tag}-", 1)
                session.proxies.update({"http": proxy_url, "https": proxy_url})

            api = YouTubeTranscriptApi(http_client=session)
            try:
                fetched = api.fetch(video_id, languages=languages)
            except Exception:
                fetched = api.fetch(video_id)
            return " ".join([snippet.text for snippet in fetched])

        except IP_BLOCKED_ERRORS as e:
            if attempt < max_retries - 1:
                wait = 2 + attempt * 2
                print(f"  ⚠ IP 疑似被封（{type(e).__name__}），{wait}s 后换 IP 重试 ({attempt+1}/{max_retries})", file=sys.stderr)
                time.sleep(wait)
                continue
            return f"[字幕拉取失败（IP 被封重试已耗尽）：{type(e).__name__}]"
        except Exception as e:
            err_name = type(e).__name__
            if "Disabled" in err_name or "NotFound" in err_name or "NoTranscript" in err_name:
                return f"[该视频未开启字幕：{err_name}]"
            if attempt < max_retries - 1:
                wait = 2 + attempt * 2
                print(f"  ⚠ 字幕拉取异常（{err_name}: {e}），{wait}s 后重试 ({attempt+1}/{max_retries})", file=sys.stderr)
                time.sleep(wait)
                continue
            return f"[字幕拉取失败：{err_name}: {e}]"

    return "[字幕拉取失败：重试次数耗尽]"


def format_output(query, google_pages, videos, transcripts, category=None):
    """整理成"关键词素材.md"格式"""
    lines = [f"# {query}", ""]
    if category:
        lines.append(f"> 分类：{category}")
        lines.append("")
    for i, page in enumerate(google_pages, 1):
        lines.append(f"## Google 素材 {i}")
        lines.append(f'素材来源地址：{page["url"]}')
        lines.append(f'网页标题：{page["title"]}')
        lines.append("")
        lines.append("素材内容（网页正文）：")
        lines.append(page["content"])
        lines.append("")
        lines.append("---")
        lines.append("")
    for i, video in enumerate(videos, 1):
        lines.append(f"## YouTube 素材 {i}")
        lines.append(f'素材来源地址：https://www.youtube.com/watch?v={video["id"]}')
        lines.append(f'视频标题：{video["title"]}')
        lines.append(f'频道：{video["channel"]}')
        lines.append(f'播放量：{video["view_count"]:,}')
        lines.append(f'时长：{video["duration_string"]}')
        lines.append("")
        lines.append("素材内容（字幕）：")
        lines.append(transcripts[i - 1])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def process_one_keyword(keyword, count, lang, proxy, category=None, topic=None,
                        max_duration=3600, sources="both", google_count=2):
    """按 sources 收集 Google 网页和/或 YouTube 字幕。"""
    google_pages = []
    if sources in ("both", "google"):
        google_pages = collect_google(keyword, google_count, proxy=proxy)
        google_success = sum(
            1 for page in google_pages
            if not page.get("content", "").startswith("[网页")
        )
        google_failed = len(google_pages) - google_success
        COLLECTION_STATS["google_success"] += google_success
        COLLECTION_STATS["google_failed"] += google_failed
        print(
            f"  [Google 汇总] 成功 {google_success} / 失败 {google_failed}",
            file=sys.stderr,
        )

    if sources == "google":
        if not google_pages:
            return None
        return format_output(keyword, google_pages, [], [], category=category)

    print(f"  [YouTube 搜索] {keyword}", file=sys.stderr)
    videos = search_videos(keyword, count, proxy=proxy)
    if not videos:
        print("  [YouTube 汇总] 未找到候选视频", file=sys.stderr)
        return format_output(keyword, google_pages, [], [], category=category) if google_pages else None
    COLLECTION_STATS["youtube_candidates"] += len(videos)
    print(f"  [YouTube 搜索] 找到 {len(videos)} 个候选视频", file=sys.stderr)

    # 双层过滤：先按时长剔除超长视频，再按主题相关性剔除无关 MV/同名内容
    before_duration = len(videos)
    videos = filter_by_duration(videos, max_duration)
    COLLECTION_STATS["youtube_filtered"] += before_duration - len(videos)
    effective_topic = topic or infer_topic(keyword)
    if effective_topic:
        before_topic = len(videos)
        filtered = filter_by_topic(videos, effective_topic)
        COLLECTION_STATS["youtube_filtered"] += before_topic - len(filtered)
        if not filtered:
            # 候选视频全部不相关（如搜 "farever codes" 命中 Claude Code 教程）
            # 直接判失败，不放行污染下游内容；上游会按 reason=no_related 记录
            print("  [YouTube 汇总] 候选视频全部被过滤", file=sys.stderr)
            return format_output(keyword, google_pages, [], [], category=category) if google_pages else None
        videos = filtered

    videos = videos[:count]  # 过滤后再裁到 count 个
    if not videos:
        return format_output(keyword, google_pages, [], [], category=category) if google_pages else None

    transcripts = []
    youtube_success = 0
    youtube_failed = 0
    for index, video in enumerate(videos, 1):
        print(
            f'  [YouTube {index}/{len(videos)}] {video["title"]}',
            file=sys.stderr,
        )
        transcript = fetch_transcript(video["id"], lang=lang, proxy=proxy)
        transcripts.append(transcript)
        if transcript.startswith(("[字幕拉取失败", "[该视频未开启字幕")):
            youtube_failed += 1
            COLLECTION_STATS["youtube_failed"] += 1
            print(f"    ✗ 字幕获取失败：{transcript}", file=sys.stderr)
        else:
            youtube_success += 1
            COLLECTION_STATS["youtube_success"] += 1
            print(f"    ✓ 字幕获取成功：{len(transcript):,} 字符", file=sys.stderr)
    print(
        f"  [YouTube 汇总] 成功 {youtube_success} / 失败 {youtube_failed} / "
        f"保留 {len(videos)} 个视频",
        file=sys.stderr,
    )
    return format_output(keyword, google_pages, videos, transcripts, category=category)


def run_single(args):
    """单关键词模式：默认同时收集 Google 与 YouTube。"""
    if args.proxy:
        print("使用代理：已配置", file=sys.stderr)
    else:
        print("⚠ 未使用代理，频繁调用 Google / YouTube 会触发风控", file=sys.stderr)

    output = process_one_keyword(
        args.query,
        args.count,
        args.lang,
        args.proxy,
        topic=args.topic,
        max_duration=args.max_duration,
        sources=args.sources,
        google_count=args.google_count,
    )
    if output is None:
        print("未搜到可用的 Google 网页或 YouTube 视频素材", file=sys.stderr)
        sys.exit(1)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\n已写入：{args.output}", file=sys.stderr)
    else:
        print(output)


def run_batch(args):
    """批量模式：读 keywords.json，每个关键词生成一个 md 文件"""
    if not os.path.exists(args.keywords_json):
        print(f"错误：keywords.json 不存在：{args.keywords_json}", file=sys.stderr)
        sys.exit(1)

    with open(args.keywords_json, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"错误：keywords.json 格式不合法：{e}", file=sys.stderr)
            sys.exit(1)

    categories = data.get("categories", [])
    if not categories:
        print("错误：keywords.json 里没有 categories", file=sys.stderr)
        sys.exit(1)

    total = sum(len(c.get("keywords", [])) for c in categories)
    print(f"批量模式：共 {len(categories)} 个分类，{total} 个关键词", file=sys.stderr)
    print(f"输出目录：{os.path.abspath(args.output_dir)}", file=sys.stderr)
    if args.proxy:
        print("使用代理：已配置", file=sys.stderr)
    else:
        print("⚠ 未使用代理，频繁调用 Google / YouTube 会触发风控", file=sys.stderr)

    os.makedirs(args.output_dir, exist_ok=True)

    for key in COLLECTION_STATS:
        COLLECTION_STATS[key] = 0

    success = 0
    skipped = 0
    failed = []

    for cat in categories:
        category_name = cat.get("category", "uncategorized")
        cat_slug = slugify(category_name)
        # 按分类建子目录
        cat_dir = os.path.join(args.output_dir, cat_slug)
        os.makedirs(cat_dir, exist_ok=True)

        keywords = cat.get("keywords", [])
        print(f"\n=== 分类：{category_name}（{len(keywords)} 个关键词）→ {cat_dir} ===", file=sys.stderr)

        for kw in keywords:
            kw_slug = slugify(kw)
            output_file = os.path.join(cat_dir, f"{kw_slug}.md")

            # 断点续跑：已存在则跳过
            if os.path.exists(output_file):
                print(f"  ✓ 跳过（已存在）：{kw} → {output_file}", file=sys.stderr)
                skipped += 1
                continue

            print(f"  处理：{kw}", file=sys.stderr)
            try:
                content = process_one_keyword(
                    kw, args.count, args.lang, args.proxy,
                    category=category_name,
                    topic=args.topic,
                    max_duration=args.max_duration,
                    sources=args.sources,
                    google_count=args.google_count,
                )
                if content is None:
                    print(f"    ⚠ 未搜到可用素材，跳过", file=sys.stderr)
                    failed.append({"keyword": kw, "category": category_name, "reason": "no Google pages / no related videos"})
                    continue
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"    ✓ 写入：{output_file}", file=sys.stderr)
                success += 1
            except Exception as e:
                print(f"    ✗ 失败：{type(e).__name__}: {e}", file=sys.stderr)
                failed.append({"keyword": kw, "category": category_name, "reason": f"{type(e).__name__}: {e}"})

    # 汇总
    print("\n" + "=" * 50, file=sys.stderr)
    print(f"批量完成：成功 {success} / 跳过 {skipped} / 失败 {len(failed)} / 总计 {total}", file=sys.stderr)
    print(f"输出目录：{os.path.abspath(args.output_dir)}", file=sys.stderr)
    print(
        "Google 正文："
        f"成功 {COLLECTION_STATS['google_success']} / "
        f"失败 {COLLECTION_STATS['google_failed']}",
        file=sys.stderr,
    )
    print(
        "YouTube 字幕："
        f"成功 {COLLECTION_STATS['youtube_success']} / "
        f"失败 {COLLECTION_STATS['youtube_failed']} / "
        f"过滤 {COLLECTION_STATS['youtube_filtered']} / "
        f"候选 {COLLECTION_STATS['youtube_candidates']}",
        file=sys.stderr,
    )
    if failed:
        print("\n失败列表：", file=sys.stderr)
        for f_item in failed:
            print(f"  - [{f_item['category']}] {f_item['keyword']}: {f_item['reason']}", file=sys.stderr)


def main():
    load_env_file()
    parser = argparse.ArgumentParser(
        description="Google 网页正文 + YouTube 字幕批量收集（支持单关键词 / keywords.json 批量）"
    )

    # 互斥的输入源（必须二选一）
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--query", help='单个关键词（如 "farever classes"）')
    input_group.add_argument(
        "--keywords-json",
        help="keywords.json 文件路径（接上一章 ChatGPT 分类聚合输出的 JSON）",
    )

    parser.add_argument("--count", type=int, default=2, help="每个关键词抽取视频数量（默认 2）")
    parser.add_argument("--google-count", type=int, default=2, help="每个关键词抽取 Google 网页数量（默认 2）")
    parser.add_argument(
        "--sources",
        choices=["both", "google", "youtube"],
        default="both",
        help="收集渠道：both / google / youtube（默认 both）",
    )
    parser.add_argument("--lang", default="zh-Hans", help="字幕语言（默认 zh-Hans，回退 en）")
    parser.add_argument(
        "--proxy",
        help="临时覆盖 .env 代理配置的 URL（正常使用直接读取 USE_PROXY 和 TUNNEL_*）",
    )
    parser.add_argument(
        "--topic",
        help="游戏主题名（用于过滤无关视频，如 farever）。不填则从关键词首单词推断",
    )
    parser.add_argument(
        "--max-duration",
        type=int,
        default=3600,
        help="视频最大时长（秒，默认 3600=1 小时）；超过会被过滤掉",
    )

    # 输出选项
    parser.add_argument("--output", help="单关键词模式：输出文件路径（不填则打印到 stdout）")
    parser.add_argument(
        "--output-dir",
        default="./keywords-materials",
        help="批量模式：输出目录（默认 ./keywords-materials/，按分类建子目录，每个关键词一个 md 文件）",
    )

    args = parser.parse_args()
    if not args.proxy:
        args.proxy = proxy_from_env()

    if args.query:
        run_single(args)
    else:
        run_batch(args)


if __name__ == "__main__":
    main()
