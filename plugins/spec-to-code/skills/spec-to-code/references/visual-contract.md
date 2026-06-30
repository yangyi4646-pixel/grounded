# Visual Contract Protocol

The visual contract turns "make it fit this product" into executable evidence. It applies to new screens, composed components, detail/list/forms, or any style-affecting change.

## Source Priority

1. Explicit SPEC visual/interaction contract.
2. User-confirmed decision log.
3. Canonical sibling evidence from the project profile.
4. Existing token/component grammar from source.
5. Gap back to `prd-to-spec`.

Existing code is evidence, not product truth. It cannot override SPEC/PRD without confirmation.

## Contract Table

Before implementation, fill a compact table:

| Surface | Canonical sibling | Layout shell | Form/field grammar | Semantic assets | States | Proof |
| --- | --- | --- | --- | --- | --- | --- |

Use one row per affected surface. For XS style fixes, one row is enough.
Template: `templates/visual-contract-table.md`.

For style-affecting work, also fill `templates/runtime-visual-proof.md`. The visual contract says what should be true; runtime visual proof shows that the rendered node actually obeys it.

## What Counts as Contract

- Layout shell: page container, header/body/footer, sidebar/tree/list/detail arrangement, scroll owner.
- Typography: role, size, weight, line height, truncation behavior.
- Spacing/density: section padding, row height, control gap, table density, card/list rhythm.
- Form grammar: label, required mark, validation message, control width, disabled/readonly state.
- Field grammar: chip/tag/badge shape, icon role, status color, empty value.
- Semantic assets: icons, illustrations, badges, status marks, warning/error indicators.
- State layout invariants: read/edit, loading, empty, error, hover/open menu, async prefill, boundary data.

## Proof Rules

- Class added is not proof. The actual rendered node must show the intended style or semantic asset.
- Token name is not proof. Read back the token value, computed style, DOM box, screenshot, or canonical sibling value where practical.
- If a wrapper component owns text rendering, verify the wrapper's child node or computed style.
- If an interactive control replaces text, verify layout invariants before and after the transition.
- If an icon/status/badge carries meaning, verify name/role/size/color/weight against the contract.
- If design-side judgment is required, report `visual alignment complete` at most until design accepts.

## Semantic Asset Proof Ladder

Use this ladder for icons, badges, status marks, illustrations, warning/error symbols, and field chips:

| Level | Evidence | Verdict |
| --- | --- | --- |
| Intent only | Runner says "use warning icon" or chooses a visually similar name | Fails proof |
| Registry/package evidence | Asset exists in icon set, token registry, or sibling source | Partial; proves availability, not actual render |
| Sibling semantic match | Same asset is used for the same product meaning in a canonical sibling | Pass for choice, still needs render proof |
| Rendered proof | Screenshot/DOM/computed style shows actual name/role/size/color/weight on the affected node | Pass |
| Missing asset | Desired asset not in host system | Return gap or use confirmed fallback; do not silently substitute |

## Common Failures

| Failure | Required Counter |
| --- | --- |
| Parent class changed but child renderer overrides it | Inspect actual rendered node/computed style |
| Token exists but runtime value differs from expected taste | Read token value and compare rendered computed style/screenshot |
| Read state aligned, edit state grows or shifts | Check bounding boxes before/after interaction |
| Field chips use mixed icon/tag grammar | Extract and reuse one field grammar |
| Icon chosen by visual similarity | Treat icon as semantic asset; verify meaning and sizing |
| Local feedback applied to sibling pages | Keep local scope unless SPEC/user expands it |
