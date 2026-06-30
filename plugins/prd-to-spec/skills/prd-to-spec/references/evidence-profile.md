# Evidence Profile Protocol

Evidence Profile is a repository-local evidence inventory used during PRD-to-SPEC reconciliation. It is not product truth, not a domain playbook, and not a replacement for user confirmation.

## Authority Order

| Rank | Source | How To Use |
| --- | --- | --- |
| 1 | PRD / user confirmation / decision log | Freeze product facts and SPEC contracts. |
| 2 | Source reconciliation | Prove current system shape, constraints, and implementation candidates. |
| 3 | Evidence Profile | Speed up recon by pointing to current evidence, risks, and known gaps. |
| 4 | Optional domain adapter | Suggest candidate questions and risk dimensions only. |
| 5 | Model inference | Only as labeled hypothesis or recommended default. |

If Evidence Profile conflicts with PRD path, IA, ownership, or user-confirmed facts, the profile loses. Record the conflict as a gap instead of silently choosing.

## Generic vs Project-Specific Boundary

These eight optimizations are generic protocol, not project content. The skill owns the rule shape; the generated project profile owns concrete facts.

| Optimization | Generic Skill Owns | Project Profile Owns |
| --- | --- | --- |
| 1. Authority order | Source ranking and conflict rule. | Actual PRD links, decisions, source paths, and conflicts. |
| 2. Create/refresh trigger | Risk conditions that require a profile or micro-profile. | Whether the current repo/task matches those triggers. |
| 3. Required header | Required header fields and stale-check concept. | Timestamp, repo, branch/commit, scan scope, stale triggers. |
| 4. Fixed sections | Section names and minimum evidence categories. | Filled rows for this repo's objects, surfaces, consumers, and hazards. |
| 5. Confidence enum | Definitions of `exact`, `similar`, `exists-only`, `unknown`. | Per-row confidence labels based on actual evidence. |
| 6. Evidence citation | Rule that factual claims cite source path, command, or decision source. | The concrete files, commands, line refs, screenshots, or notes. |
| 7. Negative findings | Requirement to record searched-but-missing evidence. | What was searched, how, result, and SPEC impact. |
| 8. Gate/self-eval | Criteria for profile completeness and honest pass/partial/fail. | Actual gate result and unchecked reasons for this task. |

Do not move project-specific components, routes, ports, tokens, object names, status values, or business defaults into this protocol. If a domain adapter is useful, it may propose question dimensions only; facts still come from PRD, user confirmation, source recon, or the generated project profile.

## When To Create Or Refresh

- A gap default depends on existing-system behavior, capability, permissions, routing, reuse, data lifecycle, or visual grammar.
- The PRD references existing objects or surfaces but simplifies their real shape.
- The work may affect config/consumption surfaces, list/detail pairs, shared renderers, semantic assets, permission boundaries, or downstream readers.
- Existing profile is stale: branch changed, cited paths changed, design system migrated, routes moved, or a prior task found a profile miss.

XS changes may use a focused micro-profile covering only the affected evidence. M/L work needs a project-local profile path or an explicit reason why no existing-system evidence is involved.

## No-Code / Unavailable Evidence

如果任务处于早期概念、无代码仓库、无访问权限,或本轮默认不依赖现有系统能力,不要伪造 Evidence Profile。复制 `templates/no-code-evidence.md`,明确:

- 证据为何不可用或不需要。
- 哪些假设不能被代码验证。
- 哪些默认只允许作为 provisional default。
- 哪些事项必须在 SPEC freeze / handoff / spec-to-code 前确认。

该模板是降级说明,不是产品判断来源。后续拿到仓库或运行证据时,必须刷新 Evidence Profile 或 micro-profile。

## Confidence Enum

| Confidence | Meaning | Allowed Use |
| --- | --- | --- |
| `exact` | Direct source proves this object/surface/behavior. | May support a recommended default, still not override PRD. |
| `similar` | A sibling pattern is close but not the same target. | Candidate default only; mark transfer risk. |
| `exists-only` | Symbol/path/component exists, semantics not proven. | Recon lead only; cannot be written as "已对账". |
| `unknown` | Evidence missing or contradictory. | Gap or blocking question. |

Every factual row must include confidence plus source path, command, or decision source. Claims without evidence are `unknown`.

## Required Sections

Use `profiles/template.md` unless the project has a stricter local format.
The generated profile must start with the required header from the template; missing generated time, repository, commit/worktree, scan scope, stale triggers, or status means the profile is incomplete.

1. Profile header: generated time, repo, branch/commit, scan scope, stale triggers.
2. Product surfaces and object vocabulary found in source.
3. Existing-system contracts relevant to this PRD: ownership, permissions, lifecycle, identifiers, routes, storage, propagation.
4. Consumption map: who reads or depends on the object, including list/detail/config/consumer surfaces.
5. Scope hazards: shared renderers, global constants, permission gates, migration paths, or semantic assets that could cause silent spread.
6. Negative findings: paths searched but not found, unsupported assumptions, unavailable commands, or evidence that stayed `unknown`.
7. Open profile gaps: what still needs recon or user confirmation before freezing SPEC facts.

## Output Rules

- Write generated profiles to the target repository, for example `docs/tmp/prd-to-spec-evidence-profile.md` or the repository's own agent/profile folder.
- Do not copy generated project profiles into the shareable skill package.
- Do not use profile prose as a citation. Cite the source paths or commands recorded inside the profile.
- Domain adapters may add candidate question dimensions, but must not add project-specific components, ports, routes, tokens, or object facts.
