import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the test-development AI tutorial shell", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /测试开发 × AI/);
  assert.match(html, /从传统测试到 AI 质量工程/);
  assert.match(html, /先重建测试开发这份工作，再判断 AI 应该改哪里/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|SkeletonPreview/);
});

test("ships only validated public pages without empty catalog placeholders", async () => {
  const response = await render();
  const html = await response.text();
  for (const id of ["TD-F01", "TD-P01", "TD-P02", "TD-P03", "TD-P04", "TD-P05", "TD-P06", "TD-P07", "TD-P08"]) assert.match(html, new RegExp(id));
  for (const id of ["TD-AP01", "TD-AP02", "TD-AP03", "TD-AP04", "TD-AP05", "TD-AP06", "TD-AP07", "TD-AP08"]) assert.match(html, new RegExp(id));
  for (const id of ["TD-S03", "TD-A03", "TD-A06", "TD-C01", "TD-T12", "TD-B06"]) assert.doesNotMatch(html, new RegExp(`data-page-id="${id}"`));
  assert.doesNotMatch(html, /完整课程|仅提纲|待开发|仅保留知识位置|本页尚未通过逐题研究/);
  assert.match(html, /实验已跑/);
  assert.match(html, /资料已审/);
});
