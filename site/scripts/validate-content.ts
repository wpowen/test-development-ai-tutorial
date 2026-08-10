import { firstUsablePath, pages, releaseScope, sourceNotes } from "../content/course.ts";

const errors: string[] = [];
const byId = new Map(pages.map((page) => [page.id, page]));

if (pages.length < 60) errors.push(`knowledge catalog must contain the original map plus the deep pilot, found ${pages.length}`);
if (byId.size !== pages.length) errors.push("page IDs must be unique");
if (releaseScope.mode !== "pilot-path") errors.push("current release must declare pilot-path scope");
if (releaseScope.catalogComplete) errors.push("pilot-path release cannot claim catalogComplete=true");
if (releaseScope.promisedPageIds.length !== 9) errors.push("profession-reality plus requirements-to-evidence path must promise exactly 9 deep pages");
if (new Set(releaseScope.promisedPageIds).size !== releaseScope.promisedPageIds.length) errors.push("promised IDs must be unique");
if (firstUsablePath.join(",") !== releaseScope.promisedPageIds.join(",")) errors.push("learner path must equal promised deep-pilot pages");
if (firstUsablePath[0] !== "TD-F01") errors.push("deep path must start with profession reality reconstruction");

const bannedGenericPhrases = [
  "先把真实问题说清楚",
  "按证据顺序完成工作流",
  "在最小业务场景里亲手做一次",
  "迁移到你的项目",
  "轮到你动手",
  "本页完成后",
  "你会带走",
];

for (const id of firstUsablePath) {
  const page = byId.get(id);
  if (!page) {
    errors.push(`usable path references unknown page ${id}`);
    continue;
  }
  if (["planned", "outlined"].includes(page.status)) errors.push(`usable path page ${id} is not delivered`);
}

for (const page of pages) {
  for (const dependency of page.prerequisites) {
    if (!byId.has(dependency)) errors.push(`${page.id} references unknown prerequisite ${dependency}`);
    if ((byId.get(dependency)?.order ?? 999) >= page.order) errors.push(`${page.id} prerequisite ${dependency} must appear earlier`);
  }
  if (page.status === "planned" || page.status === "outlined") {
    if (releaseScope.promisedPageIds.includes(page.id)) errors.push(`${page.id} is promised but not delivered`);
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
  const learnerCopy = JSON.stringify({ summary: page.summary, why: page.why, blocks: page.blocks, practice: page.practice, completion: page.completion });
  for (const phrase of bannedGenericPhrases) {
    if (learnerCopy.includes(phrase)) errors.push(`${page.id} contains generic/template phrase: ${phrase}`);
  }
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

console.log(`Tutorial content valid: ${releaseScope.promisedPageIds.length} deep pages delivered; ${pages.length} topics visible.`);
