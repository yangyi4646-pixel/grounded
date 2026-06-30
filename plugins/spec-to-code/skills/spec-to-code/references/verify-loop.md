# 验证闭环(Verification Loop)

完成口径:可运行门通过、SPEC-code 契约一致、视觉证明已检查;不可执行门必须明确列为 `unchecked + reason`。

报告使用 `templates/verification-report.md`。机械检查包括:`scripts/check_completion_tier.py <report.md>` 检查完成层级,`scripts/check_implementation_boundary.py <report-or-contract.md>` 检查边界表,`scripts/check_product_structure_preflight.py <report-or-contract.md>` 检查多对象/详情 UI 的 Product Structure Preflight,`scripts/check_runtime_visual_proof.py <report-or-proof.md>` 检查样式/视觉工作声明中的真实渲染节点证明。

## 验证门

1. **类型检查(Types)**
   运行项目 typecheck,或当前项目中最窄且可靠的等价命令。

2. **Lint / 静态检查**
   运行项目 lint/check 命令。若项目命令只检查 git diff 且可能 no-op,使用直接针对文件/路径的命令兜底。

3. **测试(Tests)**
   对改动的纯逻辑和受影响流程运行单元或集成测试。从组件中抽出的纯逻辑必须有测试。纯 UI 渲染不需要脆弱测试,除非它承载行为。

4. **路由 / 入口证明(Route / Entry Proof)**
   证明用户能到达该面:路由注册、权限 wrapper、导航入口、deep link,或宿主路由等价证据。

5. **审批 / 生命周期门(Approval / Lifecycle Gate)**
   任务触发审批、发布/下线/删除、pending 可编辑性、撤回/重新提交、回调/外部处理、配置面、版本生效或下游消费读取时,证明 SPEC 有 Approval / Lifecycle Gate,且包含确认范围、来源、受影响/阻塞单元。缺失时,将受影响状态或消费路径回流 `prd-to-spec`。

6. **P0/P1 确认状态门(Confirmation Status Gate)**
   检查 SPEC / gaps / handoff 是否存在 P0/P1/P2 和确认截止点。P0 一律停止受影响实现路径。P1 若影响当前实现单元,且截止点为 `before spec-to-code` 或 `before affected unit implementation`,实现前升级为受影响单元 P0 并回流 `prd-to-spec`。不得把 `推荐默认(待确认)` 写成代码默认。

7. **产品结构实现前检查(Product Structure Preflight)**
   多对象、字段映射、卡片/表格/详情、头部/展开区、展开/收起 UI,必须证明 SPEC 有当前页面主对象、Information Ownership Matrix(信息归属矩阵)、头部摘要职责、展开区职责、不重复展示规则、当前页面不承载的信息。
   5 项 canonical 定义见 `prd-to-spec/references/information-ownership.md`(随其更新)。
   每个 `yes` 需要 SPEC 锚点/来源;每个 `no` 需要停止/回流决策和受影响/阻塞路径;每个 `N/A` 需要原因/来源。缺失时,UI 编辑前先把受影响实现路径回流 `prd-to-spec`。

8. **视觉证明(Visual Proof)**
   使用 profile 中的项目预览方式。验证视觉契约规定的状态:默认、loading/empty/error、读/写、预填、非法、边界值,以及相关响应式/容器变体。

9. **运行时视觉证明(Runtime Visual Proof)**
   样式改动必须证明真实渲染节点:token/style readback、computed style、screenshot、DOM node、bounding box,或显式 unchecked reason。wrapper 承载的文字、badge/tag、table cell、tooltip、icon、status mark 需要节点级证明;父级 class 证明不够。

10. **SPEC-code 契约 diff**
   对比代码和 SPEC 冻结值:ids、分隔符、枚举、存储键、对象归属、路由/用户路径、Scope Boundary、以及 SPEC 冻结的视觉契约项。

11. **可用性走查(Usability Walkthrough)— fresh 子代理**
   非纯逻辑、非 XS 的 UI 单元,出码且原型在本地可跑时,由**未参与实现的 fresh 子代理**执行(作者不评自己的可用性)。
   先确认 localhost 端口**真正编译的仓库/worktree**;装作没看过实现,照 SPEC 的用户目标/验收**冷启动驱动**原型(点/填/跳),逐步用四段式记录:**我以为会… / 实际… / 卡在哪 / 严重度(卡死 / 绊脚 / 小瑕)**。
   每条改法**锚到现有 token / 组件 / 兄弟页**,不用凭空理想标准;拿不准标「待你拍」。产出清单落盘 `docs/specs/<需求>/`,对话给 3–5 行摘要。
   本门只评"第一次来的人**干不干得成**",**不打分、不脚本硬验、不自动改、不掺视觉长相**(长相归门 8/9 与品味层)。无法驱动浏览器时记 `unchecked + reason`。
   指引见 `references/usability-walkthrough.md`。

## 视觉证明要求

- 截图或 DOM 证明必须指向真实渲染 surface,不能只指组件源码。
- 样式改动尽量提供真实节点证明:computed style、bounding box、可访问文本、真实节点 class、截图对比。
- 无法访问浏览器时,记录为 `unchecked + reason`;不得声称已对齐。
- 控件出现/消失的状态切换要检查布局不变量:行高、容器 padding、footer 位置、overflow。
- 新页面或组合面改动时,应与 profile 中的 canonical sibling 做成对比较。
- 语义资产要证明:icon/badge/status 名称、尺寸、字重、颜色角色、状态映射。

## 完成层级(Completion Tiers)

| 层级 | 含义 |
| --- | --- |
| implementation complete | 代码已写完,并按复用、路由、数据、范围契约自查 |
| local validation complete | types/lint/tests/route proof 通过;不可用门已列出 |
| visual alignment complete | 必要状态的视觉契约证明通过 |
| usability walkthrough complete | fresh 子代理可用性走查已出清单;卡死项已澄清或标「待你拍」 |
| design-side release complete | 设计负责人已验收 taste / fit |

只能报告已达到的最高层级。任一门 unchecked 时,不得只说“done”。

## 回流 SPEC 协议(Return-to-Spec Protocol)

若实现中发现缺失、冲突或产品级决策:

1. 复制 `templates/return-to-spec-list.md`,写明锚点、观察证据、影响和建议决策。
2. 停止受影响实现路径。
3. 将决策回流 `prd-to-spec`。
4. SPEC 或决策日志更新后再恢复。

不得把路径级回流扩大成整包冻结。只有在不冻结、不渲染、不验证缺失产品决策的前提下,才可继续无关 recon、证据采集和不依赖该决策的实现工作。

P1 到期规则:若 SPEC 中某 P1 的确认截止点已经到达当前阶段(before spec-to-code / before affected unit implementation),且该 P1 影响当前单元,它在实现端等同 P0。停止该单元实现,回流确认;不得按推荐默认编码。

源码/profile 证据不能覆盖 SPEC 或 PRD,只能暴露 gap。

Scope Boundary gap 是产品级决策。Affected Surfaces / Non-Goals / Propagation Rule 缺失或矛盾时,不得推进跨面编辑、共享 renderer 改动或语义资产替换。

信息归属 gap 是产品级决策。当前页面主对象、头部 vs 展开职责、不重复规则缺失或矛盾时,不得推进卡片/折叠/表格/详情重写。

Gate 脚本只能证明必要结构和证据位已填写,不能证明产品决策正确;产品决策仍需要 SPEC、PRD、用户确认、决策日志或代码证据。
