# 产品结构实现前检查(Product Structure Preflight)

> `yes` 必须有 SPEC 锚点/来源和实现决策。`no` 必须有停止/回流决策和受影响/阻塞路径。`N/A` 必须有明确原因和来源;裸 `N/A` 无效。

| 必要 SPEC 契约(Required SPEC Contract) | 是否存在(Present?) | SPEC 锚点 / 来源(SPEC Anchor / Source) | 实现决策(Implementation Decision) | 受影响 / 阻塞路径(Affected / Blocked Path) |
| --- | --- | --- | --- | --- |
| 当前页面主对象(Current page main object) | yes / no / N/A |  |  |  |
| 信息归属矩阵(Information Ownership Matrix) | yes / no / N/A |  |  |  |
| 头部摘要职责(Header summary responsibility) | yes / no / N/A |  |  |  |
| 展开区职责(Expanded-detail responsibility) | yes / no / N/A |  |  |  |
| 不重复展示规则(Do-not-repeat display rule) | yes / no / N/A |  |  |  |
| 当前页面不承载的信息(Information this page does not carry) | yes / no / N/A |  |  |  |

决策(Decision):
- [ ] 继续(Proceed):所有必要结构契约都存在,或已显式 N/A + 原因。
- [ ] 停止(Stop):改 UI 前回流 `prd-to-spec`。
