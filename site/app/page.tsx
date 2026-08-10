"use client";

import { useEffect, useMemo, useState } from "react";
import { firstUsablePath, modules, pages, sourceNotes } from "../content/course";

const statusLabel = {
  planned: "待开发",
  outlined: "仅提纲",
  "desk-researched": "资料已审",
  "fixture-tested": "实验已跑",
};

function setHash(id: string) {
  window.location.hash = id;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

export default function Home() {
  const [currentId, setCurrentId] = useState(firstUsablePath[0]);
  const [query, setQuery] = useState("");
  const [completed, setCompleted] = useState<string[]>([]);
  const [mobileNav, setMobileNav] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    const sync = () => {
      const id = window.location.hash.replace("#", "");
      setCurrentId(pages.some((page) => page.id === id) ? id : firstUsablePath[0]);
      setMobileNav(false);
    };
    sync();
    const restoreTimer = window.setTimeout(() => {
      const saved = window.localStorage.getItem("career-ai-completed");
      if (saved) setCompleted(JSON.parse(saved));
    }, 0);
    window.addEventListener("hashchange", sync);
    return () => {
      window.clearTimeout(restoreTimer);
      window.removeEventListener("hashchange", sync);
    };
  }, []);

  const current = pages.find((page) => page.id === currentId) ?? pages[0];
  const currentIndex = pages.findIndex((page) => page.id === current.id);
  const previous = currentIndex > 0 ? pages[currentIndex - 1] : undefined;
  const next = currentIndex < pages.length - 1 ? pages[currentIndex + 1] : undefined;
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

  const delivered = pages.filter((page) => page.status === "desk-researched" || page.status === "fixture-tested").length;
  const currentModule = modules.find((item) => item.id === current.moduleId)!;

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="mobile-menu" onClick={() => setMobileNav(!mobileNav)} aria-label="打开课程目录">目录</button>
        <a className="brand" href={`#${firstUsablePath[0]}`}>
          <span className="brand-mark">QE</span>
          <span><b>测试开发 × AI</b><small>从会测试，到会验证 AI 系统</small></span>
        </a>
        <div className="top-progress">
          <span>专业主路径已完成 {completed.filter((id) => firstUsablePath.includes(id)).length}/{firstUsablePath.length}</span>
          <div><i style={{ width: `${(completed.filter((id) => firstUsablePath.includes(id)).length / firstUsablePath.length) * 100}%` }} /></div>
        </div>
      </header>

      <aside className={`sidebar ${mobileNav ? "open" : ""}`}>
        <div className="course-summary">
          <p className="eyebrow">当前可用版本</p>
          <h2>从传统测试到 AI 质量工程</h2>
          <p>完整知识树保留；当前深度交付“需求文档到执行证据”八页实战。仅有主题但未完成逐题研究的页面继续显示为提纲。</p>
          <div className="summary-stats"><span><b>{delivered}</b> 深度正文</span><span><b>{pages.length - delivered}</b> 提纲/待重写</span></div>
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
          <div className="breadcrumb"><span>{currentModule.title}</span><span>›</span><span>{current.id}</span></div>
          <div className="lesson-meta">
            <span className={`status-badge ${current.status}`}>{statusLabel[current.status]}</span>
            <span>{current.type}</span><span>{current.duration}</span><span>更新于 2026-08-10</span>
          </div>
          <h1>{current.title}</h1>
          <p className="lead">{current.summary}</p>

          {current.status === "planned" || current.status === "outlined" ? (
            <section className="planned-panel">
              <p className="eyebrow">{current.status === "outlined" ? "仅保留知识位置" : "本页尚未开发"}</p>
              <h2>本页尚未通过逐题调研与教材正文门禁</h2>
              <p>{current.why}</p>
              <div className="planned-grid"><div><b>学完应当能够</b><p>{current.outcomes[0]}</p></div><div><b>最终产物</b><p>{current.artifact}</p></div></div>
              <p className="boundary"><b>当前证据边界：</b>{current.evidenceBoundary}</p>
            </section>
          ) : (
            <>
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
                  {block.table && <div className="table-wrap"><table><thead><tr>{block.table.headers.map((header) => <th key={header}>{header}</th>)}</tr></thead><tbody>{block.table.rows.map((row, rowIndex) => <tr key={`${block.title}-${rowIndex}`}>{row.map((cell, cellIndex) => <td key={`${rowIndex}-${cellIndex}`}>{cell}</td>)}</tr>)}</tbody></table>{block.table.caption && <small>{block.table.caption}</small>}</div>}
                  {block.code && <div className="code-box"><button onClick={() => copy(block.code!, `${current.id}-${index}`)}>{copied === `${current.id}-${index}` ? "已复制" : "复制"}</button><pre>{block.code}</pre></div>}
                  {block.expected && <div className="expected"><b>预期结果</b><p>{block.expected}</p></div>}
                  {block.warning && <div className="warning"><b>常见误区</b><p>{block.warning}</p></div>}
                </div>
              </section>)}

              <section className="practice-card">
                <p className="eyebrow">实操</p>
                <h2>练习与项目替换</h2>
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
        <div className="route-card"><b>当前深度路径</b><p>{firstUsablePath.join(" → ")}</p><small>测试依据 → 需求契约 → 评审 → 风险 → Oracle → 自动化 → 执行证据 → 变更回归</small></div>
      </aside>
    </div>
  );
}
