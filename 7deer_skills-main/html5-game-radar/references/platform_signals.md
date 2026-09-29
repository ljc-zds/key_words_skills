# 平台首发特点与监测方法

## 1. itch.io

**为什么重要：**
- 最大的独立 HTML5 游戏首发平台
- 开发者直接发布，没有中间商
- 第一时间发现新游戏

**监测方法：**
```
URL: https://itch.io/games/tag-html5/sort:-created
滚动收集新游戏卡片
重点字段：发布日、票数、浏览量
```

**信号解读：**
| 指标 | 高价值信号 | 低价值信号 |
|------|-----------|-----------|
| 票数 | > 100 👍 | < 10 👍 |
| 浏览量 | > 5000 views | < 500 views |
| 开发者 | 有其他游戏/社群 | 首次发布 |
| 标签 | html5 + 明确类型 | 只有 html5 |

**RSS 备选：**
- `https://itch.io/feed`（需要登录）

---

## 2. Reddit r/webgames

**为什么重要：**
- 玩家发现新游戏的第一社区
- 真实用户体验，非营销内容
- 帖子突然火了 = 游戏有传播力

**监测方法：**
```bash
npx tsx reddit.ts new webgames --limit 50
npx tsx reddit.ts search "html5 OR browser game" --sub webgames --sort new --limit 20
```

**信号解读：**
| 指标 | 高价值信号 | 低价值信号 |
|------|-----------|-----------|
| upvotes | > 50 | < 10 |
| comments | > 20 | < 5 |
| 标题含游戏名 | ✅ 有 | ❌ 没有 |
| 帖子时间 | < 3 天 | > 7 天 |

---

## 3. Google Trends

**为什么重要：**
- 搜索量爆发 = 套利窗口
- 可发现还没被内容页覆盖的游戏

**监测方法：**
```
搜索 games related trending queries:
"why is [game] so popular"
"[game] game unblocked"
"play [game] online free"
```

**信号解读：**
- Google 搜索自动补全出现游戏名 = 搜索量已达一定规模
- YouTube 搜索量 > Google 搜索量 = 视频营销期，适合视频配套文章

---

## 4. X/Twitter

**为什么重要：**
- 游戏病毒扩散最早信号
- 开发者/主播 announcement
- 转发链 = 传播路径

**监测搜索词：**
```
(new game OR new free game OR "just launched") (html5 OR browser game)
"everyone is playing" "[game name]"
"this game is so good" html5 OR browser
itch.io "first look" OR "just released"
```

**信号解读：**
- 开发者自己发推宣布 = 最早信号
- 大账号转发 = 即将爆发
- 普通用户发 gameplay = 已经爆发

---

## 5. CrazyGames

**为什么重要：**
- HTML5 游戏专业平台，流量可观
- 有编辑推荐机制

**监测 URL：**
```
主页: https://www.crazygames.com
新游戏: https://www.crazygames.com/browse/new
编辑推荐: https://www.crazygames.com/browse/editorschoice
```

**注意：** URL 结构可能变化，用 browser 打开主页后找导航

---

## 6. YouTube

**为什么重要：**
- 游戏内容爆发滞后于社交媒体
- 新游戏首批视频 = 流量入口

**监测搜索词：**
```
"new game" "no download" OR "play now" html5
"[game name] gameplay" -let’s play -walkthrough
```

---

## 优先级排序

| 优先级 | 平台 | 时效性 | 可靠性 |
|--------|------|--------|--------|
| ⭐⭐⭐⭐⭐ | itch.io | 最高 | 高 |
| ⭐⭐⭐⭐ | Reddit r/webgames | 高 | 高 |
| ⭐⭐⭐⭐ | X/Twitter | 最高 | 中 |
| ⭐⭐⭐ | Google Trends | 中 | 高 |
| ⭐⭐⭐ | CrazyGames | 中 | 高 |
| ⭐⭐ | YouTube | 低 | 中 |

**建议工作流：**
1. itchio 为主（发现最多新游戏）
2. Reddit 为辅（玩家验证）
3. X/Twitter 为预警（最早信号）
4. Google Trends 验证（套利窗口确认）
