# 审批 / 生命周期确认门(Approval / Lifecycle Gate)

> 当需求触发审批、发布/上线、下线、删除、撤回、重新提交、回调、外部处理、生命周期状态、配置开关、版本生效或下游消费读取时必填。
> 每行必须确认、标 gap,或显式写 `不适用 + 原因 + 来源`。`Blocked Units` 表示该行确认前不能推进的 SPEC 小节、UI 路径、状态机或实现路径。
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
