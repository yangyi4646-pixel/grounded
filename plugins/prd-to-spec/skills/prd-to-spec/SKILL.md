---
name: prd-to-spec
description: >-
  Use when 需要把一句话/薄需求、PM PRD、需求文档或纪要转成可执行 PRD/SPEC,把 PRD 更新同步进已有 SPEC,
  或用户要求「把需求补全成 PRD、把 PRD 转成 SPEC、蒸馏规格、这个需求怎么落、PM 稿更新同步 SPEC」.
  也用于 agent 正在把推断产品选择当结论、要求用户判断工程 jargon、未对账代码就给系统能力默认值,
  或验收不可验证却声称 SPEC 完成的场景。不用于直接写功能代码。
---

# 需求/PRD -> 可执行 SPEC

本 skill 只产出和对齐规格文档,不写功能代码。输入可以是一句话、薄需求、PRD、纪要或 PRD 更新。agent 可以展开候选结构,但冻结事实必须来自 PRD、用户确认、决策日志或代码证据。

## 铁律

```text
NO REUSE OR SYSTEM-CAPABILITY DEFAULT WITHOUT AN ESTABLISHED PRODUCT CODEBASE.
NO FROZEN SPEC FACT WITHOUT SOURCE, CODE EVIDENCE, OR USER CONFIRMATION.
NO SCOPE EXPANSION WITHOUT SCOPE BOUNDARY.
NO APPROVAL/LIFECYCLE DEFAULT WITHOUT AN OPERATION GATE.
NO MULTI-OBJECT DETAIL UI WITHOUT INFORMATION OWNERSHIP MATRIX.
NO FULL SPEC GENERATION PAST A P0 CONFIRMATION BLOCKER.
```

## 默认路径

0. **确立锚定产品**:先确认这个需求落在哪个现有产品/代码仓。已知(当前工作目录即该仓,或用户已指定路径)→ 声明后继续。需求明显要复用现有产品的页面/字段/能力,但代码仓未确立或在当前仓找不到 → 停,先请用户指定本地项目(给路径);确属无现有产品可锚的全新概念 → 用 `templates/no-code-evidence.md` 显式降级,不静默臆造现有能力。
1. **分档**:先判 XS/S/M/L;不确定升一档,但不得把小需求无理由拖进完整矩阵。
2. **读源**:读取 PRD/纪要/聊天决策/已有 SPEC。薄输入先落 `source/intent.md` 或等价意图记录。
3. **对账**:逐源标一致、互补、冲突、独有。PRD 明写的 IA、入口、对象归属优先冻结;源码便利性只能写实现候选。
4. **必要 recon**:只有当默认依赖现有系统能力时才扫描代码;无代码或早期概念(须先过第 0 步确认确无现有产品可锚)用 `templates/no-code-evidence.md` 明确降级。
5. **抽骨架**:XS 写影响判断;S 写 mini-spec;M/L 用 `references/spec-template.md` 起 §0、Scope Boundary、单元索引和各单元。
6. **触发式读 reference**:只读取下方路由表命中的文件,不要把所有规则一次性展开。凡路由命中 `templates/*` + `scripts/check_*.py` 的 gate,必须复制模板标题/表头并运行脚本;不得只用散文转述。
7. **确认门**:P0 停止完整 SPEC;P1 写确认截止点;P2 进 Later/backlog。确认后才回填实体契约。
8. **落盘与摘要**:长产物写到 `docs/specs/<需求>/` 或仓库约定路径;对话只给路径、决策摘要和未决项。

## 复杂度分档

| 档位 | 场景 | 产物 |
| --- | --- | --- |
| XS | 文案、样式、已有展示小调整;不改对象/权限/路由/存储 | 影响判断 + 1-3 条验收 |
| S | 单页轻交互;复用现有字段/组件;无新共享契约 | mini-spec |
| M | 新配置、表单、列表操作;改字段、入口、权限或状态 | 完整 SPEC 单元 |
| L | 新对象、跨模块、多角色、生命周期、多人并行 | 完整 SPEC + handoff |

升级条件:新增或改变对象模型、字段基数、枚举、状态机、权限、可见范围、存储键、URL 参数、行 id、消费读取、共享 renderer、语义资产,或现有系统语义不明。

## Reference Routing

| 触发 | 读取/使用 |
| --- | --- |
| 起手不确定需求落在哪个产品/代码仓,或要复用现有产品但仓库未确立 | 停 + 请用户指定本地项目路径(见默认路径第 0 步) |
| 新项目无 specs 约定 | `references/bootstrap.md` |
| 默认依赖现有系统能力 | `references/evidence-profile.md`;若没有代码证据用 `templates/no-code-evidence.md` |
| BI/数据产品薄输入 | `references/profiles/bi-product.md` |
| M/L 完整规格 | `references/spec-template.md`, `references/gap-checklist.md` |
| 需要确认或降阶拆问 | `references/clarify-loop.md`, `templates/confirmation-question.md` |
| P0 硬确认 | `templates/p0-confirmation-request.md`, `scripts/check_stop_on_p0_confirmation.py` |
| P1/P2 分级 | `scripts/check_confirmation_gap_levels.py` |
| 审批、发布、下线、删除、版本、消费读取 | `references/approval-lifecycle.md`, `templates/approval-lifecycle-gate.md`, `scripts/check_approval_lifecycle_gate.py` |
| 多对象、字段映射、详情卡片、头部/展开、配置页 | `references/information-ownership.md`(5 项 canonical 定义), `templates/information-ownership-matrix.md`, `scripts/check_information_ownership_matrix.py` |
| Scope Boundary 不清 | `templates/scope-boundary.md`, `scripts/check_scope_boundary.py` |
| 给用户/内部留痕分层(C2 用户段无 jargon) | `scripts/check_c2_user_section.py`(PASS=presence-only:无 `【给用户】` 段→not-applicable;用户段是否纯业务语义/可答交 judge/人) |
| 精确命中/可直接复用/exact match claim | `scripts/check_capability_verification.py`(PASS=presence-only:无此类 claim→not-applicable;符号是否真含目标能力交 judge/人) |
| 验收要变可检查断言 | `references/acceptance-as-eval.md` |

> 脚本 PASS = 结构/presence 合规,不证明业务正确;语义与业务判对交 judge/人。

## 确认分级

| 等级 | 含义 | 处理 |
| --- | --- | --- |
| P0 | 改变主对象、对象边界/基数、IA/入口、生命周期、权限、id/存储、删除/迁移、消费读取、字段语义 | 停止完整 SPEC,只交付确认请求、gap 清单、占位骨架 |
| P1 | 不阻塞整体骨架,但影响某单元实现选择、交互、默认值、恢复策略 | 可写草案和推荐默认,必须写确认截止点;到点未确认则升级受影响单元 P0 |
| P2 | 不影响当前规格冻结和实现路径 | 记录为 Later/backlog,不得写成已做 |

## 输出规则

- SPEC 必须包含:源对齐声明、决策日志、§0 冻结契约、Scope Boundary、单元索引、验收断言、未决 gap。
- gap 每条必须包含:位置、缺什么/歧义、推荐默认、理由、影响单元、优先级、确认截止点(若 P1)。
- `N/A` 必须写原因和来源;`未确认/待确认/gap/阻塞` 不得同时写 N/A。
- 机制脚本只检查结构与证据占位,不证明产品判断正确。
- 聊天确认必须当轮回写 SPEC 决策日志;spec-to-code 回流必须先提案、确认、再改 SPEC。

## 禁止的捷径

- 把薄输入退回给用户写完整 PRD。
- 把推断、常理、profile 缓存或源码便利性写成冻结事实。
- 只列 gap 不发确认问题。
- P0 已命中仍继续写完整 SPEC。
- 用卡片、折叠、容器或样式解决对象边界、信息归属、字段语义问题。
- 把局部反馈默认扩散到列表/详情/配置/消费侧。
- 声称 SPEC 完成但验收不可检查。

## Side Effects

| Capability | prd-to-spec |
| --- | --- |
| Reads repository | Optional, only when existing-system evidence is needed |
| Writes docs/specs | Yes |
| Writes product code | No |
| Runs tests | No by default; may run skill checker scripts |
| Uses browser/screenshots | No by default |
| Requires project profile | Optional; required only when defaults depend on existing-system evidence |

> 跨工具映射:`Task` -> Codex `spawn_agent`;`AskUserQuestion` -> 分组澄清/直接提问;`TodoWrite` -> `update_plan`;`Read/Write/Edit/Bash` -> 本地文件和 shell 工具。
