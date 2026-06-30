# 信息归属矩阵(Information Ownership Matrix)

> 必填字段是机制门,不是装饰。每行必须有具体信息、展示职责、去重/排除规则和来源。`N/A` 只允许写成 `不适用: ...` / `N/A because ...`,并带来源或决策依据。

当前页面主对象(Current page main object):

| 信息域 / 层级(Domain / Layer) | 归属规则(Ownership Rule) | 信息(Information) | 展示职责(Display Responsibility) | 排除 / 去重规则(Exclusion / Dedupe Rule) | 来源(Source) |
| --- | --- | --- | --- | --- | --- |
| 当前主对象(Current main object) | 定义当前页面主对象或主关系的信息 |  |  |  |  |
| 上游对象(Upstream object) | 在当前对象之前或之外独立存在的信息 |  |  |  |  |
| 下游消费对象(Downstream consumer object) | 只有被其它 surface 消费时才成立的信息 |  |  |  |  |
| 关系态信息(Relation-only information) | 只有两个对象发生关系时才成立的信息 |  |  |  |  |
| 完整详情页信息(Full-detail-only information) | 属于完整详情页、不属于当前视角的信息 |  |  |  |  |

头部摘要职责(Header summary responsibility):

展开区职责(Expanded-detail responsibility):

不重复展示规则(Do-not-repeat rule):
- 一个信息只能出现在最合适的一层。
- 头部摘要已经展示的字段、映射或同义信息,展开区不得用同名或换一种说法重复。
- 展开区只回答:头部没有给出的新增信息是什么。
- 完整详情页信息应通过详情页链接承载,不得在当前视角重复。
