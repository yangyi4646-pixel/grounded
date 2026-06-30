# Return-to-Spec List / 实现回流规格清单

当实现发现 SPEC 缺失、冲突或产品级决策未确认时使用。只停止受影响路径,不要默认整包冻结。

| Gap ID | SPEC Anchor | Observation / Evidence | Affected Path | Decision Needed | Suggested Default | Stop / Continue Boundary | Owner / Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R2S-1 |  |  |  |  |  |  | `open / confirmed / resolved` |

规则:
- Observation 必须是代码、运行时、SPEC、PRD 或评审反馈证据,不能写模型感觉。
- Suggested Default 只能是待确认建议,不得直接编码。
- Stop / Continue Boundary 要写清哪些 UI 路径停、哪些 recon 或无关单元可继续。
- 规格更新后,在 SPEC 决策日志记录日期、actor、变更和出处。
