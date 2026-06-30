# Implementation Evidence Profile Bootstrap

An Implementation Evidence Profile is a repository-local inventory generated before SPEC-to-code work. It records evidence for how this repository actually implements routes, visual grammar, reuse, data access, verification, and known hazards.

It is not part of the shareable skill, not a product decision record, and not a model-written project summary. It cannot override SPEC, PRD, Scope Boundary, handoff notes, or user-confirmed decisions.

## When to Generate

- No existing profile is available.
- The existing profile is stale: major dependency update, design system migration, route restructure, component library change, or a previous task exposed a grammar mismatch.
- The work is a new screen, composed view, form, table, details page, or any UI where host-system fit matters.

XS edits may use a focused micro-profile for the affected grammar only. Non-XS work must produce a project-local profile path before implementation.

## Authority Order

| Rank | Source | How To Use |
| --- | --- | --- |
| 1 | SPEC §0, Scope Boundary, user-confirmed handoff | Freeze values, routes, object model, states, and edit scope. |
| 2 | Decision log / explicit user confirmation | Resolve conflicts and scope expansions. |
| 3 | Current source evidence | Prove available patterns and constraints. |
| 4 | Implementation Evidence Profile | Cache pointers to evidence and known gaps. |
| 5 | Sibling pattern / component name / model inference | Candidate only; must be capability-checked. |

If profile evidence conflicts with SPEC or Scope Boundary, stop and return the conflict to `prd-to-spec`.

## Generic vs Project-Specific Boundary

These eight optimizations are generic protocol, not project content. The skill owns the rule shape; the generated project profile owns concrete facts.

| Optimization | Generic Skill Owns | Project Profile Owns |
| --- | --- | --- |
| 1. Authority order | Source ranking and conflict rule. | Actual SPEC section, handoff note, decision record, and source conflict. |
| 2. Create/refresh trigger | Risk conditions that require a profile or micro-profile. | Whether this task is XS or non-XS, and what repo areas must be scanned. |
| 3. Required header | Required header fields and stale-check concept. | Timestamp, repo, branch/commit, scan scope, stale triggers. |
| 4. Fixed sections | Section names and minimum implementation evidence categories. | Filled rows for this repo's routes, siblings, visual grammar, data access, and hazards. |
| 5. Confidence enum | Definitions of `exact`, `similar`, `exists-only`, `unknown`. | Per-row confidence labels based on actual source proof. |
| 6. Evidence citation | Rule that factual claims cite source path, command, screenshot, or test method. | Concrete files, commands, line refs, screenshots, and test outputs. |
| 7. Negative findings | Requirement to record searched-but-missing evidence and unavailable checks. | Searches run, missing assets, unsupported assumptions, and implementation impact. |
| 8. Gate/self-eval | Criteria for profile completeness and honest pass/partial/fail. | Actual gate result, unchecked reasons, and the highest reached completion tier. |

Do not move project-specific components, routes, ports, tokens, icons, object names, status values, commands, or business defaults into this bootstrap. If a project needs a reusable profile, generate it inside that repository and refresh it when its evidence goes stale.

## Confidence Enum

| Confidence | Meaning | Allowed Use |
| --- | --- | --- |
| `exact` | Direct source proves this target behavior or exact sibling grammar. | May support implementation choice if SPEC permits it. |
| `similar` | A sibling pattern is close but not the same target. | Candidate reuse with transfer risk. |
| `exists-only` | Symbol/path/component exists, semantics or rendered behavior not proven. | Recon lead only; not capability proof. |
| `unknown` | Missing, contradictory, or inaccessible evidence. | Must become unchecked item, gap, or explicit mock boundary. |

Every factual row must include one of these confidence values plus a source path, command, screenshot, or test method. Claims without evidence are `unknown`.

## Existing Profile Freshness Gate

Before reusing an existing profile, check:

| Check | Fresh Enough | Stale / Partial |
| --- | --- | --- |
| Timestamp and commit | Profile commit matches current worktree or the scanned files are unchanged | Branch moved, design-system files changed, or profile has no commit/scope |
| Scope match | Profile covers the affected surface type and grammar | New screen/form/table/detail/status/asset grammar not covered |
| Evidence paths | Cited source paths still exist and match the described convention | Paths missing, renamed, or behavior changed |
| Known mismatch | No later task exposed a profile miss in the affected grammar | Prior task found style/route/asset mismatch not folded back |

If stale, regenerate the affected section or create a new project-local profile. Do not treat an old profile as stronger than the current SPEC or source evidence.

## Scan Checklist

| Area | Evidence to Capture |
| --- | --- |
| Runtime | package manager, framework, dev server command, type/lint/test commands |
| Routing | route files, entry/navigation patterns, permission guards, route ordering hazards |
| Page grammar | canonical sibling screens by surface type; page shell, header, body, footer |
| Form grammar | label placement, required mark, validation message, row spacing, control width, submit area |
| Field grammar | chips, tags, icons, badges, status colors, empty/loading/error states |
| Semantic assets | icon system, asset naming, sizing, weight/color roles, fallback rules |
| Tokens/styles | design tokens, CSS module conventions, utility classes, hardcode policy |
| Data access | existing service/request wrappers, fixture/mocking pattern, project data inspection tools |
| Tests | unit/integration locations, test runner quirks, what logic is usually tested |
| Known hazards | commands that no-op, flaky tests, unsupported Node/browser versions, auth or preview constraints |

## Output Location

Write the generated profile to a project-local path, for example:

```text
docs/tmp/spec-to-code-profile.md
```

If the project has its own agent/profile folder, use that. Do not put generated profiles into the shareable skill package unless explicitly creating a template.

## Required Profile Header

Copy this header shape before filling the body. A generated profile without every header bullet below is incomplete.
T1/Profile Bootstrap cannot be `pass` if generated time, repository, commit/worktree, scan scope, stale triggers, or status is missing.

```markdown
# spec-to-code Implementation Evidence Profile

- Generated at: <ISO datetime>
- Repository: <path or repo name>
- Commit/worktree: <branch + commit if available>
- Scan scope: <files/areas scanned>
- Stale when: <conditions>
- Status: evidence inventory, not product truth
```

## Required Sections

Do not skip the header and do not replace the fixed sections with a prose summary.

1. Runtime and verification commands.
2. Route and entry conventions.
3. Canonical sibling map by surface type.
4. Visual and interaction grammar: page, form, field, status, assets, spacing/density, state variants.
5. Reuse roots and capability checks.
6. Data/mock boundary.
7. Scope hazards: shared renderers, global styles, shared semantic assets, downstream consumers.
8. Negative findings: searched-but-missing evidence, unsupported assumptions, unavailable checks.
9. Open profile gaps.

Every factual line must cite at least one source path or command and a confidence enum.

## Hard Boundary

If profile evidence conflicts with SPEC/PRD, do not choose the profile silently. Record the conflict and return to `prd-to-spec`.
