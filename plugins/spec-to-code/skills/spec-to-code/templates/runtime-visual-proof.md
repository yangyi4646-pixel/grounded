# Runtime Visual Proof

> Required for style-affecting changes. `N/A + reason` is allowed only when the implementation has no rendered visual/style impact.

| Surface | Rendered Node | Token / Style Readback | Computed / Screenshot Evidence | Layout Invariant | Result |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | pass / fail / unchecked |

## Evidence Rules

- Parent class is not enough if a child renderer owns the actual text/icon/badge.
- Token name is not enough; record token value, computed style, screenshot, DOM proof, or why it is unchecked.
- For tables, tags, badges, tooltips, icons, typography, and status marks, verify the actual node that the user sees.
