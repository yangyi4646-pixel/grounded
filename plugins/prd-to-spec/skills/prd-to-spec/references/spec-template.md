# SPEC.md 骨架模板

> 复制下面"模板正文"作为 `SPEC.md` 起点,逐节填。**ALWAYS 用本结构**——§0 契约的稳定性靠固定模板保证。
> 已确认才写实;未决进「⚠️ 待确认」并标阻塞对象。小占位用尖括号 `〈…〉`(避免与代码围栏冲突)。
>
> **结构化槽位**:各表必填列双消费者(轻档 skill + 重档引擎)共用;可空列引擎专用(如 archetype / blueprint field / 视觉量→token / sourceRef / predicate)。
> 轻档留空即登记为 gap(收口到「gaps / 不做项」表),升级引擎时再填、不重写 SPEC。可空列示例值给占位或留空,轻档不必填。
> 每张表自带「备注/出处」列承载 prose,不另起平行散文段(同一事实只写一处,防双写漂移)。

---------------- 模板正文(从下一行开始复制)----------------

# 〈需求名〉 SPEC

## 源对齐声明
- 蒸馏自:`source/〈文件〉@〈版本/日期〉`(列全部源:PRD / 纪要 / 原型)
- 多源对账:一致 N 条;冲突已解 M 条(见决策日志);仅纪要含的决策 K 条(已折入)
- 本轮(〈日期〉)确认 gap:#1 #3 #7;暂缓:#5(待确认)
- 状态:配置侧 ①②③ 完成 / ④ 待对齐 / 消费侧 ⑤ 进行中

## §0 冻结契约(改动需全单元同步,最高优先级)
跨所有单元共享;任一改动要通知所有受影响单元并更新 handoff。

### 对象模型
| 实体 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| 〈实体〉 | 〈字段〉 | 〈类型〉 | 是/否 | 关系基数:实体A —< 实体B(一对多 / 多对多?) |

### 枚举与状态
- `〈Enum〉`: A | B | C(完整集合,含未设置)
- 状态流转:草稿 → 发布(是否有草稿?不可逆?)

### id / 存储键
- 行 id:〈生成规则,是否稳定〉
- 存储键:`〈key〉` = 〈结构〉;拥有者:单元〈n〉

### 契约值(逐字字面量,verify-loop 直接 diff;禁推断)
> 此表是契约值的**唯一拷贝源**;单元节只引用「键」名,不重述值。
> **规约**:枚举/视觉量必须绑代码库**真实 token 名**(实测值,如 `--color-text-link`),禁占位假名;未冻结的格子填「⚠️ 待确认 → 见 notes/gaps.md#Gn」,**不编造 token**。
| 键 | 字面量值 | 闭集? | 拥有单元 | 备注/出处 |
| --- | --- | --- | --- | --- |
| id.separator | `〈如 "::"〉` | — | §0 | 〈出处〉 |
| enum.〈Enum〉 | `A` \| `B` \| `C` | 是/否 | §0 | 〈含未设置?〉 |
| storage.key | `〈key〉` = `〈结构 JSON 形〉` | — | 单元〈n〉 | 〈出处〉 |

### 表单视觉契约(决定表单长相的字段模型;一等契约,非区域装配的备注)
> 真正决定表单长相的是 `Form + Form.Item`,**不是** `FormSection`(后者只是带 padding 的两列 grid 盒子)。
> 必填/可空:轻档留空即登记为 gap(收口到「gaps / 不做项」表);可空留空 = gap。冻结值须为代码库实测值。
| 键 | 必填? | 冻结值(本仓库实测) | 出处(镜像页) | 备注 |
| --- | --- | --- | --- | --- |
| form.lib | 必填 | 〈本仓库 Form 库,示例 `@your-org/ui`〉 | 〈如 AtomicMetricForm〉 | 〈出处〉 |
| form.layout | 必填 | `vertical`(label 上、控件下) | 〈镜像页〉 | |
| form.fieldComponent | 必填 | `Form.Item`(label + name + rules);禁手写 `<div>label</div> + 裸控件` | 〈镜像页〉 | |
| form.requiredMark | 必填 | rules 驱动(`rules:[{required}]`),星在**文字后** `名称 *`;禁手写 span | 〈镜像页〉 | |
| form.validation | 必填 | 内联(Form.Item 红字);**禁** Notification 吐司 | 〈镜像页〉 | |
| section.grid | 可空 | FormSection = 2 列 grid(`gap:12px 16px`),跨行用 `.spanFull`(`grid-column: span 2`) | 〈镜像页〉 | 留空=gap |
| page.width | 可空 | 主体内层 `840`/`880` 居中等宽,`margin:0 auto`,非贴边 16px;GoBack 自带 padding 不再外包 | 〈镜像页〉 | 留空=gap |
| control.width | 可空 | 默认撑满 grid 单元格;定宽控件须显式列(如聚合 `width:150`),否则撑满 | 〈镜像页〉 | 留空=gap |
| footer.ownership | 必填 | 复用共用 `EditFooter` 或各单元自有 Footer;**禁跨单元 import 兄弟页私有 Footer** | 〈镜像页〉 | |

### 页面契约(每页一行;archetype 是引擎判别键)
> archetype / 权限 PK 可空:留空 = 轻档自行选骨架;填了 = 引擎据此选渲染分支。
| 页面/单元 | archetype | 路由 path | new/edit 共用? | 权限 PK | 入口跳转 | 备注/出处 |
| --- | --- | --- | --- | --- | --- | --- |
| 〈单元n〉 | 〈enterprise-table-page \| search-results-page \| explorer-page \| 表单页;可空〉 | `/…` | 是/否 | `〈PK,可空〉` | 〈从X右键→〉 | 〈出处〉 |

### 共享类型 / 模块位置
- `types/…`、`model/…`:谁定义、谁复用

## 单元索引
| # | 单元 | 范围 | 拥有会话 | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 1 | 列表 | … | 会话A | §0 | 完成 |
| 2 | 新建/编辑 | … | 会话B | §0,#1 | 进行中 |
| out | 明确不做 | 见下「gaps / 不做项」表(逐项带 id) | — | — | — |

## Scope Boundary(实现边界真源;spec-to-code 必读)
> 本节回答「本轮到底改哪里、哪里明确不改、哪些连带同步」。局部截图 / 当前 URL / 当前页面反馈默认只作用于 current surface;跨入口扩散必须写在 Propagation Rule 或决策日志里。
> 模板: `templates/scope-boundary.md`。机械检查: `scripts/check_scope_boundary.py <SPEC.md>`。
| Surface / 单元 | Affected Surfaces(本轮直接改) | Non-Goals / 不改面 | Propagation Rule(连带同步规则) | Owner | 出处 |
| --- | --- | --- | --- | --- | --- |
| 单元〈n〉 | 〈页面/入口/状态/消费面〉 | 〈相邻列表/详情/配置/导出/消费侧哪些不改〉 | 〈如共用枚举/语义资产需同步;默认不扩散〉 | 会话〈x〉 | PRD / 用户确认 / 决策日志 |

## 审批 / 生命周期确认门(Approval / Lifecycle Gate;审批 / 生命周期 / 消费读取时必填)
> 当需求涉及审批、发布/上线、下线、删除、撤回、重新提交、回调、第三方/外部处理、生命周期状态、配置开关、版本生效或下游消费读取时,本节是实现前置条件。
> 模板: `templates/approval-lifecycle-gate.md`。机械检查: `scripts/check_approval_lifecycle_gate.py <SPEC.md>`。
> 每行必须写确认范围、来源和阻塞单元(Blocked Units)。`N/A` 只能写成 `不适用: ...` / `N/A because ...`,并带出处或决策依据;空表不能作为过门证据。
> `不适用 / N/A` 只用于“本需求明确不触发该风险”。如果原因是“输入未提 / PRD 未写 / 待确认 / 需后续确认”,必须写成 gap,不得写 N/A。

| 操作 / 风险(Operation / Risk) | 默认必须进 gap(Default is Gap) | 已确认范围(Confirmed Scope) | 来源(Source) | 阻塞单元(Blocked Units) |
| --- | --- | --- | --- | --- |
| 删除/下线/归档等破坏性操作(Destructive operations) | 是:不得静默把破坏性操作排除在审批/生命周期控制外 | 〈确认 / gap Gx / 不适用:本需求明确不触发该风险+原因〉 | 〈出处〉 | 〈阻塞 SPEC 单元 / UI 路径 / 状态机 / 实现路径〉 |
| 批量操作(Batch/bulk operations) | 是:单项路径受控时,不得静默放过批量路径 | 〈确认 / gap Gx / 不适用:本需求明确不触发该风险+原因〉 | 〈出处〉 | 〈阻塞 SPEC 单元 / UI 路径 / 状态机 / 实现路径〉 |
| 审批中可编辑性 / 重复提交(Pending editability / repeat submit) | 是:pending 锁定、审批中可编辑、重复提交都属于产品契约 | 〈确认 / gap Gx / 不适用:本需求明确不触发该风险+原因〉 | 〈出处〉 | 〈阻塞 SPEC 单元 / UI 路径 / 状态机 / 实现路径〉 |
| 撤回 / 重新提交(Withdraw / resubmit) | 是:取消/拒绝后的恢复路径必须明确 | 〈确认 / gap Gx / 不适用:本需求明确不触发该风险+原因〉 | 〈出处〉 | 〈阻塞 SPEC 单元 / UI 路径 / 状态机 / 实现路径〉 |
| 回调 / 外部处理(Callback / external handling) | 是:内部处理 vs 外部处理、只读 vs 可操作必须明确 | 〈确认 / gap Gx / 不适用:本需求明确不触发该风险+原因〉 | 〈出处〉 | 〈阻塞 SPEC 单元 / UI 路径 / 状态机 / 实现路径〉 |
| 配置面(Config surface) | 是:开关、模式、审批人、端点是独立 surface | 〈确认 / gap Gx / 不适用:本需求明确不触发该风险+原因〉 | 〈出处〉 | 〈阻塞 SPEC 单元 / UI 路径 / 状态机 / 实现路径〉 |
| 版本 / 消费读取(Version / consumption read) | 是:pending/rejected 版本不得静默影响下游读取 | 〈确认 / gap Gx / 不适用:本需求明确不触发该风险+原因〉 | 〈出处〉 | 〈阻塞 SPEC 单元 / UI 路径 / 状态机 / 实现路径〉 |

## 信息归属矩阵(Information Ownership Matrix;多对象 / 详情 / 展开收起时必填)
> 当页面涉及多个对象、字段映射、上游/下游消费、头部摘要、展开/收起、卡片/表格/详情结构时,本节是 spec-to-code 的实现前置条件。
> 模板: `templates/information-ownership-matrix.md`。机械检查: `scripts/check_information_ownership_matrix.py <SPEC.md>`。
> 每行必须有具体信息、展示职责、去重/排除规则和出处。`N/A` 只能写成 `不适用: ...` / `N/A because ...`,并带出处或决策依据;空表不能作为过门证据。

当前页面主对象(Current page main object):

| 信息域 / 层级(Domain / Layer) | 归属规则(Ownership Rule) | 信息(Information) | 展示职责(Display Responsibility) | 排除 / 去重规则(Exclusion / Dedupe Rule) | 来源(Source) |
| --- | --- | --- | --- | --- | --- |
| 当前主对象(Current main object) | 〈当前页面主对象或主关系的定义〉 | 〈本页核心信息〉 | 〈头部/主体/展开区怎么承载〉 | 〈哪些信息不得重复〉 | 〈出处〉 |
| 上游对象(Upstream object) | 〈上游对象独立存在的信息〉 | 〈如来源对象字段〉 | 〈只做上下文还是可编辑〉 | 〈不复刻完整详情〉 | 〈出处〉 |
| 下游消费对象(Downstream consumer object) | 〈下游消费才成立的信息〉 | 〈消费面/读取影响〉 | 〈本页是否展示〉 | 〈不展示则写跳转/不做〉 | 〈出处〉 |
| 关系态信息(Relation-only information) | 〈两个对象发生关系后才成立的信息〉 | 〈字段A -> 字段B / 绑定状态〉 | 〈通常是当前页重点〉 | 〈不得和上游/下游重复〉 | 〈出处〉 |
| 完整详情页信息(Full-detail-only information) | 〈完整详情页才应承载的信息〉 | 〈完整定义/取值/审计/历史〉 | 〈本页跳转或不展示〉 | 〈禁止在当前视角重复〉 | 〈出处〉 |

头部摘要职责(Header summary responsibility):

展开区职责(Expanded-detail responsibility):

不重复展示规则(Do-not-repeat rule):
- 一个信息只能出现在最合适的一层。
- 头部摘要已展示的字段、映射或同义信息,展开区不得用同名或换一种说法重复。
- 展开区只回答:头部没有给出的新增信息是什么。
- 完整详情页信息应通过详情页链接承载,不得在当前视角重复。

### gaps / 不做项(单一真源;引擎读 id→gaps[].id)
> 单元索引 `out` 行与各单元 out-of-scope 统一收口到此表,**不在散文里重复**。
| id | 范围 | reason(prose) | 类型 |
| --- | --- | --- | --- |
| gap-〈x〉 | 〈本期不含 X〉 | 〈出处+原因〉 | out-of-scope \| runtime-gap |

## 单元 〈n〉:〈名〉
- **范围**:in-scope 一句话;out-of-scope 明列(并在「gaps / 不做项」表登记 id)。
- **实现边界**:引用上方 Scope Boundary 行;禁止在单元内另起一套范围口径。
- **实现路径**:落在 `〈目录/组件/model〉`。
- **复用件清单**(reuse-first 第 1/2 扫描顺序;引擎读 component owner):

  | 复用件 | 来源路径 | props/配置 | 薄封装依据 | 备注/sourceRef |
  | --- | --- | --- | --- | --- |
  | `〈现成模块〉` | `src/…` | 〈关键 props〉 | 〈为何只薄封装〉 | 〈可空〉 |

- **区域装配**(顺序硬跟字段流;轻档=FormSection 顺序,引擎=region→blueprint field):

  | 顺序 | region/分区 | 组件 owner | blueprint field | 必需 slots | 视觉量→token(可空) | 备注/出处 |
  | --- | --- | --- | --- | --- | --- | --- |
  | 1 | 〈如 筛选区〉 | 〈SourcePageToolbar〉 | `〈如 filters;可空〉` | 〈text/select〉 | width=`〈--var,可空〉` | 〈出处〉 |

- **交互矩阵**(kind/默认/确认取消逐条消歧;kind/options 必填,谓词语义/submitIdsMode 可空):

  | 控件 | kind | 选项/options | 单/多选 | 默认值 | 谓词/effect 语义(可空) | submitIdsMode(可空) | 备注/出处 |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | 〈主题筛选〉 | select | 全部\|A\|B | 单 | 全部 | 〈如 row.theme===v;空=轻档散文消化/引擎登 gap〉 | — | 〈出处〉 |

- **验收(可勾验断言,非散文 — 见 `references/acceptance-as-eval.md`)**:

  | # | Given-When-Then | 检查方式 | 期望 | 通过 |
  | --- | --- | --- | --- | --- |
  | A1 | Given 〈前置〉 When 〈操作〉 Then 〈可观察结果〉 | 实拍 / UT / 命令 | 〈期望 observable/值〉 | ☐ |
  | A2 | Given 〈边界:空/超限/无权限〉 When … Then … | 实拍 / UT | … | ☐ |

  - 检查方式:UI→**实拍**(observable「出现/不出现」);纯逻辑/Model→**UT**;可复现→**命令**贴输出。
  - 完成判据:**全部断言可检且通过** + lint/UT 过 + 文案/埋点到位。
  - gap 回流锚点:某断言失败 → 记「A# 失败 + 现象」,回流为 SPEC 增量断言(带出处),**不写散文**。

## ⚠️ 待确认(阻塞中)
| # | 问题 | 推荐默认 | 阻塞单元 | 状态 |
| --- | --- | --- | --- | --- |
| 5 | 〈歧义点〉 | 〈默认+理由〉 | 单元3 | 已问/待问 |

## 决策日志(即回流 changelog 落点)
> spec-to-code 回流改 SPEC/PRD 时,经用户确认后在此记一条,**不静默改、不另起平行散文**。
| 日期 | actor(谁) | 决策 | 出处 | 影响 |
| --- | --- | --- | --- | --- |
| 〈date〉 | 〈PM / 用户 / spec-to-code 回流〉 | 〈关键决策,如 实体A↔B = 多关联〉 | 纪要 / 用户确认 | §0 对象模型 |
| 〈date〉 | 〈actor〉 | 〈交互决策,如 共享控件置顶〉 | 用户确认 | 单元〈n〉 |

---------------- 模板正文结束 ----------------
