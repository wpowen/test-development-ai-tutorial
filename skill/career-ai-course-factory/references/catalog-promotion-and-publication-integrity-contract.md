# Catalog, Promotion, and Publication Integrity Contract

Use this contract whenever tutorial pages move from the internal catalog to a learner-facing tutorial or release archive. These gates are independent of prose quality, page count, static build success, and author-written delivery status.

## Required machine-readable artifacts

The authoring package must contain:

- `research/catalog-manifest.json`: the only ordered catalog identity surface;
- `research/support-ownership.json`: exact page ownership for architecture and material bundles;
- `research/executability-audit.json`: one current machine verdict per candidate public page;
- `research/topics/<page-id>/promotion-receipt.json`: the page-specific promotion decision;
- `research/publication-closure.json`: source, tutorial, static export, and ZIP-member hash closure.
- `research/capability-profiles.json`: exact professional capability profile for every public page;
- `research/professional-evidence.json`: model, integration, clean-room, practitioner, and learner evidence lanes;
- `research/status-registry.json`: one current hash-pinned human verdict per scope with explicit supersession.
- `research/source-assimilation-ledger.json`: exact frozen-source section/atom closure and disposition record;
- `research/source-semantic-projection.json`: exact source-function projection into learner pages, visuals, reusable assets, and exercises;
- `research/learner-usability-reuse.json`: beginner term dependencies, observable actions, failure recovery, and reusable-artifact contract per public page;
- `research/visual-sequence-manifest.json`: continuous display order plus repository-owned visual sources and hashes.

The assembled release must contain public-safe projections named `CATALOG-MANIFEST.json`, `PAGE-PROMOTION-MANIFEST.json`, `EXECUTABILITY-MANIFEST.json`, `ARTIFACT-CLOSURE.json`, `SOURCE-ASSIMILATION-MANIFEST.json`, `SOURCE-SEMANTIC-PROJECTION.json`, `LEARNER-USABILITY-REUSE.json`, `VISUAL-SEQUENCE-MANIFEST.json`, `CAPABILITY-PROFILES.json`, `PROFESSIONAL-EVIDENCE.json`, and `STATUS-REGISTRY.json`. `RELEASE-MANIFEST.json` pins the hash of each projection.

## Canonical catalog

`catalog-manifest.json` records `schema_version`, `catalog_id`, `content_version`, ordered `page_ids`, `previous_validated_page_ids`, and one page record per ID. Page records use exact IDs and name an exact `support_bundle_id`.

- Page records and ordered `page_ids` must match exactly.
- A `validated-subset` public set must be a subset of this catalog.
- A `complete-catalog` public set must equal the ordered canonical catalog.
- Do not reconstruct the catalog independently from TypeScript arrays, curriculum counts, directory names, HTML, or release archives.

If the new public set removes a previously validated page, add a repository-owned JSON scope-change record and reference it from the release scope or catalog manifest. It records the previous and current ordered sets, exact removed IDs, rationale, approver, approval time, and `APPROVED` verdict. A silent page-count decrease fails.

## Exact support ownership

`support-ownership.json` contains bundles with `bundle_id`, exact `owner_page_ids`, `shared`, `applicability`, and ordered `material_refs`.

- Wildcards, loose prefixes, partial IDs, title tests, and unanchored regular expressions are not owners.
- A non-shared bundle has exactly one owner.
- A shared bundle names every allowed page and explains why the same files and architecture apply.
- A public page's ordered material links must match its owned bundle. A group default must not overwrite page-specific support.

## Promotion and executability

Every candidate public page must first pass its fourteen-file topic package. The research contract files are selected explicitly by `claim-inventory.json`:

`research-brief.md`, `source-pack.csv`, `research-runs.json`, `claim-inventory.json`, the selected receipt (`deep-research-receipts.json` or `codex-research-receipts.json`), the matching contradiction matrix and saturation record, `evidence-synthesis.md`, `engineering-blueprint.md`, `manuscript.md`, `comparison.md`, `lab-manifest.json`, `validation.md`, and `projection-ledger.json`.

Its `promotion-receipt.json` then records the exact fourteen-file inventory, `PASS` verdict, editorial score of at least 90, boundary-preservation score of 100, the current executability-audit path and hash, exact learner-material hashes, validation time, and reviewer. The receipt belongs to one exact page ID.

`research/executability-audit.json` records one unique entry per candidate public page. Publication requires `verdict=PASS` and `finding_count=0`. A desk-researched or fixture-tested label cannot override a failed or stale executability audit.

The technical-editorial protected-item inventory remains the information-preservation authority. Rewriting the receipt together with weakened content is not a valid review; changed facts, commands, fields, numbers, citations, uncertainty, scope, or boundaries must return to technical review.

## Hash closure

`publication-closure.json` pins the current canonical catalog and tutorial JSON. For every page-material link it records:

- exact `page_id` and tutorial `href`;
- authoring `source_ref`;
- static-export `dist_ref`;
- ZIP `archive_member`;
- one SHA-256 value shared by all three byte-identical copies.

The entry set must exactly cover all learner-facing material links. Source files, static exports, and archive members must exist, stay inside their declared roots, and match the pinned hash. The ZIP member set must exactly equal the declared member set and must not contain absolute or parent-traversal paths.

## Gate order

Run the gates in this order:

1. canonical catalog and release scope;
2. exact support ownership;
3. fourteen-file topic package including claim-level Deep Research and research-to-page projection;
4. page promotion receipt and executability PASS;
5. source-to-tutorial-to-static-to-ZIP hash closure;
6. exact source assimilation, beginner/reuse, visual/sequence, capability, five-lane professional evidence, and status-supersession projections;
7. complete-solution and assembled public-release validation.

Any failure keeps the affected page internal and blocks downstream release assembly.
