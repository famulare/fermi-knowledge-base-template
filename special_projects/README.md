# Special Projects

A top-level component for **bounded work** whose scope or structure is sufficiently
out-of-step with the main `raw/`→`meta/` flow that forcing it into that flow would
distort it.

**Characteristics:**
- Has its own internal hierarchy (not required to follow raw/meta separation)
- Scoped to a bounded project with a clear purpose and completion state
- Can be ingested into the main KB later via standard workflows, but stands alone first
- Includes a `README.md` and (for significant projects) a `design-contract.md`

**Examples:** collaboration retrospectives, research sprints, cross-project analyses,
design exercises, evaluation reports.

**To start one:** copy `_template/` to `special_projects/<project-name>/` and fill it in.
