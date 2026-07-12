# Forgeloop 编码 Skill 套件重构实施方案

状态：待执行
创建日期：2026-07-12
设计依据：`docs/proposals/forgeloop-skill-suite-rebuild.md`
上游基线：Matt Pocock Skills Commit `391a2701dd948f94f56a39f7533f8eea9a859c87`

## 1. 实施目标

在不安装或发布半成品实施分支的前提下，将 Forgeloop `2.5.0` 的五个本地文档型 Skills 重构为设计稿封板的 20 个 Tracker 驱动 Skills，并完成：

- GitHub、GitLab、Local Markdown 三套 Tracker 主路径；
- 单 Spec、多 Spec、依赖图、双 Reviewer、修复循环和最终验收；
- Codex Skill Frontmatter、`agents/openai.yaml` 与插件 Manifest 契约；
- 旧 Skills 的受控原位替换和下游历史文档的只读迁移入口；
- 可重复的静态校验、Fixture 验收和新线程安装冒烟。

## 2. 非目标与实施边界

- 不创建 `PLAN.md` 或 `LEDGER.md`；
- 不在对应替代闭环通过前删除旧 Skill；
- 不把 Matt 上游已有 Skill 契约重新设计一遍；
- 不在首版实现 Initiative 内并行 Frontier；
- 不实现 Linear、Jira 等 `Other` Tracker 的完整适配；
- 不自动发布 GitHub Release、推送分支或创建 PR，除非用户在发布阶段另行授权；
- 不额外触发完整 CI 来重复 Coder 与 Reviewer 的验证职责。

## 3. 实施策略

### 3.1 Git 版本化的原位重构

源码始终使用标准目录：

```text
plugins/forgeloop/
  skills/
```

版本边界由插件 SemVer 和 Git 承担，不创建任何目录级版本副本：

1. 从记录清晰的 `2.5.0` 源码 Commit 建立实施分支；
2. 将插件版本标记为 `3.0.0-dev.0`；
3. 每个闭环任务直接在标准 `skills/` 中新增、替换或删除对应 Skill；
4. 只有替代能力通过本任务验收后，才删除对应旧 Skill；
5. 每个任务形成可恢复的 Git Commit；
6. 开发中间 Commit 不安装、不发布；
7. 全部 Gate 通过后将 Manifest 封为 `3.0.0`，再执行本地安装冒烟。

### 3.2 上游继承

对 18 个有上游来源的 Skills 使用固定映射和机械转换，不手工重写正文。允许的转换仅包括：

- Skill/品牌名称；
- 文件夹和跨 Skill 引用路径；
- `research` → `primary-source-research`；
- `code-review` → `review-change`；
- `setup-matt-pocock-skills` → `setup-forgeloop`；
- `ask-matt` → `ask-forgeloop`；
- 移除 Claude 专用 `disable-model-invocation`；
- 生成 Codex `agents/openai.yaml`；
- 已封板的 `resolving-merge-conflicts` 安全收紧。

`recommend-initiatives` 和 `run-initiative` 是 Forgeloop 原生实现，不从上游 `implement` 拼接正文。

### 3.3 Skill 结构

每个 Skill 至少包含：

```text
<skill-name>/
  SKILL.md
  agents/openai.yaml
```

约束：

- `SKILL.md` Frontmatter 只包含 `name` 与 `description`；
- `skills/**` 下的正文、References、Tracker 模板和 UI 元数据全部使用英文；项目设计、实施与迁移文档继续使用中文；
- `description` 以 `Load when` 开头，只描述适用请求和必要的相邻边界，不复述内部流程、输出或规范；
- 仅用户调用的 11 个 Skills 在 `agents/openai.yaml` 设置 `policy.allow_implicit_invocation: false`；
- `default_prompt` 必须显式包含 `$<skill-name>`；
- `SKILL.md` 目标少于 500 行；
- 详细协议放到一层 `references/`，不深层嵌套；
- 不在 Skill 目录创建 README、安装指南或变更日志。

实现方式遵守 Skill Creator：

- `recommend-initiatives` 与 `run-initiative` 使用 `init_skill.py` 在标准 `skills/` 中初始化或重建；
- 有固定上游来源的 Skills 视为已有 Skill 导入，不重新生成正文；
- 所有 `agents/openai.yaml` 使用 `generate_openai_yaml.py` 生成或刷新，不手写容易漂移的 UI 元数据；
- 每次正文发生实质修改后重新核对并刷新对应 `agents/openai.yaml`。

## 4. 全局完成定义

任何任务只有同时满足以下条件才能标记完成：

1. **入口可识别**：Frontmatter 描述能区分应该触发和不应该触发的请求。
2. **核心行为闭环**：从用户入口或模型调用到明确结果，不依赖聊天中的隐藏决定。
3. **输出状态明确**：成功、空结果、阻塞、取消或失败均有可观察结果。
4. **错误暴露**：认证、权限、缺失配置、坏引用和状态冲突不会静默降级。
5. **关键边界覆盖**：至少包含一个成功 Fixture 和一个失败/边界 Fixture。
6. **结构校验通过**：运行 `quick_validate.py`，并通过套件静态校验器。
7. **无范围回归**：没有修改当前任务之外的上游继承内容或无关 Skills。
8. **证据可复查**：记录执行命令、Fixture、实际输出和差异摘要。

任务不能因为“文件已创建”或“文字看起来合理”而完成。

## 5. 依赖顺序

```text
M0 校验与导入基础
  -> M1 上游能力与用户入口
    -> M2 run-initiative 执行内核
      -> M3 集成验收与版本封板
        -> M4 本地安装冒烟与发布准备
```

每个 Milestone 必须通过自身 Gate 后才能进入下一阶段。

## 6. M0：校验与导入基础

### T0.1 建立实施基线与套件静态校验器

**目标**：让后续每个 Skill 都能在标准目录中被独立、确定性校验，并让所有中间状态可由 Git 恢复。

**变更范围**：

- 记录 `2.5.0` 源码 Commit；
- 将实施分支插件版本设为 `3.0.0-dev.0`；
- 创建 `2.5.0`、阶段性和最终 `3.0.0` 预期 Skill 清单；
- 创建轻量套件校验脚本，优先使用 Python 标准库；
- 创建 Fixture 清单校验，不实现行为模拟器。

**验收标准**：

- 基线 Commit 的 `skills/` 按 V2 清单校验为恰好五个 Skill；
- 实施分支使用标准 `skills/`，不存在目录级版本副本；
- 阶段性校验能清晰报告尚未完成的目标 Skill，而不是把开发中间态误报为发布成功；
- 最终模式要求恰好 20 个正式 Skills；
- 校验器能发现重复名称、目录名与 Frontmatter 不一致、缺失 `SKILL.md`、缺失 `agents/openai.yaml`、错误 Invocation Policy 和旧 Skill 引用；
- 校验器自身有正例和反例 Fixture；
- 运行校验不会修改文件；
- Manifest 始终发现标准 `skills/`，但预发布版本不得安装或发布。

**验证方法**：运行校验器的 `2.5.0` 成功用例、`3.0.0` 不完整用例和至少三个故意破坏的反例。

### T0.2 建立固定上游导入映射与漂移校验

**依赖**：T0.1。

**目标**：保证“原样继承”可以被机器验证，而不是依赖人工记忆。

**变更范围**：

- 建立 18 个上游来源到 `3.0.0` 目标目录的声明式映射；
- 提供导入或同步脚本，支持 `--check`/dry-run；
- 建立允许机械差异清单；
- 校验上游工作树 Commit 必须等于封板 Commit。

**验收标准**：

- 上游 Commit 不匹配时立即失败且不写文件；
- dry-run 列出所有来源、目标、重命名和允许差异；
- 连续执行两次结果幂等；
- `to-spec`、`to-tickets` 等直接继承正文在归一化机械替换后与上游一致；
- 未列入允许差异的正文变化导致校验失败；
- `recommend-initiatives`、`run-initiative` 不被导入脚本覆盖。

**验证方法**：正确 Commit 导入、错误 Commit 拒绝、人工篡改继承正文后三个用例。

### M0 Gate

- `2.5.0` 源码 Commit 已记录并可恢复；
- 实施分支使用 `3.0.0-dev.0` 与标准 `skills/`；
- 静态校验器和上游漂移校验均可重复执行；
- 所有失败用例提供可定位错误。

## 7. M1：上游能力与用户入口

### T1.1 落地 `setup-forgeloop` 与三套 Tracker 模板

**依赖**：M0。

**范围**：导入并机械改造上游 Setup、GitHub/GitLab/Local 模板、Domain 文档和 Triage 标签映射。

**验收标准**：

- GitHub Remote 推荐 GitHub，GitLab Remote 推荐 GitLab，无 Remote 可选择 Local；
- 用户一次只回答一个配置问题；
- 写入 `docs/agents/issue-tracker.md`、Domain 配置和需要时的标签映射；
- GitHub 使用 `gh`、GitLab 使用 `glab`、Local 使用 `.scratch/`；
- 缺少 `AGENTS.md`/`CLAUDE.md` 时按上游规则请求选择，不擅自创建；
- 重跑只更新已有配置块，不重复追加；
- 无认证或权限不足时明确失败，不回退到另一 Tracker；
- 三套 Setup Fixture 均通过。

### T1.2 落地交互设计闭环

**依赖**：T1.1。

**范围**：`grilling`、`domain-modeling`、`grill-with-docs`。

**验收标准**：

- `grilling` 一次只提出一个高影响问题并给出推荐答案；
- 代码库事实由 Agent 调查，不交给用户回忆；
- `domain-modeling` 只在术语或长期决定变化时更新 `CONTEXT.md`/ADR；
- `grill-with-docs` 不创建 Spec、Ticket 或代码；
- 未决问题存在时不会伪装成设计完成；
- 中文文档、技术标识和上游行为边界均保持正确。

### T1.3 落地大型探索闭环

**依赖**：T1.1、T1.2。

**范围**：`primary-source-research`、`prototype`、`wayfinder`。

**验收标准**：

- Research 只使用高信任一手来源并逐项引用；
- Prototype 明确可抛弃，不直接进入生产代码；
- Wayfinder 在 Tracker 创建 Map、Child Tickets、Blocking 与 Frontier；
- 单会话可看清的问题不会被膨胀为 Map；
- 每次只解决一个 Wayfinder Ticket；
- GitHub、GitLab、Local 的 Map/Claim/Resolve Fixture 均能得到等价结果。

### T1.4 落地 Spec 与 Ticket 发布闭环

**依赖**：T1.1、T1.2。

**范围**：`to-spec`、`to-tickets`，主体直接继承上游；`to-tickets` 仅追加 Forgeloop Acceptance Repair 与 Spec Revision Reconciliation 适配。

**验收标准**：

- `to-spec` 使用上游模板和发布规则，不加入自定义模板；
- 上下文不足时停止，不替用户发明决定；
- `to-tickets` 产生可在新鲜上下文完成的垂直切片；
- Wide Refactor 使用上游 expand–contract 规则；
- Parent、Blocking 与 `ready-for-agent` 按 Tracker 能力表达；
- 用户未批准拆分前不发布 Tickets；
- 用户显式请求 Acceptance Repair 时按每个 Finding 的 `repair_key` 查询复用，只为未匹配 Findings 创建最小修复 Tickets，不重新拆解完整 Spec；
- 用户显式请求 material Spec Revision 对账时保留 Completed 历史，只对受影响 Open Tickets 提出 `retain`、`update`、`supersede`、`create` 动作；
- 三套 Tracker 的单 Spec、多 Ticket、阻塞图 Fixture 均通过；
- 不创建 `PLAN.md` 或 `LEDGER.md`。

### T1.5 落地 Triage 闭环

**依赖**：T1.1、T1.2。

**范围**：`triage` 及其 Agent Brief、Out-of-Scope References。

**验收标准**：

- 能列出未分类、待 Triage、等待信息后有新回复的请求；
- Issue/PR/MR 的发现范围遵守 Tracker 配置；
- 在应用标签、评论或关闭前展示推荐并等待用户方向；
- `needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix` 有明确输出；
- 已实现请求与真正拒绝请求不会混入同一 Out-of-Scope 记录；
- 权限失败不造成部分状态静默成功。

### T1.6 落地工程实现 Primitives

**依赖**：T0.2。

**范围**：`tdd`、`codebase-design`。

**验收标准**：

- TDD 保持上游 Red-Green 与公共 Seam 纪律；
- 测试验证外部行为，不锁死实现细节；
- Codebase Design 统一 Deep Module、Seam、Adapter、Leverage 和 Locality 词汇；
- 两个 Skill 可被 Coder 复用，但不会自行扩大 Ticket Scope；
- `quick_validate.py` 与上游漂移检查通过。

### T1.7 落地诊断与冲突处理 Primitives

**依赖**：T1.6。

**范围**：`diagnosing-bugs`、`resolving-merge-conflicts`。

**验收标准**：

- Diagnosis 先建立可复现反馈环，再假设、插桩、修复和回归测试；
- 用户只要求诊断时不修改代码；
- Merge Conflict 先恢复双方意图；
- 意图不兼容时返回结构性 Blocker，不自行选边；
- 不自动执行破坏性重置、丢弃或放弃；
- 冲突解决改变代码时明确要求重新评审。

### T1.8 落地独立双轴审查

**依赖**：T1.1、T1.6。

**范围**：`review-change`，直接继承上游 `code-review` 的定性报告。

**验收标准**：

- 固定点无效或 Diff 为空时在创建 Reviewer 前失败；
- Spec 与 Standards 使用独立上下文；
- 两轴 Findings 并列呈现，不合并排序；
- 找不到 Spec 时按上游规则报告，而不是伪造 Spec Verdict；
- 默认只读，不修改代码或 Tracker。

### T1.9 落地发现型 Workflows

**依赖**：T1.6。

**范围**：`recommend-initiatives`、`improve-codebase-architecture`。

**验收标准**：

- Recommend 只读返回 1–3 个有仓库证据的跨类别候选；
- 缺少产品目标时降低产品价值置信度，不虚构路线图；
- 不写 `docs/initiatives/recommendations/**`；
- Architecture 只报告真实 Deepening Opportunity；
- 架构可视化写入 OS 临时目录；
- 两个 Workflow 不创建 Spec/Ticket 或修改生产代码。

### T1.10 落地 Handoff

**依赖**：T0.2。

**范围**：`handoff`。

**验收标准**：

- Handoff 只包含尚未进入正式产物、但续接必需的上下文；
- 默认写 OS 临时目录；
- 不复制完整 Tracker 状态或成为第二真理源；
- 新会话仅凭 Handoff 与正式产物即可定位下一步；
- 不包含凭据或不必要的大段历史。

### T1.11 最后落地 Router 与全部 UI 元数据

**依赖**：T1.1–T1.10。

**范围**：`ask-forgeloop`、20 个 `agents/openai.yaml`。

**验收标准**：

- Router 覆盖全部正式用户入口，不引用已删除 Skill；
- Router 只推荐，不自动启动其他用户调用 Workflow；
- 20 条 Frontmatter `description` 由 `config/skill-metadata.json` 集中维护，以 `Load when` 开头并能区分相邻 Skill；
- 20 个 Skill 目录中的 Markdown 与 YAML 不含中文内容，生成源同步保持英文；
- 11 个用户调用 Skills 的 `allow_implicit_invocation` 为 `false`；
- 9 个模型可调用 Skills 为 `true` 或使用默认值；
- 每个 `display_name`、`short_description`、`default_prompt` 与实际 Skill 一致；
- 所有 `default_prompt` 显式包含 `$skill-name`；
- 20 个 Skill 分别通过 `quick_validate.py`。

### M1 Gate

- 19 个非 `run-initiative` Skills 已在标准 `skills/` 中完成；
- 上游漂移校验无未授权差异；
- 三套 Tracker 的 Setup、Wayfinder、Spec/Ticket 发布路径通过；
- Router 与 UI 元数据通过静态校验；
- `grill-initiative` 与 `plan-initiative` 只有在对应替代闭环通过后才删除；
- 实施分支仍为预发布版本，不允许安装或发布。

## 8. M2：`run-initiative` 执行内核

### T2.1 建立运行协议骨架与 Local 单 Ticket 闭环

**依赖**：M1。

**目标**：先用 Local Markdown 完成最小端到端路径，再扩展远端 Tracker。

**范围**：

- 初始化 `run-initiative`；
- 将 Scheduler、Coder、Reviewer、Checkpoint、完成门禁和 Role Task Pack 拆入一层 References；
- 扩展 Local Tracker Runtime Operations；
- 实现单 Spec、单 Ticket、无修复的完整 Fixture。

**验收标准**：

- 输入正式 Spec 后能查询 Frontier、Claim Ticket、创建新 Coder 与双 Reviewer；
- Coder 只能返回封板的四种结果；
- 双 Reviewer 对同一 Base/Head 返回结构化 Verdict；
- Coder 验证、Reviewer 审查，Scheduler 不重复运行测试；
- 双 `PASS` 后按 Integration Policy 集成并关闭 Ticket；
- Ticket 集成后由 fresh Spec Acceptance Reviewer 取得最终 Acceptance PASS；
- 缺失配置、空 Frontier、坏 Spec 引用、脏工作区冲突和 Reviewer 不可用均明确停止；
- 不写 `PLAN.md`、`LEDGER.md` 或执行状态标签。

### T2.2 增加 GitHub Runtime Parity

**依赖**：T2.1。

**验收标准**：

- 使用 `gh` 完成 Frontier、Claim、结构化 Events、PR/Commit 关联和关闭；
- 使用原生 Sub-issues/Dependencies，能力缺失时按上游正文回退；
- `auto-merge` 与 `human-merge` 均有 Fixture；
- 认证、权限、Branch Protection 和 Required Checks 失败不会回退为 Local；
- 与 Local Happy Path 产生等价领域状态。

### T2.3 增加 GitLab Runtime Parity

**依赖**：T2.1。

**验收标准**：

- 使用 `glab` 完成 Frontier、Claim、Events、MR/Commit 关联和关闭；
- Native Blocking 不可用时按上游正文回退；
- Free/Premium 能力差异有明确分支；
- 认证、权限和 Protected Branch 失败可定位；
- 与 Local/GitHub Happy Path 产生等价领域状态。

### T2.4 增加双 Reviewer 修复循环与角色连续性

**依赖**：T2.1–T2.3。

**验收标准**：

- 任一轴 `REPAIR_REQUIRED` 都返回原 Coder；
- 两个轴保持独立，Coder 同时看到两边 Findings；
- 代码变化使两个旧 Verdict 失效；
- 两个 Reviewer 对新累计 Diff 重新签发 Verdict；
- `finding_id` 在修复轮次稳定；
- 修复继续同一 Ticket 的原 Coder 与两名原 Reviewer thread；
- 每张 Ticket 最多两轮普通修复，第二轮后仍有 Blocking Finding 时 `RUN_PAUSED`；
- 合约问题进入 `CONTRACT_BLOCKER`，不消耗普通修复预算。

### T2.5 增加 Branch、Integration 与冲突路径

**依赖**：T2.4、T1.7。

**验收标准**：

- 默认每 Ticket 独立 Branch；
- 只有 Ticket Graph 预先声明时使用共享 Integration Branch；
- 共享模式必须存在 `integrate-and-verify` Ticket；
- `human-merge` 停在可恢复状态，刷新后继续；
- Head 或 Base 实际变化使相关 Verdict 失效；
- 冲突解决改变代码后重新进入 Coder 与双 Reviewer；
- PR/MR 关闭但未合并不会关闭 Ticket；
- Scheduler 不额外触发完整 CI。

### T2.6 增加 Spec 最终验收

**依赖**：T2.5。

**验收标准**：

- 每个 Spec 集成后始终创建 fresh、隔离、只读的 Acceptance Reviewer；
- Ticket Reviewer 不跨 Ticket Agent Run 复用；
- Acceptance Verdict 绑定 Spec Revision 和最终 Commit；
- `ACCEPTANCE_BLOCKED` 只修复 Scheduler 输入或暂停，不生成 repair key；
- 失败时 Spec 保持打开并生成稳定 `repair_key`；只复用 `$to-tickets` 已显式创建的正式修复工作，不自行创建或隐式调用；
- 已关闭 Ticket 的历史 Verdict 不被改写；
- 所有修复工作完成前 Spec 不能关闭。

### T2.7 增加多 Spec Initiative 与跨 Spec 验收

**依赖**：T2.6。

**验收标准**：

- 单 Spec 不创建多余父对象；
- 多 Spec 输入先预览，并按 `initiative_revision` 幂等创建或复用持久化 Initiative Tracker Item；
- 增删成员 Spec 必须有 Tracker 原生用户确认，Event 记录确认引用与派生 `initiative_revision`，不得复制成员关系；
- 全部 Initiative Tickets 集成后冻结同一最终 Commit，依次完成成员 Spec Acceptance；
- 成员 Specs 在 Initiative Acceptance 前保持 Open；所有成员对同一最终 Commit PASS 后创建 fresh Initiative Acceptance Reviewer；
- Initiative PASS 后先关闭成员 Specs，最后关闭父 Item；Initiative Repair 路由到现有 owning Spec，不创建 Initiative 直属 Ticket或 reopen 状态；
- 跨 Spec `PASS` 前父 Item 保持打开；
- `CANCELLED`、`PAUSED`、`COMPLETED` 可区分；
- 跨 Spec 验收失败暂停并要求用户显式调用 `$to-tickets`，不伪造完成。

### T2.8 增加串行调度、幂等与恢复

**依赖**：T2.4–T2.7。

**验收标准**：

- 一个 Initiative 同时只有一张活动 Ticket；
- 每次完成后重新查询 Frontier；
- 并发 Scheduler Claim 以确定性规则产生一个胜者；
- 失败者不创建 Coder；
- Checkpoint 带 Run ID、事件特定幂等键和恢复所需的最小字段；
- 重复恢复不创建重复 Event；
- `EVENT_SUPERSEDED` 可以纠正错误而不改历史；
- Tracker 原生事实与 Events 冲突时停止并报告；
- 崩溃后可以沿原 Run ID 恢复；
- `PAUSED` 保留 Claim，`RUN_CANCELLED` 停止派发、尽力中断当前 child，并只释放当前 Run ID 的 Claim；
- Ticket 成功关闭后释放其 Claim，根 Item 完成关闭后释放根 Scheduler Claim；
- 跨 Scheduler 任务恢复不依赖旧 child thread，从 Tracker 与 Git 创建 fresh child；
- Spec 实质变化使用 `RUN_PAUSED` reason=`SPEC_CHANGE`，仅在用户显式调用 `$to-tickets` 对账后恢复；
- 不使用短 TTL 误判长任务死亡。

### M2 Gate

- `run-initiative` 的 Local、GitHub、GitLab Happy Path 全部通过；
- Repair、Integration、Spec Acceptance、Multi-Spec、Recovery Fixture 全部通过；
- `run-initiative/SKILL.md` 保持精简，详细协议单一来源；
- 20 个正式 Skills 全部完成；旧 `run-initiative-sequences` 已由多 Spec 闭环替代并删除；
- 插件仍为预发布版本，不允许对外发布。

## 9. M3：集成验收与版本封板

### T3.1 执行完整 Fixture 矩阵

**依赖**：M2。

必须覆盖：

1. 单 Spec、单 Ticket 简单闭环；
2. 单 Spec、多 Ticket Blocking Graph；
3. 多 Spec Initiative 与跨 Spec验收；
4. Spec Reviewer 失败后的修复循环；
5. Standards Reviewer 失败后的修复循环；
6. 双轴同时失败；
7. 修复预算耗尽；
8. `CONTRACT_BLOCKER`；
9. `human-merge` 暂停和恢复；
10. 共享 Integration Branch；
11. Spec 最终验收失败；
12. Initiative 最终验收失败；
13. 空 Frontier；
14. 认证/权限失败；
15. Reviewer 不可用；
16. 崩溃恢复与重复 Event；
17. GitHub、GitLab、Local 三平台等价主路径。
18. `NO_CHANGE_REQUIRED` 零 Diff 双 Reviewer；
19. 取消时按 Run ID 释放 Claim 且保留候选证据；
20. Spec 实质变化暂停并显式转交 `$to-tickets`；
21. Acceptance 修复工作按 `repair_key` 幂等复用；
22. 多 Spec `initiative_revision` 漂移时停止恢复。
23. `REVIEW_BLOCKED` 与 `ACCEPTANCE_BLOCKED` 的非 Repair 路由；
24. 候选代码 Check 失败回到原 Coder，外部 Check 失败暂停；
25. Local 成功路径释放 Ticket lock 与 `scheduler.lock`；
26. 多 Spec 所有 Acceptance 绑定同一最终 Commit；
27. 多 Spec 父 Item 创建响应不确定时按 Revision 查询复用。
28. Shared Reviewer 输入变化时两轴重审；
29. Spec Revision 只对账 Open Tickets并保留 Completed 历史；
30. Initiative Repair 路由 owning Specs、重新执行所有 Spec Acceptance，且不 reopen。

**验收标准**：每个 Fixture 都包含初始状态、入口 Prompt、预期写入、禁止写入、终态和失败诊断；行为输出由新鲜上下文验证，不把预期答案泄漏给执行 Agent。

### T3.2 执行遗留清理与版本封板

**依赖**：T3.1 全部通过。

**范围**：

- 记录并验证 `2.5.0` 源码 Commit 可在临时目录恢复；Tag/Release 留到取得发布授权后执行；
- 确认五个旧 Skill 已被替代或删除，标准 `skills/` 中只保留正式清单；
- 更新 Manifest 至 `3.0.0`；
- 更新插件描述、关键词和最多三个默认 Prompt；
- 更新中文 README 和必要的兼容说明；
- 新增中文 `2.5.0`→`3.0.0` 迁移文档。

**验收标准**：

- 活动目录恰好 20 个 Skills；
- 不存在 `legacy-*` 或同义别名；
- Manifest 不再描述 DESIGN/PLAN/LEDGER/Milestone；
- 新 Skills 不读取或写入 `docs/initiatives/**`，Setup 只做只读检测；
- 迁移文档说明完成/归档保持只读、活动 Initiative 的两条迁移路径和回退方式；
- 所有旧名称只允许出现在迁移说明或设计历史中；
- 预发布版本的 Fixture 结果在 `3.0.0` 封板后再次通过。

### T3.3 执行结构与插件验证

**依赖**：T3.2。

**验收标准**：

- 20 个 Skill 分别通过 Skill Creator `quick_validate.py`；
- 套件校验器按最终 20 Skill 清单通过；
- Plugin Creator `validate_plugin.py` 通过；
- Manifest 使用严格 SemVer，路径均存在；
- 默认 Prompt 不超过三个，每条不超过 128 字符；
- 没有 `[TODO: ...]`、Claude 专用 Invocation 字段或失效资源引用；
- 上游漂移校验通过。

### M3 Gate

- 标准插件目录已经是完整 `3.0.0`；
- 所有静态、Fixture 和插件验证通过；
- V2 可从已记录源码 Commit 恢复；
- 尚未对外发布。

## 10. M4：本地安装冒烟与发布准备

### T4.1 本地 Cachebuster、重装与新线程冒烟

**依赖**：M3。

**范围**：使用 Plugin Creator 的 `update_plugin_cachebuster.py` 和已配置 Marketplace 重装流程，不手改 Marketplace。

**验收标准**：

- Cachebuster 只替换版本 Build Metadata，不堆叠；
- 能确认当前插件来自正确的本地 Marketplace；
- 重装成功后在新 Codex 线程发现 20 个 Skills；
- 用户调用型 Skills 不被隐式注入；
- 模型调用型 Skills 在匹配任务中可触发；
- 至少冒烟 `setup-forgeloop`、`to-spec`、`to-tickets`、`review-change`、Local `run-initiative`；
- 冒烟产物使用临时 Fixture 仓库，不污染本项目。

### T4.2 发布候选检查

**依赖**：T4.1。

**验收标准**：

- 将开发 Cachebuster 恢复为发布版本 `3.0.0`；
- 重新运行全部静态与插件验证；
- 生成中文 Breaking Change 摘要、迁移说明和验证证据；
- 准备但不执行 `2.5.0` Tag/Release 与 `3.0.0` 发布命令；
- Commit 信息采用可生成更新日志的格式，例如 `refactor(plugin)!: 重构为 Tracker 驱动的 Skill 套件`，正文列出行为、验证和 Breaking Change；
- 所有 Git/GitHub 操作遵循项目约束并使用全局配置的 `gh` CLI 流程；
- 在用户明确授权前不推送、不创建 PR、不打 Tag、不发布 Release。

### M4 Gate

- 本地安装与新线程行为通过；
- 发布候选版本无 Cachebuster；
- 迁移与回退说明完整；
- 等待用户单独授权发布。

## 11. 验收证据格式

每个任务交付时必须提供：

```text
Task: <任务 ID>
Entry: <验证入口>
Changed: <实际修改范围>
Commands: <执行过的校验命令>
Fixtures: <通过的正例/反例>
Result: PASS | BLOCKED
Errors: <失败路径及诊断，若无则 None>
Out of scope: <明确未做事项>
```

只有 `Result: PASS` 且对应 Milestone Gate 满足后才能进入下一任务。

## 12. 关键风险与控制

| 风险 | 控制 |
|---|---|
| 18 个上游 Skills 手工复制后漂移 | 固定 Commit、声明式映射、允许差异清单、漂移校验 |
| 开发中间态被误安装或发布 | 标准目录原位开发，但使用预发布版本、实施分支和任务 Gate；中间 Commit 禁止安装发布 |
| Invocation 误用 Claude 字段 | Frontmatter 只含 `name/description`，策略写 `agents/openai.yaml` |
| `run-initiative` 单文件膨胀 | SKILL 保留入口与主循环，协议进入一层 References |
| 三个平台行为分叉 | 共享领域契约 + 平台等价 Fixture |
| Reviewer 与 Scheduler 重复验证 | Coder 验证、Reviewer 审查、Scheduler 只编排 |
| 新旧状态双写 | 新 Skills 静态禁止 `PLAN.md`/`LEDGER.md` 运行写入 |
| 原位重构后无法回退 | 开工前记录并实测 `2.5.0` 源码 Commit 恢复；每个任务独立 Commit；授权发布后再创建 Tag/Release |
| CI 与外部平台成本失控 | Mock/Fixture 优先，真实平台只做最小冒烟，CI 按仓库既有策略自然运行 |

## 13. 方案完成标准

本实施方案可以进入执行，当且仅当：

- 任务顺序不存在循环依赖；
- 每个任务都有独立入口、行为、输出、错误和验证方法；
- 每个旧 Skill 只有在对应替代闭环通过后才删除；
- 开发中间 Commit 使用预发布版本且不安装、不发布；
- M3 之前没有任何发布动作；
- 所有封板设计条款都至少映射到一个任务和一个 Fixture；
- 发布阶段仍保留单独的用户授权门禁。
