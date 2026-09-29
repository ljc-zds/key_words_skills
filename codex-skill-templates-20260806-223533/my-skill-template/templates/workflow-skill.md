---
name: workflow-skill-name
description: "Use when <workflow trigger>. Guides the agent through <workflow outcome>. Do not use when <boundary>; escalate when <handoff condition>."
version: 1.0.0
author: Personal Codex
license: MIT
metadata:
  codex:
    tags: [workflow]
    related_skills: []
---

# Workflow Skill Name

## 你是谁

你是 ...

## 适用场景

- ...

## 不适用场景

- ...

## 工作流程

1. 先看 `references/rules.md`
2. 根据规则判断类型或路径
3. 选择 `templates/` 下的对应模板
4. 补全必要信息
5. 输出结果给用户审核
6. 不确定时按转人工/询问规则处理

## 类型与处理

| 类型 | 判断标准 | 处理方式 | 模板 |
| --- | --- | --- | --- |
| type-a | ... | ... | `templates/type-a.md` |
| type-b | ... | ... | `templates/type-b.md` |

## 红线

详见 `references/red-lines.md`。

## 输出格式

```markdown
## 判断

## 草稿/结果

## 需要用户确认的点
```

## Verification Checklist

- [ ] 已读取相关 references
- [ ] 已选择正确模板
- [ ] 已检查红线
- [ ] 已标注不确定点
