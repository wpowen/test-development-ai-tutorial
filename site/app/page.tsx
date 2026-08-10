"use client";

import { useEffect, useMemo, useState } from "react";
import { firstUsablePath, modules, pages, sourceNotes } from "../content/course";

const statusLabel = {
  planned: "待开发",
  "desk-researched": "资料已审",
  "fixture-tested": "实验已跑",
};

function setHash(id: string) {
  window.location.hash = id;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

export default function Home() {
  const [currentId, setCurrentId] = useState("TD-T01");
  const [query, setQuery] = useState("");
  const [completed, setCompleted] = useState<string[]>([]);
  const [mobileNav, setMobileNav] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    const sync = () => {
      const id = window.location.hash.replace("#", "");
      setCurrentId(pages.some((page) => page.id === id) ? id : "TD-T01");
      setMobileNav(false);
    };
    sync();
    const saved = window.localStorage.getItem("career-ai-completed");
    if (saved) setCompleted(JSON.parse(saved));
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, []);

  const current = pages.find((page) => page.id === currentId) ?? pages[0];
  const previous = pages.find((page) => page.order === current.order - 1);
  const next = pages.find((page) => page.order === current.order + 1);
  const visiblePages = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return pages;
    return pages.filter((page) => `${page.id} ${page.title} ${page.summary} ${page.artifact}`.toLowerCase().includes(keyword));
  }, [query]);

  const toggleComplete = () => {
    const updated = completed.includes(current.id)
      ? completed.filter((id) => id !== current.id)
      : [...completed, current.id];
    setCompleted(updated);
    window.localStorage.setItem("career-ai-completed", JSON.stringify(updated));
  };

  const copy = async (value: string, key: string) => {
    await navigator.clipboard.writeText(value);
    setCopied(key);
    window.setTimeout(() => setCopied(null), 1200);
  };

  const delivered = pages.filter((page) => page.status !== "planned").length;
  const module = modules.find((item) => item.id === current.moduleId)!;

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="mobile-menu" onClick={() => setMobileNav(!mobileNav)} aria-label="打开课程目录">目录</button>
        <a className="brand" href="#TD-T01">
          <span className="brand-mark">QE</span>
          <span><b>测试开发 × AI</b><small>从会测试，到会验证 AI 系统</small></span>
        </a>
        <div className="top-progress">
          <span>首条路径已完成 {completed.filter((id) => firstUsablePath.includes(id)).length}/{firstUsablePath.length}</span>
          <div><i style={{ width: `${(completed.filter((id) => firstUsablePath.includes(id)).length / firstUsablePath.length) * 100}%` }} /></div>
        </div>
      </header>

      <aside className={`sidebar ${mobileNav ? "open" : ""}`}>
        <div className="course-summary">
          <p className="eyebrow">当前可用版本</p>
          <h2>第一条完整学习路径</h2>
          <p>8 页从基础概念走到 RAG 质量门禁。其余页面保留位置，但不冒充已完成。</p>
          <div className="summary-stats"><span><b>{delivered}</b> 已交付</span><span><b>{pages.length - delivered}</b> 待开发</span></div>
        </div>
        <label className="search-box">
          <span>⌕</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索 RAG、Agent、CI…" />
        </label>
        <nav className="course-nav" aria-label="课程目录">
          {modules.map((group) => {
            const groupPages = visiblePages.filter((page) => page.moduleId === group.id);
            if (!groupPages.length) return null;
            return <section key={group.id}>
              <h3>{group.title}</h3>
              <p>{group.subtitle}</p>
              {groupPages.map((page) => <button
                key={page.id}
                data-page-id={page.id}
                className={`nav-page ${page.id === current.id ? "active" : ""}`}
                onClick={() => setHash(page.id)}
              >
                <span className="page-number">{String(page.order).padStart(2, "0")}</span>
                <span className="page-name">{page.title}<small>{page.type} · {statusLabel[page.status]}</small></span>
                <span className={`status-dot ${completed.includes(page.id) ? "done" : page.status}`} />
              </button>)}
            </section>;
          })}
        </nav>
      </aside>

      <main className="reader">
        <div className="reader-inner">
          <div className="breadcrumb"><span>{module.title}</span><span>›</span><span>{current.id}</span></div>
          <div className="lesson-meta">
            <span className={`status-badge ${current.status}`}>{statusLabel[current.status]}</span>
            <span>{current.type}</span><span>{current.duration}</span><span>更新于 2026-08-10</span>
          </div>
          <h1>{current.title}</h1>
          <p className="lead">{current.summary}</p>

          {current.status === "planned" ? (
            <section className="planned-panel">
              <p className="eyebrow">本页没有冒充完成</p>
              <h2>知识位置已经确定，正文尚未达到交付门禁</h2>
              <p>{current.why}</p>
              <div className="planned-grid"><div><b>学完应当能够</b><p>{current.outcomes[0]}</p></div><div><b>最终产物</b><p>{current.artifact}</p></div></div>
              <p className="boundary"><b>当前证据边界：</b>{current.evidenceBoundary}</p>
            </section>
          ) : (
            <>
              <section className="outcome-card">
                <div><span>本页完成后</span><ul>{current.outcomes.map((item) => <li key={item}>{item}</li>)}</ul></div>
                <div><span>你会带走</span><strong>{current.artifact}</strong><small>不是“听懂了”，而是可检查的职业产物</small></div>
              </section>

              <section className="why-card"><b>为什么测试开发需要这一页</b><p>{current.why}</p></section>

              {current.prerequisites.length > 0 && <section className="prerequisites"><b>前置页面</b>{current.prerequisites.map((id) => {
                const page = pages.find((item) => item.id === id);
                return <button key={id} onClick={() => setHash(id)}>{id} · {page?.title}</button>;
              })}</section>}

              {current.blocks.map((block, index) => <section className="content-block" key={block.title} id={`section-${index}`}>
                <div className="section-index">{String(index + 1).padStart(2, "0")}</div>
                <div className="section-body">
                  <h2>{block.title}</h2>
                  {block.body.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
                  {block.bullets && <ul>{block.bullets.map((item) => <li key={item}>{item}</li>)}</ul>}
                  {block.code && <div className="code-box"><button onClick={() => copy(block.code!, `${current.id}-${index}`)}>{copied === `${current.id}-${index}` ? "已复制" : "复制"}</button><pre>{block.code}</pre></div>}
                  {block.expected && <div className="expected"><b>你应该看到 / 得出</b><p>{block.expected}</p></div>}
                  {block.warning && <div className="warning"><b>别踩这个坑</b><p>{block.warning}</p></div>}
                </div>
              </section>)}

              <section className="practice-card">
                <p className="eyebrow">轮到你动手</p>
                <h2>练习与迁移</h2>
                <ol>{current.practice.map((item) => <li key={item}>{item}</li>)}</ol>
              </section>

              <section className="completion-card">
                <div><p className="eyebrow">完成检查</p><h2>满足这些条件，才算学完</h2></div>
                <div>{current.completion.map((item) => <label key={item}><input type="checkbox" /> <span>{item}</span></label>)}</div>
                <button className={completed.includes(current.id) ? "completed" : ""} onClick={toggleComplete}>{completed.includes(current.id) ? "✓ 已标记完成" : "标记本页完成"}</button>
              </section>

              <section className="evidence-card">
                <h2>证据与边界</h2>
                <p>{current.evidenceBoundary}</p>
                <div className="sources">{current.sourceIds.map((id) => sourceNotes[id] && <a key={id} href={sourceNotes[id].url} target="_blank" rel="noreferrer"><b>{id}</b>{sourceNotes[id].title}</a>)}</div>
              </section>
            </>
          )}

          <nav className="page-nav">
            {previous ? <button onClick={() => setHash(previous.id)}><small>← 上一页</small><b>{previous.title}</b></button> : <span />}
            {next && <button className="next" onClick={() => setHash(next.id)}><small>下一页 →</small><b>{next.title}</b></button>}
          </nav>
        </div>
      </main>

      <aside className="right-rail">
        <p className="eyebrow">本页导航</p>
        {current.blocks.map((block, index) => <button key={block.title} onClick={() => document.getElementById(`section-${index}`)?.scrollIntoView({ behavior: "smooth" })}>{index + 1}. {block.title}</button>)}
        <div className="route-card"><b>首条可用路径</b><p>{firstUsablePath.map((id) => id.replace("TD-T", "")).join(" → ")}</p><small>最终交付：RAG 发布质量门禁</small></div>
      </aside>
    </div>
  );
}
