# BI / Data Product Adapter

This adapter proposes question dimensions for thin BI/data-product requirements. It is not project truth and must not include project-specific routes, components, services, ports, or object facts.

## Candidate Dimensions

| Dimension | Questions |
| --- | --- |
| Metric / data definition | What is the business definition, grain, time window, refresh cadence, and versioning rule? |
| Permission scope | Who can see, configure, edit, export, share, or receive the output? How do data permissions filter results? |
| Consumption entry | Where does the configured object take effect, and where does the user perceive value? |
| Organization / project / folder | Which organizational unit owns the object? Is scope personal, team, project, tenant, or global? |
| Data lifecycle | How are create/update/delete, rename, archive, restore, permission loss, and upstream deletion handled? |
| Approval / lifecycle control | If approval, publish, offline, delete, withdraw, resubmit, callback, or external handling appears, which operations are controlled, which are explicitly out, and who confirmed that scope? |
| Version / consumption state | Which version is draft, pending, approved, active, historical, rejected, or withdrawn? Which version can downstream reports, dashboards, metrics, exports, alerts, or APIs read? |
| Audit / lineage / impact | What must be logged, traced, explained, or shown as downstream impact? |
| Exception states | What happens for stale data, missing source, delayed refresh, empty result, no permission, duplicate name, or partial failure? |
| Verification | Which acceptance checks prove the business effect, not just the management UI? |

## Use Rules

- Use this adapter only to generate candidate gaps and recommended defaults.
- Freeze facts only from PRD, user confirmation, source recon, or Evidence Profile.
- Move project-specific findings into the target repository's generated profile.
