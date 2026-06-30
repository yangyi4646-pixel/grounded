# Scope Boundary

| Surface / Unit | Affected Surfaces | Non-Goals | Propagation Rule | Owner | Source |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Decision Rules

| Situation | Handling |
| --- | --- |
| Current screenshot / current page feedback | Default to current surface only |
| User says "all", "global", "everywhere", "consistent across" | Put expansion in Propagation Rule |
| Shared renderer may affect multiple surfaces | List Non-Goals or return for confirmation |
| Scope Boundary missing | spec-to-code may only handle current surface and must not propagate |
