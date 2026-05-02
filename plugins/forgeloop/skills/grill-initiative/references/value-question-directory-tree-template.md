# Value Question Directory Tree Template

A Value Question Directory Tree is a directory-shaped map of decisive design uncertainties before sealing `DESIGN.md`.

It is not:

- a checklist
- a `DESIGN.md` outline
- a `PLAN.md` pre-split
- a Milestone / Task / PR breakdown
- a final decision record
- an evidence table

It asks:

> What must be understood before this candidate Initiative deserves a sealed `DESIGN.md`?

---

## 1. Tree Grammar

Build the tree with four layers:

```text
Root Question
└── Candidate-specific Decisive Uncertainty
    └── Activated Risk Lens or Sub-uncertainty
        └── Lxxx｜Source-checkable Design Uncertainty
```

Use compact directory-tree markdown. The tree should read like an expandable table of contents, not a form.

The final tree in `DESIGN.md` must read as authored project content, not a copied template. Remove all angle-bracket placeholders from the final tree.

Avoid repeating field labels such as:

```text
Why:
Evidence:
Recommendation:
Impact:
```

Evidence, recommendations, findings, and final decisions belong after focused investigation, not inside the tree.

---

## 2. Root Question

Always start with the candidate Initiative's central viability question:

```text
0. <这个候选 Initiative 是否值得进入 DESIGN.md 并最终封板？>
```

The root question is not asking whether code should be written. It asks whether the candidate has enough design significance, value, boundary, and risk to deserve a formal `DESIGN.md`.

The final root question should be candidate-specific. Do not leave the root as a generic placeholder.

---

## 3. Mandatory Viability Axes

Every tree should consider these axes, but only keep the branches that matter to this candidate.

```text
0. <这个候选 Initiative 是否值得进入 DESIGN.md 并最终封板？>
├── 1. <价值是否真实成立？>
├── 2. <边界是否足够清楚？>
├── 3. <真理源是否会被破坏？>
├── 4. <设计是否会引入架构熵？>
├── 5. <结果是否能被证明？>
└── 6. <如果不该这样做，应如何分流？>
```

Do not mechanically expand all axes. Delete or collapse axes that do not create meaningful uncertainty.

Mandatory axes are generation aids. Use them to discover candidate-specific parent nodes. Do not copy the axis names as final tree parent nodes unless the axis name itself is the actual decisive uncertainty for this candidate.

Prefer final parent nodes that name the candidate's real design tension, for example:

```text
0. 009 是否应该从 Studies 页面补丁升级为事件研究闭环并封为 DESIGN.md？
├── 1. 009 的价值是否来自真实研究结果，而不是页面展示？
├── 2. historical_backfill 是否能服务样本生成，而不滑向 trading backtest？
├── 3. EventStudyRun 是否必须成为唯一研究真理源？
├── 4. mock-seed / web fallback 是否会伪造 release readiness？
├── 5. raw close downgrade 是否足以支撑初版研究可信度？
└── 6. full-market runtime hardening 是否必须拆出后续 Initiative？
```

Do not copy this example unless it is the actual candidate under review.

---

## 4. Leaf ID Rule

Every retained leaf node must have a stable Leaf ID:

```text
L001｜<source-checkable design uncertainty?>
L002｜<source-checkable design uncertainty?>
L003｜<source-checkable design uncertainty?>
```

A retained leaf is any final question node kept in the tree.

Once a leaf is retained, it must never silently disappear. If it later proves invalid, duplicate, low-value, or out of scope, close it explicitly in the `Leaf Resolution Matrix` as one of:

```text
Rejected
Deferred
Merged
Out of Scope
```

Do not reuse a Leaf ID for a different question during Draft revision.

Do not renumber existing Leaf IDs unless the user explicitly asks for a full rewrite.

Parent nodes do not need IDs unless they are also retained as final leaf questions.

---

## 5. Axis Expansion Rules

### 5.1 Value Axis

Use this axis to test whether the Initiative has real value, not just activity.

```text
1. <价值是否真实成立？>
├── L001｜<用户真正要改变的是业务结果、系统能力、运行可信度，还是开发体验？>
├── L002｜<做完之后必须出现什么真实对象、状态变化或用户可见结果？>
├── L003｜<哪些结果只是“动作发生”，不能证明“价值成立”？>
└── L004｜<是否存在“零结果也算成功”的伪成功？>
```

Keep this axis when the candidate may confuse activity with outcome.

### 5.2 Boundary Axis

Use this axis to prevent one candidate from silently becoming multiple Initiatives.

```text
2. <边界是否足够清楚？>
├── L005｜<它是否足够成为 Initiative，而不是小修、Milestone、Task 或调研？>
├── L006｜<是否混入另一个目标，导致一个 DESIGN.md 承载两个战役？>
├── L007｜<哪些相邻问题看似相关，但一旦纳入会改变 Initiative 类型？>
└── L008｜<哪些问题应进入后续 Initiative，或直接排除？>
```

Do not include execution order, Milestone count, Task decomposition, PR sequencing, command choice, or exact file-edit steps here.

### 5.3 Truth Source Axis

Use this axis when the candidate touches data, state, rules, configuration, docs, runtime facts, generated artifacts, or user-visible truth.

```text
3. <真理源是否会被破坏？>
├── L009｜<唯一真理源是什么：数据源、状态源、规则源、配置源、接口源，还是文档源？>
├── L010｜<是否会复制一份派生真值，而不是引用 canonical source？>
├── L011｜<fixture / mock / fallback 是否可能冒充正式路径？>
├── L012｜<是否会出现双真值、双路径、双状态机或半迁移？>
└── L013｜<缺失、失败或不一致时，是 typed failure，还是 silent fallback？>
```

This axis is usually mandatory for data, state, workflow, generated-document, or release-readiness Initiatives.

### 5.4 Architecture Entropy Axis

Use this axis to identify where the design may increase long-term complexity.

Do not expand every lens. Activate only the lenses that the candidate actually touches.

```text
4. <设计是否会引入架构熵？>
├── <Interface Contract Lens 是否需要展开？>
├── <Data Model Lens 是否需要展开？>
├── <State Lifecycle Lens 是否需要展开？>
├── <Test Feedback Lens 是否需要展开？>
├── <Migration / Compatibility Lens 是否需要展开？>
├── <Runtime / Operations Lens 是否需要展开？>
└── <Security / Policy Lens 是否需要展开？>
```

Replace activated lens placeholder nodes with the appropriate lens subtree below. Remove unactivated lens nodes.

---

## 6. Risk Lens Library

### 6.1 Interface Contract Lens

Activate when the Initiative adds or changes an API, CLI, UI route, internal service boundary, adapter, repository, SDK call, module interface, skill interface, or document handoff interface.

```text
<Interface Contract Lens>
├── Lxxx｜<新增能力是复用正式入口，还是开了第二入口？>
├── Lxxx｜<输入、输出、错误语义、幂等语义是否需要裁决？>
├── Lxxx｜<调用方是否必须理解内部细节才能正确使用接口？>
├── Lxxx｜<业务规则是否会泄漏到多个 caller，而不是封装在深模块里？>
├── Lxxx｜<是否存在兼容、版本、迁移或废弃旧接口的长期裁决？>
└── Lxxx｜<这个接口是否会成为未来 Agent / CLI / 自动化流程的控制点？>
```

### 6.2 Data Model Lens

Activate when the Initiative touches schema, database tables, entity identity, derived fields, caches, parquet / files, migrations, indexing, snapshots, auditability, or generated document fields.

```text
<Data Model Lens>
├── Lxxx｜<核心实体是什么，生命周期边界在哪里？>
├── Lxxx｜<主键、唯一约束、去重语义是否能支撑重复运行？>
├── Lxxx｜<哪些字段是源字段，哪些字段是派生字段？>
├── Lxxx｜<是否存在“一眼方便”的冗余字段，未来会变成第二真值？>
├── Lxxx｜<schema / template 变化是否破坏历史数据、回放、回归或审计？>
├── Lxxx｜<数据缺失、迟到、重复、乱序时是否有正式语义？>
└── Lxxx｜<当前数据模型是否让未来 Reviewer 能判断事实来源？>
```

### 6.3 State Lifecycle Lens

Activate when the Initiative touches tasks, cases, workflow states, status transitions, retries, idempotency, recovery, partial success, concurrency, Draft/Sealed status, or document lifecycle.

```text
<State Lifecycle Lens>
├── Lxxx｜<状态从哪里开始，在哪里结束，失败后停在哪个合法状态？>
├── Lxxx｜<哪些状态转移必须幂等？>
├── Lxxx｜<重复运行、重试、部分成功、并发运行分别如何表现？>
├── Lxxx｜<是否存在跳过正式状态机的快捷路径？>
├── Lxxx｜<是否需要记录 transition reason，供解释、审查或恢复？>
└── Lxxx｜<如果中途失败，系统是否能重建运行态而不篡改真理源？>
```

### 6.4 Test Feedback Lens

Activate when acceptance depends on tests, fixtures, mocks, E2E flows, real data, CI, regression, reviewer checks, or Agent-runnable feedback loops.

```text
<Test Feedback Lens>
├── Lxxx｜<哪些行为不变量必须被测试，而不是测试内部实现？>
├── Lxxx｜<哪些边界可以 mock，哪些边界必须走真实路径？>
├── Lxxx｜<fixture 是否会掩盖真实数据、真实状态或真实接口问题？>
├── Lxxx｜<是否需要失败路径测试，证明系统不会 silent fallback？>
├── Lxxx｜<是否存在 Agent 可以重复运行的最小反馈环？>
└── Lxxx｜<测试失败时能否定位到设计问题，而不是只暴露实现噪音？>
```

### 6.5 Migration / Compatibility Lens

Activate when old and new paths may coexist.

```text
<Migration / Compatibility Lens>
├── Lxxx｜<这是替换旧路径，还是在旧路径上叠加补丁？>
├── Lxxx｜<新旧路径共存期间，哪条路径是正式路径？>
├── Lxxx｜<是否存在半迁移状态：旧路径未删，新路径未立？>
├── Lxxx｜<兼容窗口、删除条件、回退条件是否需要设计裁决？>
├── Lxxx｜<迁移是否会改变用户、调用方或数据消费者的契约？>
└── Lxxx｜<未来如何证明旧路径可以安全删除？>
```

### 6.6 Runtime / Operations Lens

Activate when the Initiative touches production-like execution, scheduling, scale, performance, data freshness, observability, failure recovery, or repeated Agent operation.

```text
<Runtime / Operations Lens>
├── Lxxx｜<本轮是否需要证明生产运行能力，还是只证明设计路径可信？>
├── Lxxx｜<运行规模、时间窗口、资源成本是否会改变 Initiative 类型？>
├── Lxxx｜<失败恢复、断点续跑、重试、超时是否属于本轮设计裁决？>
├── Lxxx｜<是否需要区分 sample readiness 与 full-runtime hardening？>
├── Lxxx｜<运行结果是否可复现、可追踪、可解释？>
└── Lxxx｜<哪些运行风险必须拆出后续 Initiative？>
```

### 6.7 Security / Policy Lens

Activate when the Initiative touches permissions, auth, secrets, privacy, regulated data, destructive operations, external calls, audit logs, or human confirmation.

```text
<Security / Policy Lens>
├── Lxxx｜<谁被允许触发、读取、修改或回滚这个能力？>
├── Lxxx｜<是否触及 secrets、凭证、权限边界或外部服务？>
├── Lxxx｜<失败时是否可能泄漏数据、绕过权限或扩大访问范围？>
├── Lxxx｜<是否需要审计日志、操作记录或人工确认？>
└── Lxxx｜<安全边界是否属于 DESIGN 裁决，而不是后续实现细节？>
```

---

## 7. Proof Axis

Use this axis to identify what kind of evidence can support later Decision Records.

Do not list exact filenames, commands, or screenshot paths here.

```text
5. <结果是否能被证明？>
├── Lxxx｜<什么证据能证明“结果成立”，而不只是“动作发生”？>
├── Lxxx｜<什么证据能证明没有绕过真理源？>
├── Lxxx｜<什么证据能证明失败路径被显式处理？>
├── Lxxx｜<哪些证据必须可复现、可回放或可审计？>
└── Lxxx｜<哪些证据只是辅助，不能作为 blocking acceptance？>
```

Specific evidence artifacts belong in Focused Context Findings, Decision Records, or `DESIGN.md` evidence requirements, not in the Value Question Tree.

---

## 8. Disposition Axis

Use this axis to keep the tree from forcing every candidate into sealed `DESIGN.md`.

```text
6. <如果不该这样做，应如何分流？>
├── Lxxx｜<哪些条件不满足时应 Reject，而不是继续设计？>
├── Lxxx｜<哪些不确定性过大时应 Defer to research？>
├── Lxxx｜<哪些混合目标应 Split into multiple Initiatives？>
├── Lxxx｜<哪些内容应进入后续 Initiative、Residual Risk 或 Rejected Alternative，而不是本轮 Scope？>
└── Lxxx｜<哪些风险可以留作 Residual Risk？>
```

---

## 9. Valid Node Test

A node is valid only if answering it differently may change at least one of:

- whether the candidate deserves `DESIGN.md`
- whether the `DESIGN.md` can be sealed
- selected design
- rejected alternatives
- Scope
- Non-Goals
- truth source
- interface contract
- data model boundary
- state lifecycle
- test feedback strategy
- evidence standard
- residual risks
- disposition: ready / split / defer / reject

If a node only affects Milestone order, Task detail, command choice, file name, implementation sequencing, or PR shape, remove it from the tree.

---

## 10. Tree-to-Design Coverage Expectation

Every retained leaf in the Value Question Directory Tree must later appear exactly once in the `Leaf Resolution Matrix`.

Valid leaf landings are:

- Decision Record
- Selected Design element
- Design Detail section
- Downstream Constraint
- Activation Blocker
- Design Follow-up
- Residual Risk
- explicit Rejection
- explicit Deferral
- explicit Merge
- explicit Out of Scope closure

This template only creates the question map. The later `DESIGN.md` must prove that retained questions did not become decorative.

Coverage by parent node, activated risk lens, or vague prose is not sufficient.

---

## 11. Rendering Rules

- Use directory-tree markdown.
- Parent nodes should be decisive uncertainties, not document section names.
- Parent nodes should be candidate-specific when possible; do not mechanically copy mandatory axis names.
- Leaf nodes must have stable `Lxxx` IDs.
- Leaf nodes should be design-risk questions, not implementation tasks.
- Keep depth to 2-3 levels.
- Avoid flat `Q001 / Q002 / Q003` lists as the main structure.
- Do not decide inside the tree.
- Do not include evidence bullets inside the tree.
- Do not include Milestone, Task, PR sequence, command lists, or evidence filenames.
- Do not leave angle-bracket placeholders in the final tree.
- After the tree, perform focused investigation, write Findings, close leaves in the Leaf Resolution Matrix, write Decision Records, and land accepted decisions in Selected Design / Design Details.

---

## 12. Architecture Entropy Radar

Use this radar to decide whether an Architecture Entropy branch or risk lens should be expanded.

Watch for:

- second truth: same fact maintained in two places
- second entrypoint: new shortcut bypasses the formal interface
- second state machine: old state flow remains while a new one appears
- half migration: old and new paths coexist without deletion conditions
- mock acceptance: tests pass through fixture while formal path remains unproven
- pass-through module: module adds names but hides no complexity
- god service: unrelated rules accumulate in one service
- leaky abstraction: caller must understand internal details
- fallback masking failure: default, empty, or mock result hides a real error
- permanent temporary flag: flag/config lacks lifecycle and deletion condition
- rule copying: same business rule appears in scan, API, UI, and tests
- unreplayable evidence: result cannot be reproduced from fixed input
- decorative question tree: leaves are listed but not closed in the Leaf Resolution Matrix
- chat truth drift: design body appears in chat but not in the durable `DESIGN.md`
