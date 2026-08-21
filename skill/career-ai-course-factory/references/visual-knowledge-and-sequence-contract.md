# Visual Knowledge and Sequence Contract

## Stable identity versus learner order

Keep stable `page_id` values for traceability. Add a separate learner-facing `display_number` that is exactly `1..N` in the released navigation order. Module-local order, source IDs, database positions, aliases, and historical catalog numbers must never appear as the primary sequential lesson number.

Every prerequisite must occur earlier than its consumer. The previous/next chain must match the same ordered list. Reordering requires regenerating the visual-sequence manifest and fidelity hashes.

## Required artifact

Create `research/visual-sequence-manifest.json` with an exact record for every promised page. Each page declares its display number, prerequisites, the knowledge relationship being taught, required visual kinds, and repository-owned visual artifacts.

Choose the visual by relationship:

- concept taxonomy or knowledge system -> concept map;
- state and lifecycle -> state/lifecycle flow;
- actor or component interaction -> sequence diagram;
- component, data, trust, or deployment boundary -> architecture/data-flow view;
- symptom to diagnosis -> decision tree;
- metrics to business decision -> metric tree;
- professional growth and evidence -> career evidence ladder;
- staged validation or rollout -> gate/ring diagram.

Each visual names `visual_id,kind,purpose,source_path,alt_text,caption,nodes,edges,source_refs`. Store SVG, Mermaid, or another repository-owned inspectable source. A decorative card, generic five-box pipeline, screenshot without provenance, or a diagram reused across unrelated pages fails. Nodes and edges must express topic-specific semantics, failure paths, evidence points, and decision boundaries.

## Learner-view checks

Verify the rendered visual at desktop and narrow mobile widths, alt text, text readability, source-to-render hash closure, and page linkage. The caption explains what decision the visual supports and what it does not prove.

## Anti-bypass tests

Fail on skipped/duplicated display numbers, prerequisite inversion, broken previous/next order, missing visual files, fewer than five meaningful nodes or four relationships for an engineering page, duplicate page visual paths, remote-only diagrams, or visual claims that are not sourced in the page evidence package.
