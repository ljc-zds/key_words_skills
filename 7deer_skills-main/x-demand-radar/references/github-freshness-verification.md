## GitHub Repo Freshness Verification

⚠️ **X热度 ≠ 项目新。Must verify EVERY GitHub-linked signal before ranking.**

```javascript
// Run on GitHub repo page (browser_console)
const createdEl = document.querySelector('relative-time');
const createdAt = createdEl?.getAttribute('datetime') || '';
const daysSinceCreated = (new Date() - new Date(createdAt)) / (1000 * 60 * 60 * 24);

let freshnessMultiplier;
if (daysSinceCreated < 7) freshnessMultiplier = 1.0;      // 🆕 新品
else if (daysSinceCreated < 30) freshnessMultiplier = 0.7; // 📈 上升
else if (daysSinceCreated < 90) freshnessMultiplier = 0.3; // ⚠️ 旧项目回锅
else freshnessMultiplier = 0;                               // 💀 排除
```

### Catastrophic Case

UI-TARS-desktop (bytedance) — 29K GitHub stars, 1.4K X likes, hotScore 5,505, but repo existed for months. X post was new, project was not.

CEO caught it: "这个项目明显是个旧项目哦，虽然X帖子是昨天的。"

Applied `freshnessMultiplier = 0` → excluded from ranking entirely. No arbitrage value.

### Rules

- For non-GitHub signals (API launches, product releases, waitlists): default `freshnessMultiplier = 0.8`
- If a product page has a visible release date, extract and use actual age
- Signals with `freshnessMultiplier = 0` are EXCLUDED from all reports
- This is mandatory Step 2.5 — never skip it, even if it means extra browser navigations
