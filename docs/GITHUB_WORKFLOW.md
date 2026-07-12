# GitHub Workflow

Use this workflow so all four members can work in parallel without merge conflicts.

## Repository Setup

The repository should contain:

```text
README.md
docs/
transit_ops/
```

Recommended first commands after the GitHub repository exists:

```bash
git remote add origin <github-repo-url>
git add transitOps
git commit -m "Add TransitOps planning and architecture"
git push -u origin main
```

If the Odoo addon will live at the repository root, move `transit_ops/`, `docs/`, and `README.md` to root before the first implementation commit. Avoid changing the structure after the team starts coding.

## Branches

Create one branch per member:

```bash
git checkout -b member1-core-backend
git checkout -b member2-ui-dashboard
git checkout -b member3-ops-integration
git checkout -b member4-qa-docs
```

Each member pushes only their branch:

```bash
git push -u origin member1-core-backend
```

Member 3 is the release integrator and merges pull requests into `main`.

## Ownership Rules

| Member | Branch | Editable Files |
|---|---|---|
| Member 1 | `member1-core-backend` | `transit_ops/models/vehicle.py`, `driver.py`, `trip.py`, `transit_ops/data/sequence.xml` |
| Member 2 | `member2-ui-dashboard` | `security/*`, core `views/*`, dashboard `static/src/components/dashboard/*` |
| Member 3 | `member3-ops-integration` | manifest, imports, maintenance/fuel/expense/dashboard models and views |
| Member 4 | `member4-qa-docs` | `transit_ops/data/demo_data.xml`, `README.md`, `docs/*` |

Do not edit files outside your ownership list. If a fix is needed in another member's file, open an issue or comment on their pull request.

## Pull Request Rules

Every PR should include:

```text
Summary:
Files changed:
How tested:
Screenshots, if UI changed:
Known risks:
```

PR checks before merge:

- No unowned files changed.
- No frozen model, field, method, XML ID, or selection key was renamed.
- Addon install or upgrade was tested by Member 3 when production files changed.
- Dashboard screenshot was attached when dashboard UI changed.
- QA checklist was updated when behavior changed.

## Commit Style

Use small commits with clear messages:

```text
Add vehicle and driver models
Implement trip dispatch validation
Add TransitOps RBAC groups
Build dashboard client action shell
Add maintenance workflow
Add demo data and QA checklist
```

Avoid large mixed commits that change multiple owners' files.

## Daily Hackathon Merge Order

1. Scaffold PR from Member 3.
2. Backend PR from Member 1.
3. Operations/API PR from Member 3.
4. Security/views/dashboard PR from Member 2.
5. Demo/docs PR from Member 4.
6. Final release PR from Member 3 with install, upgrade, and demo-flow verification.

## Conflict Handling

If Git reports a conflict:

1. Stop and identify the conflicted file.
2. Check the ownership table.
3. The owner resolves the conflict.
4. Non-owners may explain the desired behavior but should not rewrite the file.

This rule is strict because the project is short and parallel. Ownership discipline is faster than arguing with merge conflicts during the final hour.

## Suggested GitHub Issues

Create these issues and assign them immediately:

| Issue | Assignee |
|---|---|
| Scaffold `transit_ops` addon and manifest | Member 3 |
| Implement vehicle, driver, trip, and sequence | Member 1 |
| Implement dispatch, complete, cancel validations | Member 1 |
| Implement RBAC groups and ACLs | Member 2 |
| Implement vehicle, driver, and trip views | Member 2 |
| Implement custom Owl dashboard frontend | Member 2 |
| Implement maintenance, fuel, and expense models | Member 3 |
| Implement dashboard backend API | Member 3 |
| Add operational views and actions | Member 3 |
| Add demo data | Member 4 |
| Add QA, visual QA, demo script, and submission docs | Member 4 |
| Run final install, upgrade, and demo workflow | Member 3 and Member 4 |

## Definition of Done

A branch is done when:

- It changes only owned files.
- It follows the frozen architecture contract.
- It has been tested locally or clearly marks what could not be tested.
- It has no install-breaking traceback.
- It has a concise PR summary for the release integrator.
