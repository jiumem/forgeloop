# Matt Pocock Skills v1.2.3 上游审计

审计日期：2026-08-14

## 结论与落地状态

值得升级，但不值得把固定 Commit 机械改成 `v1.2.3` 后整体同步。本次落地已经将 Forgeloop 固定到 `v1.2.3` 的 Commit `6acc160e`，并通过本地适配保留 Forgeloop 的授权、Reviewer 价值函数和最小作用量边界。

最值得吸收的是三类改动：`diagnosing-bugs` 的密钥脱敏、`improve-codebase-architecture` 的 YAGNI 热区聚焦，以及 `code-review`、`codebase-design`、`improve-codebase-architecture` 的跨 Harness 中性委派措辞。它们分别降低安全泄露、低价值架构审查和 Claude 专用提示失效的风险。[v1.2.3 Release](https://github.com/mattpocock/skills/releases/tag/v1.2.3) [v1.2.0 Release](https://github.com/mattpocock/skills/releases/tag/v1.2.0)

不应直接吸收的是 `wayfinder` 的自动并行研究与自动写研究分支，以及新增 `wizard` 的隐式触发。`grilling` 的分轮思想则针对真实存在的 20–30 轮串行访谈痛点进行了适配吸收：每轮只询问 3–5 个前提已满足的独立问题，最多 5 个，高影响或有依赖的问题仍单独处理。[round-by-round Grilling](https://github.com/mattpocock/skills/commit/a4b2009a1a3ac9575506c10b4c84f08f9bba7a38) [Wayfinder / Prototype changeset](https://github.com/mattpocock/skills/commit/77d207ef03219cc603e2832e1159cbdd1c91818e) [Wizard graduation](https://github.com/mattpocock/skills/commit/b3376f8d39848dd08572ec2667da4739a67c8c04)

落地采用了“先修同步边界，再分项吸收”的小闭环，而不是一次性接受全部上游行为。

## 实际比较基线

用户记忆中的 `v1.1.0` 是正确的版本世代，但升级前 Forgeloop 实际固定的是 Commit [`391a2701`](https://github.com/mattpocock/skills/commit/391a2701dd948f94f56a39f7533f8eea9a859c87)，不是 `v1.1.0` 标签。历史声明见[封板设计](../proposals/forgeloop-skill-suite-rebuild.md#L7)；当前 Pin 见 [`upstream-map.json`](../../tooling/forgeloop/config/upstream-map.json#L2)。

| 基线 | Commit | 时间（UTC） | 相对关系 |
|---|---|---|---|
| `v1.1.0` | [`d574778`](https://github.com/mattpocock/skills/commit/d574778f94cf620fcc8ce741584093bc650a61d3) | 2026-07-08 13:20:40 | Release 于 13:20:57 发布 |
| 升级前 Forgeloop 固定点 | [`391a270`](https://github.com/mattpocock/skills/commit/391a2701dd948f94f56a39f7533f8eea9a859c87) | 2026-07-10 13:14:59 | 比 `v1.1.0` 多 16 个提交 |
| 当前 Forgeloop / `v1.2.3` | [`6acc160`](https://github.com/mattpocock/skills/commit/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e) | 2026-08-06 14:05:05 | 比升级前固定点多 128 个提交 |

官方比较显示，实际待审范围为 128 个提交、118 个文件、2669 行新增和 1461 行删除：[固定点 → v1.2.3](https://github.com/mattpocock/skills/compare/391a2701dd948f94f56a39f7533f8eea9a859c87...6acc160e4e0cd062dbbbd7a1b26ae92855edf07e)。若从标签 `v1.1.0` 比较则是 144 个提交，因此本文所有集成判断都以 `391a2701` 为准，避免重复计算本地已经包含的 16 个提交。

官方没有发布或标签 `v1.2.1`；这个序列是 `v1.2.0`、`v1.2.2`、`v1.2.3`。[Releases](https://github.com/mattpocock/skills/releases) [Tags](https://github.com/mattpocock/skills/tags)

## 各 Release 的变化

### v1.2.0 — 2026-08-05 12:37:40 UTC

官方 Release 包含以下变化：[v1.2.0 Release](https://github.com/mattpocock/skills/releases/tag/v1.2.0)

- 为每个 Skill 增加 `agents/openai.yaml`，区分 Codex 的显式与隐式调用，并增加共享 `AGENTS.md`。[PR #551](https://github.com/mattpocock/skills/pull/551)
- 新增正式 Skill：`to-questionnaire`、`wizard`、`wait-what`。[PR #593](https://github.com/mattpocock/skills/pull/593) [PR #680](https://github.com/mattpocock/skills/pull/680) [PR #751](https://github.com/mattpocock/skills/pull/751)
- `prototype` 的逻辑原型改为单文件 HTML，可由非开发者直接操作；原型被视为可追溯的一手证据。[PR #763](https://github.com/mattpocock/skills/pull/763)
- 发布原生 Claude Code Plugin。[PR #536](https://github.com/mattpocock/skills/pull/536)
- `wayfinder` 明确使用“decision ticket”，并在建图后并行派发所有 Research tickets，结果写入 `research/<name>` 分支。[PR #763](https://github.com/mattpocock/skills/pull/763)
- `writing-great-skills` 破坏性重命名为 `writing-for-agents`，范围扩展到所有 Agent 消费的文档。[PR #763](https://github.com/mattpocock/skills/pull/763)
- `improve-codebase-architecture` 增加 YAGNI 范围过滤：优先用户指定方向，否则查看近期提交热区。[PR #533](https://github.com/mattpocock/skills/pull/533)
- `ask-matt` 增加 Phase Boundary 决策树，校正 `/handoff`、`/compact` 和 Wayfinder 的路由，并补齐 `grilling`、`resolving-merge-conflicts`。[PR #763](https://github.com/mattpocock/skills/pull/763)
- Setup 简化 Triage/Domain 询问，并统一 Local Tracker 为一 Ticket 一文件；这部分实现 Commit [`44eed54`](https://github.com/mattpocock/skills/commit/44eed545186ffd0263e8004867750b80cfddd215) 早于 Forgeloop 固定点，因此主体已经在本地基线中，实际新增只剩后续术语清理。
- `grilling` 从软件计划扩展到任意计划、决策和想法，并由“一次一个问题”改成“每轮询问当前全部 Frontier”。[PR #532](https://github.com/mattpocock/skills/pull/532) [PR #593](https://github.com/mattpocock/skills/pull/593)
- 删除六个未进入正式插件的旧 Skill，其中四个已被 `domain-modeling`、`codebase-design`、`triage`、`to-tickets`、`to-spec`、`improve-codebase-architecture` 吸收。[PR #752](https://github.com/mattpocock/skills/pull/752)
- 完成 `PRD` → `spec` 术语清理，涉及 `to-spec`、`code-review` 和 Tracker 模板。[PR #734](https://github.com/mattpocock/skills/pull/734)

### v1.2.2 — 2026-08-05 18:10:19 UTC

只有一项：修复 `writing-for-agents` 的 Codex 元数据，使其恢复模型可调用，并修正旧显示名。[v1.2.2 Release](https://github.com/mattpocock/skills/releases/tag/v1.2.2) [PR #766](https://github.com/mattpocock/skills/pull/766)

Forgeloop 没有映射这个 Skill，因此没有直接集成价值。

### v1.2.3 — 2026-08-06 14:05:28 UTC

- `diagnosing-bugs` 要求命令、输出和抓取产物先脱敏，凭据留在环境变量中；HITL 脚本也提示 `capture` 会回显。[PR #779](https://github.com/mattpocock/skills/pull/779)
- `code-review`、`codebase-design`、`improve-codebase-architecture` 删除 Claude Code 专用的 Tool 与 Agent type 名称，改成 Harness 中性委派。[PR #781](https://github.com/mattpocock/skills/pull/781)
- `wizard` 删除不可靠的分钟级耗时估计，只保留阶段进度。[PR #783](https://github.com/mattpocock/skills/pull/783)

## 对当前映射的真实影响

Forgeloop 当前映射 18 个上游 Skills，[映射清单](../../tooling/forgeloop/config/upstream-map.json#L4-L381)中有 13 个目录发生正文或 Reference 变化；`domain-modeling`、`grill-with-docs`、`research`、`resolving-merge-conflicts`、`handoff` 只有新增 Codex 元数据，没有主体行为变化。

| 本地目标 | 实际变化 | 判断 |
|---|---|---|
| `diagnosing-bugs` | Redact 规则与 HITL 回显警告 | **直接吸收**。安全收益明确，不扩大行为保证；现有 Authorization overlay 可以保留。[上游提交](https://github.com/mattpocock/skills/commit/efce423018fc6468a3239621f1c1bcaacc723801) [本地映射](../../tooling/forgeloop/config/upstream-map.json#L73-L103) |
| `codebase-design` | `DESIGN-IT-TWICE.md` 删除 `Agent tool` 专名 | **直接吸收**。仅提升 Harness 可移植性。[上游提交](https://github.com/mattpocock/skills/commit/14bfbbd8654a8d2910299e1a004c19c1979687d8) |
| `improve-codebase-architecture` | YAGNI 热区聚焦、Harness 中性派发、`design tree` 改为 `decision tree` | **适配吸收**。YAGNI 与“最小作用量”高度一致，但必须保留本地只读、空结果和授权边界。[上游 Commit](https://github.com/mattpocock/skills/commit/45afd8074a8b7de5fe073845d080fa9dd6c429fa) [本地封板边界](../proposals/forgeloop-skill-suite-rebuild.md#L170-L176) |
| `prototype` | Logic TUI 改为自包含 HTML、自由操作按钮和场景 Walkthrough | **适配吸收**。产品经理和领域专家可直接验证状态模型，价值高；但“自动建 throwaway branch、自动写 Issue 指针”不能因此获得新授权。[上游源码](https://github.com/mattpocock/skills/blob/v1.2.3/skills/engineering/prototype/LOGIC.md) [本地原型边界](../proposals/forgeloop-skill-suite-rebuild.md#L147) |
| `spec-standards-review` | `PRD` 术语清理、移除 Claude 专用派发语句 | **适配吸收**。保留本地固定 Scope 与双 Reviewer 隔离，不回退最近加入的交付价值函数和必要性门槛。[上游提交](https://github.com/mattpocock/skills/commit/14bfbbd8654a8d2910299e1a004c19c1979687d8) [本地映射](../../tooling/forgeloop/config/upstream-map.json#L7-L69) |
| `setup-forgeloop`、`to-spec` | `PRD` → `spec` 术语收尾 | **直接吸收正文，适配映射**。主体 Setup 改进已经包含在固定点，不能重复宣称升级收益。[上游提交](https://github.com/mattpocock/skills/commit/a2f9333669ff53db762c87ecda5a15442060a3be) |
| `tdd` | 接口形状有疑问时引用 `codebase-design` 词汇 | **适配吸收**。只在公共 Seam 的形状确实阻塞当前行为验证时引用；不能把普通实现自动升级为架构设计。[上游源码](https://github.com/mattpocock/skills/blob/v1.2.3/skills/engineering/tdd/SKILL.md#L18-L26) [本地 TDD overlay](../../tooling/forgeloop/config/overlays/tdd-append.md) |
| `wayfinder` | “decision ticket”术语；自动并行解决 Research tickets 并写分支 | **拆分处理**：吸收术语，不吸收自动执行。后者破坏本地“一次只解决一张 investigation ticket”的既有产品约束。[上游源码](https://github.com/mattpocock/skills/blob/v1.2.3/skills/engineering/wayfinder/SKILL.md#L103-L116) [本地元数据](../../tooling/forgeloop/config/skill-metadata.json#L116-L120) |
| `grilling`、`triage` | 整轮 Frontier 提问 | **适配集成**。吸收依赖感知的分轮思想，但不一次询问整个 Frontier：每轮默认 3–5 个、最多 5 个独立问题；高影响或作为其他问题前提的决策单独询问；用户可批量接受推荐或随时降回逐问。[上游源码](https://github.com/mattpocock/skills/blob/v1.2.3/skills/productivity/grilling/SKILL.md#L6-L20) [本地契约](../../plugins/forgeloop/skills/grilling/SKILL.md#L6-L24) |
| `ask-forgeloop` | 上游新增 Phase Boundary 树与新 Skill 路由 | **不直接集成**。本地使用完整 Router overlay，上游新正文会被覆盖，而新增 `PHASE-BOUNDARIES.md` 会成为无引用文件。只在 Forgeloop 自己出现上下文切换问题时单独设计。[本地 Overlay 映射](../../tooling/forgeloop/config/upstream-map.json#L5) |
| `to-tickets` | 删除上游末尾的 `/implement` 路由句 | **保留本地语义、更新适配锚点**。Forgeloop 仍需在发布后只提示用户显式启动 `$run-initiative`，不得自动启动。[本地目标正文](../../plugins/forgeloop/skills/to-tickets/SKILL.md#L186) |

## 新增 Skills 是否纳入 Forgeloop

| 上游新增项 | 判断 | 原因 |
|---|---|---|
| `to-questionnaire` | **暂不集成** | 有异步收集决策的真实价值，但没有进入 Forgeloop 当前 Spec/Ticket/Initiative 闭环；应先有用户场景，再决定它是新入口还是 `grill-with-docs` 的输出模式。[上游源码](https://github.com/mattpocock/skills/tree/v1.2.3/skills/productivity/to-questionnaire) |
| `wizard` | **不集成** | 会写 `.env`、GitHub Secrets 并引导外部控制台操作，且上游把它设为模型可调用；这与 Forgeloop 的显式授权和外部副作用边界冲突。[上游源码](https://github.com/mattpocock/skills/tree/v1.2.3/skills/engineering/wizard) |
| `wait-what` | **不集成为正式 Skill** | 三行式纠偏有用，但属于会话便利命令，不值得扩大正式工程 Workflow 清单。[上游源码](https://github.com/mattpocock/skills/blob/v1.2.3/skills/productivity/wait-what/SKILL.md) |
| `writing-for-agents` | **暂不集成** | 能指导 Agent 文档写作，但 Forgeloop 的正式清单聚焦产品研发闭环，且已有系统级 Skill Creator；新增会扩大产品面而不改善当前交付主路径。[上游源码](https://github.com/mattpocock/skills/tree/v1.2.3/skills/productivity/writing-for-agents) [本地正式清单](../proposals/forgeloop-skill-suite-rebuild.md#L106-L147) |
| 原生 Claude Plugin、旧 Skills 删除 | **不集成** | Forgeloop 是 Codex Plugin，且被删除的六项都不在当前 upstream-map 中。[v1.2.0 Release](https://github.com/mattpocock/skills/releases/tag/v1.2.0) |

## 为什么本次升级不能只改 Pin

### 1. 上游 Codex 元数据与本地唯一事实源冲突

`v1.2.0` 在每个上游 Skill 中新增 `agents/openai.yaml`，但 Forgeloop 已由 [`skill-metadata.json`](../../tooling/forgeloop/config/skill-metadata.json#L1-L121) 集中维护触发描述、显示名、短描述和默认 Prompt。升级前的同步器会递归收集所有上游文件，却只从“实际文件集合”排除 `agents/openai.yaml`；若只改 Pin，Expected 集合会包含上游 YAML，`--check` 会错误报告缺失，写入时也会先导入再覆盖。[同步器实现](../../tooling/forgeloop/scripts/sync_upstream.py#L81-L148)

本次落地已把上游 `agents/openai.yaml` 明确排除在导入集合之外，并继续以本地集中元数据为唯一事实源，没有合并两个来源。

### 2. 四个映射已经发生必要文本漂移

用 `v1.2.3` 源码运行现有 Required Replacements，首先会在四个映射上停止：

- `spec-standards-review`：Spec 搜索段落完成 `PRD` 清理，且 Claude 专用 `Agent tool/general-purpose` 句已删除；
- `improve-codebase-architecture`：`Agent tool/subagent_type=Explore` 改为 Harness 中性句；
- `setup-forgeloop`：上游删除已退休的 `qa` 引用，旧替换锚点不再存在；
- `to-tickets`：末尾 `/implement` 路由句被删除，旧替换锚点不再存在。

同步器会把任何缺失锚点作为硬错误，这是正确的防漂移设计，不应绕过。[Required Replacement 门禁](../../tooling/forgeloop/scripts/sync_upstream.py#L57-L64) [当前四处映射](../../tooling/forgeloop/config/upstream-map.json#L7-L69)

本次落地已显式重写这四个映射的锚点，并重新验证本地替换后的完整语义；Required Replacement 仍然硬失败，没有降级成静默 `replace`。

## 已执行的集成切片

### 切片 1：让同步器能安全理解新上游

1. Pin 已更新到 `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`。
2. Expected 导入集合已排除上游 `agents/openai.yaml`，保留本地集中元数据。
3. 四个漂移映射已修复；已经由上游原生解决的 Claude 专用替换已删除，同时保留 Forgeloop 的冻结 Scope、只读、授权和显式启动规则。
4. Dry-run、同步器单测和 drift check 已通过。

验收：同步器面对干净的 `v1.2.3` 源码可幂等生成；每个本地 `agents/openai.yaml` 仍完全来自 `skill-metadata.json`；不存在无引用的 `PHASE-BOUNDARIES.md`。

### 切片 2：吸收低风险高价值修正

已吸收 Redact、Harness 中性措辞、YAGNI 热区聚焦和 `PRD` 术语清理；全部本地 overlay/replacement 得到保留。

验收：诊断输出不会暴露测试凭据；架构扫描优先用户范围或近期活跃代码，找不到真实机会时仍返回空结果；双轴审查仍冻结同一 Scope；所有现有验证通过。

### 切片 3：对产品行为逐项裁决

已适配吸收 Prototype HTML、TDD → Codebase Design 必要性门槛、Wayfinder “decision ticket”术语和 Grilling 有界分轮；明确拒绝 Wayfinder 自动研究分支与隐式 Wizard。Prototype 的 Branch、Commit 和 Tracker 捕获仍需单独明确授权。

验收：Prototype 可被非开发者双击运行并验证状态；普通 TDD 不会因为“可以设计得更好”而进入架构工作；Wayfinder 仍一次只推进一张票，任何 Branch/Tracker 写入都经过既有授权。

## 审计复现命令

以下命令均从仓库根目录运行，只读：

```bash
gh api repos/mattpocock/skills/releases --paginate \
  --jq '.[] | [.tag_name,.published_at,.html_url] | @tsv'

gh api 'repos/mattpocock/skills/compare/391a2701dd948f94f56a39f7533f8eea9a859c87...6acc160e4e0cd062dbbbd7a1b26ae92855edf07e' \
  --jq '{status,ahead_by,behind_by,total_commits,file_count:(.files|length)}'

python3 tooling/forgeloop/scripts/sync_upstream.py --check
```

最后一条命令现已验证当前 `6acc160e` / `v1.2.3` 固定基线无漂移；完整回归另由 Forgeloop 测试套件和 Skill 校验器覆盖。
