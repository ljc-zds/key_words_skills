<!-- 仅限生财学员使用，禁止外传 -->
<!-- 仅限生财学员使用，禁止外传 -->
<!-- 仅限生财学员使用，禁止外传 -->
<!-- 仅限生财学员使用，禁止外传 -->
<!-- 仅限生财学员使用，禁止外传 -->
<!-- 仅限生财学员使用，禁止外传 -->
# Google 与 YouTube 内容收集自动化软件使用说明

## 领取说明

这是一套同时覆盖两个渠道的内容收集自动化软件。
输入一个关键词或一份关键词 JSON，即可批量完成 Google 网页素材和 YouTube 字幕素材的搜索、提取与 Markdown 保存。

## 软件包含什么

### Google 搜索与正文提取模块

输入关键词后，自动搜索排名靠前的网页，提取网页标题、来源地址和正文内容，并按关键词保存为独立的 Markdown 文件。

**处理流程：批量输入关键词 → Google 搜索 → 筛选结果 → 提取网页正文 → 按关键词保存。**

### YouTube 搜索与字幕提取模块

脚本放置位置：`content_collection_batch.py`。**脚本同时支持 Google 和 YouTube，正常运行时默认收集两个渠道。**

输入关键词后，自动搜索高播放量视频，过滤超长视频和主题不相关视频，提取字幕并保存为 Markdown 文件。

**处理流程：批量输入关键词 → YouTube 搜索 → 时长与主题双层过滤 → 提取字幕 → 按关键词保存。**

## 使用前准备

### 1. 安装 Python3

建议使用 Python3 3.10 或更高版本。

### 2. 安装双渠道软件依赖

```bash
# 安装 Google 网页解析、YouTube 搜索和字幕提取依赖
pip install requests beautifulsoup4 yt-dlp youtube-transcript-api
```

### 3. 配置 API 和代理

配置文件放置位置：`.env`。

先创建 `.env`，再填写自己的 API Key 和代理信息。**凭证只能放在 `.env`，禁止写进 Python3 脚本或提交到公开仓库。**

#### 步骤 1：搜索

| 服务         | 配置变量             | 技术原理                                      | 获取方式                                 | 费用                  |
| ---------- | ---------------- | ----------------------------------------- | ------------------------------------ | ------------------- |
| Google 搜索  | `SERPER_API_KEY` | 调用 Serper API 获取 Google 搜索结果，返回标题、URL 和摘要 | [serper.dev](https://serper.dev/) 注册 | 免费额度 2500 次，超出后按量付费 |
| YouTube 搜索 | 无需 API Key       | `yt-dlp` 解析 YouTube 搜索结果，读取视频标题、播放量和时长    | 无需注册                                 | 免费                  |

#### 步骤 2：提取

| 服务 | 配置变量 | 技术原理 | 获取方式 | 费用 |
|---|---|---|---|---|
| Google 网页正文 | `JINA_API_KEY`（推荐） | 调用 Jina Reader 提取网页正文，并清理导航、广告和无关标签 | [jina.ai](https://jina.ai/) 注册 | 有免费额度，大量调用需要付费 |
| YouTube 字幕 | 无需 API Key，需要代理 | `youtube-transcript-api` 调用 YouTube 字幕接口 | 无需注册 | 免费，但 IP 可能被限流或封锁 |
| IP 代理池 | `USE_PROXY=true` | 为 YouTube 字幕请求提供可轮换的出口 IP | [青果网络](https://www.qg.net/etsurpvq) | 按流量计费 |

`.env` 完整格式：

```bash
# Google 搜索：在 serper.dev 注册后填写
SERPER_API_KEY=你的_Serper_API_Key

# Google 网页正文：在 jina.ai 注册后填写
JINA_API_KEY=你的_Jina_API_Key

# 大规模提取 YouTube 字幕时开启代理
USE_PROXY=true
TUNNEL_HOST=你的隧道域名
TUNNEL_PORT=你的隧道端口
TUNNEL_USER=你的用户名
TUNNEL_PASS=你的密码
TUNNEL_PROXY_FORMAT=tagged
TUNNEL_CHANNEL_PREFIX=channel
TUNNEL_TTL=60
```

配置关系必须分清：

- **Google 搜索读取 `SERPER_API_KEY`。**
- **Google 网页正文优先读取 `JINA_API_KEY`；未配置时回退到本地网页清洗。**
- **YouTube 搜索和字幕都不需要 API Key。**
- **YouTube 字幕批量提取依赖代理池，不要把 `SERPER_API_KEY` 或 `JINA_API_KEY` 当成 YouTube 凭证。**

### 4. 准备关键词 JSON

输入文件放置位置：`keywords.json`。

```json
{
  "categories": [
    {
      "category": "Classes",
      "keywords": [
        "farever classes",
        "farever class tier list"
      ]
    },
    {
      "category": "Codes",
      "keywords": [
        "farever codes"
      ]
    }
  ]
}
```

`categories` 是分类数组，`category` 是分类名称，`keywords` 是需要收集素材的关键词数组。

## 双渠道内容收集软件怎么用

cd material-collection/

## 单独运行某个渠道

```bash
# 只搜索 Google 并提取网页正文
python3 content_collection_batch.py \
  --query "farever classes" \
  --sources google \
  --google-count 2

# 只搜索 YouTube 并提取视频字幕
python3 content_collection_batch.py \
  --query "farever classes" \
  --sources youtube \
  --count 2
```

### 处理单个关键词

```bash
# 临时搜索单个关键词，并直接写入指定文件
python3 content_collection_batch.py \
  --query "farever classes" \
  --output farever-classes.md
```

### 主要用法：批量处理关键词 JSON

**关键词 JSON 是最重要的输入。**它直接承接前一步已经完成的关键词分类，让软件一次处理全部分类和关键词。

```bash
# 读取分类后的关键词 JSON，收集双渠道素材，并把每个关键词保存为独立文件
cd material-collection

python3 content_collection_batch.py \
  --keywords-json keywords.json \
  --output-dir Farever内页素材
```

运行后，每个关键词对应一个 Markdown 文件，内容至少包括：

```markdown
# farever classes

## Google 素材 1
素材来源地址：https://example.com/page-1
网页标题：页面标题

素材内容：
提取后的网页正文

## Google 素材 2
素材来源地址：https://example.com/page-2
网页标题：页面标题

素材内容：
提取后的网页正文
```

## 输出目录

批量输出目录放置位置：`关键词内页素材/`。

```text
关键词内页素材/
├── classes/
│   ├── farever-classes.md
│   ├── farever-best-class.md
│   └── farever-class-tier-list.md
└── codes/
    └── farever-codes.md
```

**每个关键词生成一个独立文件，已经生成的文件自动跳过。**运行中断后重新执行同一条批量命令，即可从未完成的关键词继续处理。