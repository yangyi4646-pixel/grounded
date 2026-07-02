---
name: spec-to-code
description: >-
  Use when 需要把已有 SPEC 转成前端代码或前端原型,或用户要求「按 SPEC 生成前端代码、出原型、
  spec→code、实现这个前端单元、生成新建/编辑页」. 也用于 agent 可能手写控件、偏离宿主产品视觉语法、
  跳过路由/入口接线、猜冻结值,或在可运行检查和视觉证明前宣称完成的场景。不用于后端实现或重新决定 SPEC。
---

# SPEC -> 前端代码

本 skill 消费已冻结的 SPEC 或 mini-spec,只实现前端代码,不重新拍产品事实。对象模型、状态、枚举、标识符、路由、Scope Boundary、验收口径属于 SPEC;实现端只能复制和验证。缺契约时停止受影响路径,用 return-to-spec list 回流。

## 铁律

```text
NO CODE GENERATION WITHOUT AN ESTABLISHED ANCHOR CODEBASE.
NO IMPLEMENTATION OUTSIDE SPEC SCOPE BOUNDARY.
NO COMPLETION CLAIM WITHOUT RUNNABLE CHECKS AND VISUAL/CONTRACT PROOF.
NO STYLE CLAIM WITHOUT RENDERED-NODE EVIDENCE.
NO MULTI-OBJECT UI IMPLEMENTATION WITHOUT PRODUCT-STRUCTURE PREFLIGHT.
NO IMPLEMENTATION OF AFFECTED UNITS WITH UNCONFIRMED P0/P1 CONTRACT GAPS.
```

## 默认路径

0. **确立锚定目标(anchor target)**:进实现前先确认要复用/锚定的宿主代码仓。当前工作目录即目标仓、且能定位 SPEC 引用的页面/组件/路由 → 一行声明「锚定到 `<repo>`」后继续。**无宿主代码仓,或 SPEC 引用的组件/路由/字段在当前仓定位不到 → 停,先问用户:锚定哪个本地项目(给路径)?还是无宿主的全新原型(确认后才按原型走)?锚定目标未确立前,不生成任何代码。**
1. **读 SPEC**:读取当前单元、§0 契约、Scope Boundary、P0/P1/P2 gap、确认截止点、相关 gate、handoff notes。
2. **证据档案**:非 XS UI 读取或生成 Implementation Evidence Profile;XS 可用 micro-profile。无代码仓库或早期原型时(须先过第 0 步确立锚定/原型口径),记录 unchecked reason,不得伪造证据。
3. **实现前短表**:用 `templates/implementation-boundary.md` 记录允许面、禁止面、传播规则、确认状态、profile 证据、复用目标、视觉契约和验证命令。
4. **触发式 preflight**:只在命中路由表条件时读取对应 reference/template/script。凡路由命中 `templates/*` + `scripts/check_*.py` 的 gate,必须复制模板标题/表头并运行脚本;不得只用散文转述。
5. **窄范围实现**:只改 SPEC 允许的 surface;局部反馈默认只作用当前面。
6. **验证闭环**:运行可用 type/lint/test/route proof/visual proof,以及非 XS UI 的**可用性走查(verify 第 11 门,fresh 子代理)**;不可执行项写 `unchecked + reason`。
7. **按层级报告**:只报告实际达到的最高层级,不要用一个 done 覆盖未检项。

## Reference Routing

| 触发 | 读取/使用 |
| --- | --- |
| 起手无宿主代码仓 / SPEC 引用在当前仓定位不到 | 停 + 请用户指定本地项目路径或确认全新原型(见默认路径第 0 步、下方「实现前拦截」) |
| 没有实现证据档案 | `references/profile-bootstrap.md` |
| 新写 UI 或可能偏离宿主语法 | `references/reuse-first.md`, `references/visual-contract.md` |
| 有复用清单/reuse-list(证据档/Exact 源/No-match 理由/否定结论 grep) | `scripts/check_reuse_first.py`(PASS=presence-only:无复用清单→not-applicable;Exact 是否真精确/复用判断对否交 judge/人) |
| 样式或视觉改动 | `templates/runtime-visual-proof.md`, `scripts/check_runtime_visual_proof.py` |
| 多对象、字段映射、详情、卡片、表格、头部/展开、重复信息 | `templates/product-structure-preflight.md`, `scripts/check_product_structure_preflight.py` |
| Scope Boundary / P0/P1 / 验证层级 | `references/verify-loop.md`, `templates/verification-report.md` |
| 原型可跑、评第一次来的人用不用得懂(可用性) | `references/usability-walkthrough.md`(verify 第 11 门,fresh 子代理) |
| 实现发现 SPEC 缺失、冲突、PRD 路径被源码覆盖;拟定交互形态暗示了被 SPEC/PRD 约束禁止的操作;或发现自己在写「切换清空 / 禁用 / 自动纠正」这类唯一目的是守住某条约束的补丁代码 | `templates/return-to-spec-list.md` |
| 实现边界需要机械检查 | `scripts/check_implementation_boundary.py` |
| 完成层级需要机械检查 | `scripts/check_completion_tier.py` |

> 脚本 PASS = 结构/presence 合规,不证明业务正确;语义与业务判对交 judge/人。

## 实现前拦截

- 锚定代码仓未确立(无宿主仓,或 SPEC 引用的 surface 在当前仓定位不到):停止全部实现,请用户指定本地项目路径或显式确认全新原型;不得凭空生成。
- SPEC 缺 Scope Boundary,且任务可能影响兄弟页、列表/详情、配置/消费面、共享 renderer 或语义资产:停止受影响路径。
- 当前单元存在 P0:停止受影响路径。
- P1 影响当前单元,且截止点是 `before spec-to-code` 或 `before affected unit implementation`:升级为该单元 P0。
- 多对象/字段映射/头部展开 UI 缺当前页面主对象、信息归属矩阵、头部职责、展开职责、去重规则、当前页不承载信息:停止受影响路径。
- 视觉或样式声明没有真实渲染节点、computed style、DOM、bounding box、screenshot 或 unchecked reason:不得声称视觉对齐。
- 冻结约束的交互后果是产品决策:拟定 UI 会让用户攒出违反 SPEC/PRD 约束的状态(如 可浏览多账户列表 vs 同源约束),或需要写「切换清空 / 禁用 / 自动纠正」类守约补丁而 SPEC 未冻结该行为(§0 无「边界规则与交互后果」行):停止受影响路径,写 return-to-spec 一行冒泡;**禁止自打创可贴消化**。

## Return-to-Spec List

实现中发现产品级缺口时,不要在实现端默认补齐。复制 `templates/return-to-spec-list.md`,逐条写:

- 缺口 ID、SPEC 锚点、观察证据、受影响路径。
- 需要谁确认、建议决策、可继续/必须停止的范围。
- 回流后由 prd-to-spec 更新 SPEC 或决策日志,再恢复实现。

路径级缺口只停止依赖它的实现路径;不依赖该决策的 recon、证据采集和无争议实现可以继续,但不能冻结或编码缺失契约。

## 输出规则

- 必须报告使用或生成的 profile/micro-profile 路径、范围、置信度和负发现。
- 必须报告实现边界表、复用清单、视觉契约、验证结果、unchecked 项和原因。
- 触发审批/生命周期、多对象结构、视觉证明时,必须报告对应 gate 结果;未触发也要写 N/A + 原因。
- SPEC-code contract diff 必须覆盖 ids、枚举、存储键、对象归属、路由/用户路径、Scope Boundary 和 SPEC 冻结的视觉契约项。
- 完成层级只能是:implementation complete / local validation complete / visual alignment complete / usability walkthrough complete / design-side release complete。

## 禁止的捷径

- 用源码里更顺手的路径覆盖 PRD 或 SPEC 明写入口。
- 把 P1 推荐默认写成代码默认。
- 用卡片、折叠、容器、间距修复主对象/信息归属缺失。
- 找到同名组件就当能力已证明。
- class name 已加就宣称样式生效。
- typecheck 通过就说“生成好了”。
- 没有后端就补后端;本 skill 仅前端。

## Side Effects

| Capability | spec-to-code |
| --- | --- |
| Reads repository | Yes |
| Writes docs/specs | Optional, for profile or return-to-spec records |
| Writes product code | Yes, frontend only |
| Runs tests | Yes, available project commands |
| Uses browser/screenshots | Yes, when UI/visual proof is required |
| Requires project profile | Non-XS unless explicitly no-code/unchecked |
