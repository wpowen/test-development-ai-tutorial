import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const html = await readFile(new URL("../dist-github-pages/index.html", import.meta.url), "utf8");

test("static GitHub Pages export contains the professional curriculum", () => {
  for (const id of ["TD-F01", "TD-P01", "TD-P02", "TD-P03", "TD-P04", "TD-P05", "TD-P06", "TD-P07", "TD-P08"]) assert.match(html, new RegExp(id));
  for (const id of ["TD-AP01", "TD-AP02", "TD-AP03", "TD-AP04", "TD-AP05", "TD-AP06", "TD-AP07", "TD-AP08"]) assert.match(html, new RegExp(id));
  for (const id of ["TD-S03", "TD-A03", "TD-A06", "TD-C01", "TD-T12", "TD-B06"]) assert.doesNotMatch(html, new RegExp(`"id":"${id}"`));
  assert.match(html, /专业主路径已完成/);
  assert.match(html, /localStorage/);
  assert.match(html, /搜索需求、执行证据、TTFT/);
  assert.equal((html.match(/"moduleId":"TD-/g) ?? []).length, 17);
  assert.doesNotMatch(html, /"status":"planned"/);
  assert.doesNotMatch(html, /"status":"outlined"|"status":"blocked"/);
  assert.doesNotMatch(html, /仅保留知识位置|本页尚未开发|本页尚未通过逐题研究|提纲\/待重写/);
  assert.match(html, /需求文档到执行证据|需求契约/);
  assert.doesNotMatch(html, /本页完成后|你会带走|轮到你动手|你应该看到 \/ 得出|别踩这个坑/);
});

test("static export ships syntactically valid client JavaScript", () => {
  const match = html.match(/<script>([\s\S]*)<\/script>/);
  assert.ok(match, "inline client script must exist");
  assert.doesNotThrow(() => new vm.Script(match[1], { filename: "github-pages-inline.js" }));
});

test("static export does not include private Sites configuration", () => {
  assert.doesNotMatch(html, /hosting\.json|project_id|account_id/i);
});
