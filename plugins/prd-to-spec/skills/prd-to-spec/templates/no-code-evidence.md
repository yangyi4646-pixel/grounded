# No-Code Evidence / 无代码证据降级

用于早期概念、纯 PRD 阶段、无仓库访问权限、或本轮默认不依赖现有系统能力的场景。它不是通过证明,只是诚实说明哪些证据不可用。

| Field | Value |
| --- | --- |
| Evidence status | `no-code / unavailable / not-needed` |
| Reason |  |
| Affected assumptions |  |
| What cannot be verified |  |
| Provisional defaults allowed? | `yes/no + scope` |
| Required confirmation before freeze |  |
| Next recon trigger |  |

规则:
- 不能用本模板替代 PRD、用户确认或决策日志。
- 涉及权限、生命周期、数据读写、消费读取、对象边界、字段语义时,仍需 gap 确认。
- 如果后续拿到代码仓库或实现证据,必须刷新 Evidence Profile。
