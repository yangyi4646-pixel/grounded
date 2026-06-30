# 需求规格总目录模板(docs/specs/INDEX.md)

> 复制本文件内容到 `docs/specs/INDEX.md`(勿自创格式)。本项目**一个需求一个文件夹**;整个 `docs/specs/` 经伞状 `.gitignore`(`*`)不进 git。
> 接手任一需求:先在下表定位 → 读其 `SPEC.md` 的 **§0 + Scope Boundary** + 对应 `handoff/`,再动手。按需读,别灌全文。

---------------- 复制以下作为 INDEX.md ----------------

# 需求规格总目录(docs/specs/)

> 本项目一个需求一个文件夹。整个 `docs/specs/` 经伞状 `.gitignore`(`*`)不进 git。
> 接手任一需求:先定位 → 读其 `SPEC.md §0 + Scope Boundary` + 对应 `handoff/`。

## 每个需求文件夹固定 4 类(源/规格两层)
| 角色 | 位置 | 谁维护 | 作用 |
| --- | --- | --- | --- |
| 工作规格(契约) | `SPEC.md` | AI | 唯一执行依据:§0 冻结契约 + Scope Boundary + 单元索引 + 各单元 范围/交互/验收 + 源对齐声明 + 决策日志 |
| 原始输入(源) | `source/` | PM / 你 | PRD 原稿、纪要、原型;只读可乱、会更新 |
| 单元交接 | `handoff/单元<n>-<名>.md` | AI | 每单元一份 |
| 临时笔记 | `notes/*.md`(含 `gaps.md`) | AI | gap 清单、调研 scratch |

> **gap 处理**:PM 的 PRD ≠ 执行用 SPEC。源更新就丢进 `source/`,跑 `/prd-to-spec`(gap 清单 + 批量确认,不臆断)把增量折进 `SPEC.md`。

## 需求清单
| 需求 | 文件夹 | 入口 | 状态 |
| --- | --- | --- | --- |
| 〈需求名〉 | `docs/specs/〈需求名〉/` | `SPEC.md` | 规划中 |

## 新增需求怎么做
1. `mkdir -p docs/specs/〈需求名〉/{source,handoff,notes}`(需求名 kebab、无空格、与本表/handoff 命名一致)。
2. **PRD/纪要原件先丢进 `〈需求名〉/source/`**。
3. 跑 `/prd-to-spec` 蒸馏出 `SPEC.md`(§0 契约 + Scope Boundary + 单元索引);每单元一份 `handoff/单元<n>-<名>.md`。
4. 本「需求清单」加一行。

---------------- 复制结束 ----------------
