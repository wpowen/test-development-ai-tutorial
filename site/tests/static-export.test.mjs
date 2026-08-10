import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const html = await readFile(new URL("../dist-github-pages/index.html", import.meta.url), "utf8");

test("static GitHub Pages export contains the professional curriculum", () => {
  for (const id of ["TD-P01", "TD-S03", "TD-A03", "TD-A06", "TD-C01", "TD-T12"]) assert.match(html, new RegExp(id));
  for (const id of ["TD-AP01", "TD-AP04", "TD-AP06", "TD-AP08"]) assert.match(html, new RegExp(id));
  assert.match(html, /专业主路径已完成/);
  assert.match(html, /localStorage/);
  assert.match(html, /搜索需求、接口、TTFT/);
  assert.equal((html.match(/"moduleId":"TD-/g) ?? []).length, 60);
  assert.doesNotMatch(html, /"status":"planned"/);
  assert.match(html, /"status":"outlined"/);
});

test("static export ships syntactically valid client JavaScript", () => {
  const match = html.match(/<script>([\s\S]*)<\/script>/);
  assert.ok(match, "inline client script must exist");
  assert.doesNotThrow(() => new vm.Script(match[1], { filename: "github-pages-inline.js" }));
});

test("static export does not include private Sites configuration", () => {
  assert.doesNotMatch(html, /hosting\.json|project_id|account_id/i);
});
