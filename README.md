# gds-agent-plugins

A Claude Code / Codex **plugin marketplace** containing a two-skill pipeline that
turns a thin requirement into front-end code **anchored to your existing product** —
reusing existing pages, components, fields and routes instead of letting the AI
invent new interactions or design patterns.

> 把粗需求「锚」到你现有的产品上:复用已有页面 / 交互 / 字段 / 路由,堵住 AI 自己发明交互、发明设计。

## The two skills

| Skill | 干什么 | What it does |
|---|---|---|
| **prd-to-spec** | 把一句话/薄需求/PRD/纪要蒸馏成可执行 SPEC,冻结复用契约 | Distill a thin requirement / PRD into an executable SPEC with a frozen reuse contract |
| **spec-to-code** | 把冻结的 SPEC 转成前端代码或原型 | Turn a frozen SPEC into front-end code or a prototype |

```
粗需求
  → 【prd-to-spec:锚需求,出 SPEC】
  → §0 冻结契约(复用哪些件 · 字段映射 · 路由/入口 · 冻结值)
  → 【spec-to-code:锚代码,出前端】
  → grounded 的 SPEC / 代码
```

## 它只干 4 件活(记这 4 件)

| | 活 | 干什么 |
|---|---|---|
| ① | **锚到现有产品** | 复用现有页面 / 组件 / 字段 / 路由,别发明 |
| ② | **补全** | PRD 没说的也补:空态/默认/loading · 错误/失败/反馈 · 权限 · 数据一致性 · 谁读到 |
| ③ | **信息边界** | 不冗余、不把 A 的信息乱搬到 B 的页面 |
| ④ | **工作流 / 生命周期** | 对象在状态间流转时,复用现有审批 / 状态机 |

每个 skill 目录下的 `scripts/check_*.py` 是这 4 件活的**确定性地板**——脚本 PASS 只说明
结构合规,内容对不对仍是判断,交人 / judge。完整说明见 `OVERVIEW.md`。

## Install

```
/plugin marketplace add yangyi4646-pixel/gds-agent-plugins
/plugin install prd-to-spec@gds-agent-plugins
/plugin install spec-to-code@gds-agent-plugins
```

Then invoke with `/prd-to-spec` and `/spec-to-code`.

本地试装(克隆后):

```
/plugin marketplace add ./gds-agent-plugins
```

## Layout

```
gds-agent-plugins/                       ← repo = marketplace
  .claude-plugin/marketplace.json
  plugins/
    prd-to-spec/
      .claude-plugin/plugin.json
      skills/prd-to-spec/                 ← SKILL.md + references / templates / scripts / profiles
    spec-to-code/
      .claude-plugin/plugin.json
      skills/spec-to-code/
  OVERVIEW.md
```

## Notes

- Skills are static markdown + deterministic Python gates; they run inside a
  supporting harness (Claude Code / Codex). They are **product-agnostic** — point
  them at any front-end repo and they anchor to *that* repo's conventions.
- Codex 用户:`skills/<name>/SKILL.md` 同一份复用,放进 `~/.codex/skills/` 或软链即可。

## License

MIT — see [LICENSE](LICENSE).
