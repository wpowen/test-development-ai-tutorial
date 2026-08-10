# TD-PS05 · Web UI 兼容性、无障碍与视觉回归

## Research brief

业务场景是客服工作台完成退款：鼠标、键盘和辅助技术用户都必须读到金额、风险提示和确认对话框；1280px 与 390px 视口、中文/英文长文本不能遮挡批准控件。传统做法只跑主路径点击和一张桌面截图，遗漏焦点顺序、语义名称、窄屏溢出、字体/语言差异和错误状态。AI 可以聚类截图差异、解释重复违规和提出 CSS 候选，但不能证明辅助技术用户可完成任务，也不能自动批准基线。工具选型为 WCAG + Playwright accessibility/visual checks，必要时接 axe-core，人工保留语义审查。

## Source pack

- WCAG 2.2：<https://www.w3.org/TR/WCAG22/>，提供可感知、可操作、可理解和健壮性成功标准；自动规则不覆盖全部语义体验。
- Playwright Visual Comparisons：<https://playwright.dev/docs/test-snapshots>，提供 screenshot baseline；官方说明 OS、浏览器、硬件和 headless 差异会影响结果。
- Playwright keyboard/mouse interaction：<https://playwright.dev/docs/input>，支持可观察的输入操作；不能替代真实辅助技术验证。
- axe-core 官方仓库：<https://github.com/dequelabs/axe-core>，提供自动化 a11y 规则引擎；通过不等于人工可用性证明。

## Evidence synthesis

事实：自动 a11y 规则、键盘/焦点路径、语义阅读顺序、响应式布局和像素差异是不同检查层。事实：视觉基线必须固定字体、OS、浏览器、数据、时区和动画，否则差异不可解释。工程综合：矩阵由用户风险、流量和市场语言裁剪；批准基线的变更记录必须包含元素、原因、commit 和责任人。

AI 变化在于可辅助截图差异分类、长文本生成和候选修复定位；工程边界是 AI 不得关闭差异、放宽规则或替人工语义检查。失败模式包括 `aria-label` 缺失、焦点被困、RTL/长文本溢出、动态时间污染截图、字体未安装、预期设计变更直接更新基线。页面材料目前仅 static-reviewed。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 用户/输入方式（输入） | 定义客服角色、键盘-only、辅助技术假设、locale、文本长度和高风险控件。 |
| 浏览器与视口矩阵（处理） | 依据真实用户风险选择 Chromium/WebKit、1280/390、zh-CN/en-US；记录选择理由与版本。 |
| DOM/语义检查（门禁） | 跑可访问名称、role、对比度和结构规则；阻断级违规不得被截图通过覆盖。 |
| 键盘/焦点路径（证据） | 记录 Tab 顺序、焦点可见性、对话框进入/退出和提交后的业务可达性。 |
| 视觉快照（处理/证据） | 稳定动态数据后保存基线、截图 hash、差异面积和 mask；不跨环境混用基线。 |
| 差异诊断（处理） | 区分 CSS、字体、数据、locale、动画、网络和真实回归；AI 仅输出候选分类。 |
| 人工批准与门禁（人工决策） | 高风险对话框、付款、权限和预期设计变化由责任人审核；未解释差异阻断合并。 |

可执行物料是兼容矩阵 YAML、键盘旅程、长文本/RTL fixture、axe 报告 schema 和视觉审批记录。检查顺序是语义、键盘、响应式、视觉、人工。

## Manuscript map

用“点击通过但键盘无法批准退款”的反例开场。再展示一个 390px 英文长文本导致确认按钮溢出的 fixture，区分自动规则、焦点路径、视觉 baseline 和人工语义。页面解释为何动态区域要稳定化而非全部 mask，并给出差异报告的证据字段。AI 作为诊断助手，不作为 baseline owner。

## Editorial review

没有把 WCAG 自动扫描写成合规认证，也没有把截图相似度写成可用性结论。保留市场、输入方式、动态内容和基线审批等业务条件；工具能力与人工责任清晰分开。真实产品、辅助技术和目标市场尚未执行，相关结论均标为 desk-researched。

## Validation

当前状态：`desk-researched`，未在目标工作台、真实辅助技术或固定浏览器矩阵上运行。

后续可离线升级为 fixture-tested：`validate_accessibility_fixture.py` 检查角色、名称和焦点序列；`render_viewport_fixture.py` 生成 1280/390 视口结果；`inject_long_rtl_text.py` 检查溢出检测；`compare_visual_manifest.py` 检查字体/locale/commit 元数据；`require_visual_approval.py` 阻止未签名基线更新。离线规则不能替代屏幕阅读器和真实用户审查。
