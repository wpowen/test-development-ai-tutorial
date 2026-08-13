# Profession methodology acquisition protocol

## Evidence lanes

Acquire methods from profession-authority (standards, syllabi, regulators), practitioner-workflow (directly observed work and postmortems), executable-artifact (repositories, schemas, runbooks), and counterevidence. AI or vendor material can establish capability, not professional necessity. Preserve publisher group and source family so copied pages are not counted as independent evidence.

## Method record

Each method record contains `method_id`, name, work domain, input/work object, observable steps, protected outcome, decision rights, risks/failure costs, prerequisites, artifacts, oracle or verification method, rationale, source refs with locator/version/hash, owner, freshness, limitations, unknowns, and status. The record must also declare `source_authority` or `precedence`, its owner, and evidence; there is no default document-type ordering.

## Compare and adjudicate

Compare methods on purpose, scope, assumptions, evidence strength, repeatability, oracle availability, cost, and residual risk. Record agreements, disagreements, and an adjudication decision; do not silently choose the newest, most convenient, or most familiar source. A conflict becomes a review question and `BLOCKED` until an accountable owner closes it.

## Freshness and gates

Record access date, effective date, version, superseded sources, and refresh trigger. Mark missing, stale, inaccessible, or internally unknown evidence explicitly as `UNKNOWN`; never fill it with model recall. Gate downstream selection on a resolvable source, explicit authority, method rationale, independent oracle, and named owner.
