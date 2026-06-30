# Reuse-First Scan

Purpose: prevent self-built UI from drifting away from the host product. Scan first, then build.

## Scan Order

1. **Project Profile**
   Load or generate the profile. It should identify route patterns, component roots, design tokens, form grammar, field display grammar, semantic assets, tests, and dev commands.

2. **Canonical Sibling**
   Find the closest existing screen by information shape and workflow, not by name alone. A list page compares to list pages, a detail page to detail pages, a config form to config forms. If no sibling fits, record why.

3. **Host Grammar**
   Extract the grammar that makes this product feel native:
   - page shell and navigation pattern
   - form labels, required marks, validation, row spacing, control width, footer ownership
   - field chips, tags, status badges, icons, empty states, loading states
   - table row density, edit/read state height, expansion layout, action menus

4. **Reusable Components and Data Access**
   Search common component roots, domain components, model/action layers, service/request wrappers, and project data tools. Do not treat a symbol match as capability proof.

5. **Design System / Token Layer**
   Use the host product's token and asset system. Do not hardcode colors, spacing, icons, or typography when the profile or sibling shows a canonical source.

## Evidence Grades

| Grade | Use | Do Not |
| --- | --- | --- |
| Exact match | Same object/workflow/state exists; cite path and capability checked | Claim exact match from a name only |
| Similar pattern | Different object or lifecycle, but useful structure | Copy behavior without rechecking SPEC |
| Library exists | Technical building block exists | Call it a business-ready pattern |
| No match | Build a thin wrapper or local implementation with reason | Invent a nonexistent pattern |

Exact match requires capability verification: read the implementation or usage that proves the behavior exists.

## Reuse List Format

Before implementation, produce:

| Need | Reuse target | Evidence grade | Capability checked | Source path | Adaptation |
| --- | --- | --- | --- | --- | --- |

No reuse target is acceptable only with a stated reason.

## Thin Wrapper Rule

Build new UI only when existing grammar has a semantic mismatch: lifecycle, cardinality, permissions, state model, or interaction contract. A thin wrapper should still call host components/tokens/assets internally.

### 新机制约定核验(引入克隆源没有的机制时)

锚定 canonical sibling 时,它未必演示你这次需要的每一种机制。一旦你要引入一个**克隆源/锚定 sibling 里没有的机制**(组件样式表、数据请求封装、i18n、路由注册、状态管理、文件上传…),**不要用通用/教科书写法**——先在本仓找一个**真正用了该机制的组件**,照它的约定写。

判据:凡“sibling 没演示、我新引入”的机制,都要单独 recon 它在本仓的用法,别假设通用写法成立。常见高危处:
- **组件样式注入**:本仓可能要求手动注入(如 `useStyles(s)` / `insertCss`);`import s from './x.scss'` 不一定自动注入 CSS——光挂 `s.className` 类名在、样式不生效。
- **弹窗内容收高**:长内容弹窗按本仓惯例收高(组件自身 `max-height/overflow` 或 Modal body 限高),别让弹窗无界生长。
- 路由注册、i18n key、请求封装、权限 wrapper 同理。

内部留痕证据行:`新引入机制:X | 本仓用 X 的组件:Y(file:line)| 其约定:… | 我照此写:是/否`。

> 反例(实测):日历预览克隆自一个纯 utility 类、无组件 scss 的 admin 页,于是新引入的 `.scss` 用通用 CSS-modules 写法、漏了本仓 isomorphic-style-loader 必需的 `useStyles(s)` → 类名挂上、CSS 永不注入 → 日历塌成竖排、弹窗溢出。一次真渲染或一次「新机制 recon」都能挡下。
