import { firstUsablePath, pages, releaseScope, sourceNotes } from "../content/course.ts";

const errors: string[] = [];
const byId = new Map(pages.map((page) => [page.id, page]));

if (pages.length !== 52) errors.push(`complete catalog must contain exactly 52 course pages, found ${pages.length}`);
if (byId.size !== pages.length) errors.push("page IDs must be unique");
if (releaseScope.mode !== "complete-catalog") errors.push("public full release must declare complete-catalog scope");
if (!releaseScope.catalogComplete) errors.push("complete-catalog release must set catalogComplete=true");
if (releaseScope.promisedPageIds.length !== pages.length) errors.push("complete-catalog promised IDs must equal the full catalog");
if (new Set(releaseScope.promisedPageIds).size !== pages.length) errors.push("complete-catalog promised IDs must be unique");
for (const page of pages) if (!releaseScope.promisedPageIds.includes(page.id)) errors.push(`complete-catalog scope does not promise ${page.id}`);
if (firstUsablePath.length !== pages.length) errors.push("complete-catalog learner path must contain every page");
if (firstUsablePath[0] !== "TD-F01") errors.push("first usable path must start at the professional baseline entry TD-F01");

for (const id of firstUsablePath) {
  const page = byId.get(id);
  if (!page) {
    errors.push(`usable path references unknown page ${id}`);
    continue;
  }
  if (page.status === "planned") errors.push(`usable path page ${id} is still planned`);
}

for (const page of pages) {
  for (const dependency of page.prerequisites) {
    if (!byId.has(dependency)) errors.push(`${page.id} references unknown prerequisite ${dependency}`);
    if ((byId.get(dependency)?.order ?? 999) >= page.order) errors.push(`${page.id} prerequisite ${dependency} must appear earlier`);
  }
  if (page.status === "planned") {
    errors.push(`${page.id} is planned inside a complete-catalog release`);
    if (page.blocks.length || page.practice.length || page.completion.length) errors.push(`${page.id} planned page must not masquerade as delivered content`);
    continue;
  }
  const contentLength = JSON.stringify(page.blocks).length;
  if (contentLength < 750) errors.push(`${page.id} content is too thin (${contentLength} chars)`);
  if (page.outcomes.length < 3) errors.push(`${page.id} needs at least 3 observable outcomes`);
  if (page.blocks.length < 4) errors.push(`${page.id} needs at least 4 teaching blocks`);
  if (page.practice.length < 3) errors.push(`${page.id} needs at least 3 practice or transfer actions`);
  if (page.completion.length < 3) errors.push(`${page.id} needs at least 3 completion checks`);
  if (page.sourceIds.length < 3) errors.push(`${page.id} needs at least 3 source references`);
  for (const sourceId of page.sourceIds) if (!sourceNotes[sourceId]) errors.push(`${page.id} references unknown source ${sourceId}`);
  if (page.evidenceBoundary.length < 35) errors.push(`${page.id} evidence boundary is too thin`);
  if (page.type === "跟做") {
    const codeBlocks = page.blocks.filter((block) => block.code).length;
    const expectedBlocks = page.blocks.filter((block) => block.expected).length;
    if (codeBlocks < 1 || expectedBlocks < 1) errors.push(`${page.id} guided lab needs commands/examples and observable expected results`);
    if (page.status === "fixture-tested" && (codeBlocks < 2 || expectedBlocks < 2)) {
      errors.push(`${page.id} fixture-tested lab needs at least two runnable/observable steps`);
    }
  }
}

if (errors.length) {
  console.error("Tutorial content invalid:\n- " + errors.join("\n- "));
  process.exit(1);
}

console.log(`Tutorial content valid: ${pages.length}/${pages.length} pages delivered under complete-catalog scope.`);
