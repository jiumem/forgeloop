# Total Task Doc 参考模板

<!-- forgeloop:anchor document-position -->
## 文档定位

- 阶段：`Total Task Doc`
- 平面：planning 正式成果文档
- 主要读者：`planner`、`total_task_doc_reviewer`、下游 runtime `coder` / reviewers，以及后续 admission 或 control 角色通过 sealed 引用读取
- 主要目的：把上游已经 sealed 的 planning 决策压缩成一张轻薄、强索引、可直接执行的执行地图，而不是重新打开设计裁决

这份文档不是第二篇设计长文，不是迁移账本，不是 reviewer verdict，也不是实现教程。

<!-- forgeloop:anchor questions-this-doc-must-answer -->
## 这份文档必须回答什么

- 这张执行地图继承了哪些已经 sealed 的上游 planning artifact 与决策
- Initiative 的边界与成功标准是什么
- Initiative 如何被切成 Milestone、Task 与集成路径
- 每个 Task 属于哪个 Milestone，依赖关系和验收标准分别是什么
- 分支与 PR 应如何收敛，而不是反过来替代对象切法
- 下游角色应从哪里寻找验收与证据入口
- sealed 之后哪些 residual risk 可以保留，哪些 follow-up 被有意延后

<!-- forgeloop:anchor required-structure -->
## 必需结构

只能使用下列一级和二级标题。二级标题才是下游 `coder` 与 `reviewer` 阅读时真正稳定的合同。除非 workflow 明确要求临时例外，否则不要另外发明一套平行结构。

默认保留所有二级标题。如果某节确实不适用，也要保留标题，并用一句简短理由标记为 `N/A`，不要直接删掉。

```markdown
# <Initiative Name> 总任务文档（Total Task Doc）

<!-- forgeloop:anchor input-baseline-and-sealed-decisions -->
## 1. 前置输入与决策基线（Input Baseline And Sealed Decisions）
<!-- forgeloop:anchor input-baseline-and-sealed-decisions/requirement-summary -->
### 1.1 需求摘要（Requirement Summary）
<!-- forgeloop:anchor input-baseline-and-sealed-decisions/design-refs -->
### 1.2 设计引用（Design Refs）
<!-- forgeloop:anchor input-baseline-and-sealed-decisions/gap-analysis-refs -->
### 1.3 差距分析引用（Gap Analysis Refs, if applicable）
<!-- forgeloop:anchor input-baseline-and-sealed-decisions/sealed-decisions -->
### 1.4 已封板决策（Sealed Decisions）
<!-- forgeloop:anchor input-baseline-and-sealed-decisions/execution-boundary -->
### 1.5 执行边界（Execution Boundary）
<!-- forgeloop:anchor input-baseline-and-sealed-decisions/initiative-reference-assignment -->
### 1.6 Initiative 法定引用指派（Initiative Reference Assignment）

<!-- forgeloop:anchor initiative -->
## 2. Initiative 总览（Initiative）
<!-- forgeloop:anchor initiative/background -->
### 2.1 背景（Background）
<!-- forgeloop:anchor initiative/scope -->
### 2.2 范围（Scope）
<!-- forgeloop:anchor initiative/non-goals -->
### 2.3 非目标（Non-Goals）
<!-- forgeloop:anchor initiative/success-criteria -->
### 2.4 成功标准（Success Criteria）

<!-- forgeloop:anchor milestone-master-table -->
## 3. Milestone 总表（Milestone Master Table）
<!-- forgeloop:anchor milestone-master-table/milestone-list -->
### 3.1 Milestone 列表（Milestone List）
<!-- forgeloop:anchor milestone-master-table/milestone-dependencies -->
### 3.2 Milestone 依赖（Milestone Dependencies）
<!-- forgeloop:anchor milestone-master-table/milestone-acceptance -->
### 3.3 Milestone 验收（Milestone Acceptance）
<!-- forgeloop:anchor milestone-master-table/milestone-reference-assignment -->
### 3.4 Milestone 法定引用指派（Milestone Reference Assignment）

<!-- forgeloop:anchor task-ledger -->
## 4. Task 账本（Task Ledger）
<!-- forgeloop:anchor task-ledger/task-list -->
### 4.1 Task 列表（Task List）
<!-- forgeloop:anchor task-ledger/task-definitions -->
### 4.2 Task 定义（Task Definitions）

<!-- forgeloop:anchor branch-pr-integration-path -->
## 5. 分支与 PR 集成路径（Branch & PR Integration Path）
<!-- forgeloop:anchor branch-pr-integration-path/default-integration-model -->
### 5.1 默认集成模型（Default Integration Model）
<!-- forgeloop:anchor branch-pr-integration-path/branch-plan -->
### 5.2 分支计划（Branch Plan）
<!-- forgeloop:anchor branch-pr-integration-path/pr-plan -->
### 5.3 PR 计划（PR Plan）
<!-- forgeloop:anchor branch-pr-integration-path/pr-dependency-order -->
### 5.4 PR 依赖顺序（PR Dependency Order）

<!-- forgeloop:anchor acceptance-matrix -->
## 6. 验收矩阵（Acceptance Matrix）
<!-- forgeloop:anchor acceptance-matrix/task-acceptance-index -->
### 6.1 Task 验收索引（Task Acceptance Index）
<!-- forgeloop:anchor acceptance-matrix/milestone-acceptance-index -->
### 6.2 Milestone 验收索引（Milestone Acceptance Index）
<!-- forgeloop:anchor acceptance-matrix/initiative-acceptance-index -->
### 6.3 Initiative 验收索引（Initiative Acceptance Index）
<!-- forgeloop:anchor acceptance-matrix/evidence-entrypoints -->
### 6.4 证据入口（Evidence Entrypoints）

<!-- forgeloop:anchor global-residual-risks-and-follow-ups -->
## 7. 全局残余风险与后续事项（Global Residual Risks & Follow-Ups）
<!-- forgeloop:anchor global-residual-risks-and-follow-ups/global-residual-risks -->
### 7.1 全局残余风险（Global Residual Risks）
<!-- forgeloop:anchor global-residual-risks-and-follow-ups/follow-ups -->
### 7.2 后续事项（Follow-Ups）
```

<!-- forgeloop:anchor text-anchor-requirement -->
## 稳定锚点要求（Text Anchor Requirement）

下游读取不得依赖标题文本、行号或目录结构。本文所有一级标题，以及所有会被下游直接引用的二级标题，都必须使用固定语义 selector 的文本锚点。

合法写法如下：

```text
<!-- forgeloop:anchor input-baseline-and-sealed-decisions -->
```

命名法如下：

- 一级标题：使用英文语义名，例如 `input-baseline-and-sealed-decisions`、`task-ledger`、`acceptance-matrix`
- 二级标题：使用 `父级/子级` 形式，例如 `input-baseline-and-sealed-decisions/execution-boundary`、`acceptance-matrix/evidence-entrypoints`
- selector 只允许 `[a-z0-9._/-]`
- 同一模板的 selector 必须跨 Initiative 保持同名；`planner` 不得按个人习惯改名

锚点本身属于正式合同，不是排版装饰。

<!-- forgeloop:anchor section-contracts -->
## 分节合同

> 本文凡标注为“唯一权威区块”的小节，其他小节只能引用，不得重裁决；若需概括，只能做索引，不得改写边界。

<!-- forgeloop:anchor input-baseline-and-sealed-decisions -->
### 1. 前置输入与决策基线（Input Baseline And Sealed Decisions）

- `1.1 需求摘要（Requirement Summary）`：说明这张执行地图所满足的最小需求摘要
- `1.2 设计引用（Design Refs）`：指向这份文档继承的 sealed `Design Doc` 或权威设计区块
- `1.3 差距分析引用（Gap Analysis Refs, if applicable）`：当 sealed `Design Doc` 写明 `Gap Analysis Requirement: required` 时，指向 sealed `Gap Analysis Doc`；否则标记为 `N/A`
- `1.4 已封板决策（Sealed Decisions）`：只概括那些已经 sealed、并且实质影响执行地图的上游决策
- `1.5 执行边界（Execution Boundary）`：这是说明当前 `Total Task Doc` 承载什么、不承载什么的唯一权威区块
- `1.6 Initiative 法定引用指派（Initiative Reference Assignment）`：这是下游使用的 Initiative 层法定参考入口的唯一权威区块
- `1.6 Initiative 法定引用指派（Initiative Reference Assignment）` 中的 repo-local durable refs 必须使用 repo-root-relative path；这同样适用于 `.forgeloop/` 下的 runtime control-plane refs
- 对于 repo-local Initiative，`1.6` 的唯一法定控制面根目录应为与本 `Total Task Doc` 同目录的 sibling `.forgeloop/`；应直接填写：
  - `global_state_doc_ref = <initiative_dir>/.forgeloop/global-state.md`
  - `task_review_rolling_doc_root_ref = <initiative_dir>/.forgeloop/task-review/`
  - `milestone_review_rolling_doc_root_ref = <initiative_dir>/.forgeloop/milestone-review/`
  - `initiative_review_rolling_doc_ref = <initiative_dir>/.forgeloop/initiative-review.md`
- 不要在 `1.6` 中写当前 workspace 绝对路径、worktree 绝对路径或 shell-cwd-relative path；如果下游执行时需要绝对路径，应在 active workspace 已绑定后从同一个 repo-root-relative ref materialize
- 这一节要证明执行地图继承的是 sealed 上游真值，而不是本地临时即兴推导

<!-- forgeloop:anchor initiative -->
### 2. Initiative 总览（Initiative）

- `2.1 背景（Background）`：只写执行所需的最小项目背景
- `2.2 范围（Scope）`：定义 Initiative 层面的执行边界
- `2.3 非目标（Non-Goals）`：定义这个 Initiative 以后不得悄悄吞进来的内容
- `2.4 成功标准（Success Criteria）`：定义 Initiative 层面的成功与交付标准
- 本节保持轻薄；不要在这里重述设计长文

<!-- forgeloop:anchor milestone-master-table -->
### 3. Milestone 总表（Milestone Master Table）

- `3.1 Milestone 列表（Milestone List）`：列出整个 Initiative 的全部 Milestone，而不是只写当前 frontier
- `3.2 Milestone 依赖（Milestone Dependencies）`：定义 Milestone 之间的串行、并行与收敛关系
- `3.3 Milestone 验收（Milestone Acceptance）`：定义每个 Milestone 的验收线
- `3.4 Milestone 法定引用指派（Milestone Reference Assignment）`：这是每个 Milestone 法定参考入口的唯一权威区块
- `3.4 Milestone 法定引用指派（Milestone Reference Assignment）` 中的 repo-local refs 也必须保持 repo-root-relative durable form；不要把某个主工作区或旧 worktree 的绝对路径写成法定真值
- `3.4` 中的 Milestone-level review refs 也必须落在同一个 Initiative-local `.forgeloop/` 根下，而不是为同一 Initiative 再开第二个 control-plane 根目录
- `Milestone List` 中的 `Planned PR Model` 默认应为 `Single PR`；只有当某个 Milestone 必须保持为单一状态边界、且无法合理切成新 Milestone 时，才使用 `多 PR 例外（Multi-PR Exception）`

<!-- forgeloop:anchor task-ledger -->
### 4. Task 账本（Task Ledger）

- `4.1 Task 列表（Task List）`：列出所有 Task，并写出稳定的 `Task Key`、所属 Milestone、摘要与依赖
- `4.2 Task 定义（Task Definitions）`：这是 Task 层字段定义的唯一权威区块
- `4.1` 与 `4.2` 必须通过 `Task Key` 一一对应：每个 Task 行都必须有且只有一个匹配定义，`4.2` 中也不得出现孤儿 Task 区块
- 每个 Task 定义至少必须包含：
  - `任务键（Task Key）`
  - `设计引用（Design Refs）`
  - `差距引用（Gap Refs）`
  - `规范引用（Spec Refs）`
  - `输入（Input）`
  - `动作（Action）`
  - `输出（Output）`
  - `非目标（Non-Goals）`
  - `依赖（Dependencies）`
  - `验收（Acceptance）`
  - `Task 局部风险 / 备注（Task-local Risks / Notes）`
- `Refs` 是必填字段，不是装饰
- repo-local `Design Refs`、`Gap Refs`、`Spec Refs` 应保持 repo-root-relative durable form；不要把 workspace-specific absolute path 当成法定 ref
- `Action` 应说明“改什么”，而不是把实现步骤按行教程式展开
- 下游 `coder` 不应该为了重建基本 Task 边界而被迫重新通读整份文档

<!-- forgeloop:anchor branch-pr-integration-path -->
### 5. 分支与 PR 集成路径（Branch & PR Integration Path）

- `5.1 默认集成模型（Default Integration Model）`：这是默认 `one Milestone -> one PR` 规则及其 `Multi-PR Exception` 的唯一权威区块
- `5.2 分支计划（Branch Plan）`：以 planning 层粒度定义计划中的分支模型与命名方式
- `5.3 PR 计划（PR Plan）`：定义计划中的 PR 对象、覆盖范围与验收清单
- `5.4 PR 依赖顺序（PR Dependency Order）`：定义 PR 之间的串行、并行与收敛顺序
- 分支与 PR 规划必须服务于 Milestone 与 Task 的切法，而不能反过来取代它们

<!-- forgeloop:anchor acceptance-matrix -->
### 6. 验收矩阵（Acceptance Matrix）

> 第 6 节只做验收与证据索引，不重定义验收线；权威分别在 `2.4`、`3.3`、`4.2` 与 `6.4`。

- `6.1 Task 验收索引（Task Acceptance Index）`：索引 Task 验收权威区块与首个可审查实物；优先指向可直接审查的 evidence，而不是说明性散文
- `6.2 Milestone 验收索引（Milestone Acceptance Index）`：索引 Milestone 验收权威区块与首个可审查实物；优先指向可直接审查的 evidence，而不是说明性散文
- `6.3 Initiative 验收索引（Initiative Acceptance Index）`：索引 Initiative 验收权威区块与首个可审查实物；优先指向可直接审查的 evidence，而不是说明性散文
- `6.4 证据入口（Evidence Entrypoints）`：这是下游验证与审查应当优先查看哪些证据入口的唯一权威区块；至少要覆盖 `primary run summary`、`auxiliary runtime summary`、`per-case evidence`、`export output`、`owning code surface`、`owning doc surface` 这六类，若某类不适用必须明确写 `N/A` 与理由
- 这个矩阵是控制面索引，不是散文式复述

<!-- forgeloop:anchor global-residual-risks-and-follow-ups -->
### 7. 全局残余风险与后续事项（Global Residual Risks & Follow-Ups）

- `7.1 全局残余风险（Global Residual Risks）`：只记录那些已知、可解释、可追踪、并且在 sealed 后本层允许保留的残余风险
- `7.2 后续事项（Follow-Ups）`：记录在不阻塞当前执行地图的前提下，被有意延后的后续工作
- 不要在这里隐藏未解决的设计或 gap 决策

<!-- forgeloop:anchor writing-rules -->
## 写作规则

- 为下游 `coder` 与 `reviewer` 的可执行性而写，不为取悦人类读者而写
- 使用固定字段、强索引、弱叙事
- 在保持轻薄的同时，不能薄到让 `total_task_doc_reviewer` 无法在本层单独判断执行地图
- 先建立静态执行对象：`Initiative -> Milestone -> Task`；然后再定义依赖与 PR 集成结构
- 如果多切一个 Milestone 能形成更干净的状态边界，应优先多 Milestone，而不是多 PR
- 每条边界、验收规则与法定引用指派都只保留一个真理源；如果另一个区块才是权威来源，就明确引用，不要在别处重新裁决
- 验收真理必须保持单一来源：`2.4 成功标准（Success Criteria）` 管 Initiative 成功，`3.3 Milestone 验收（Milestone Acceptance）` 管 Milestone 验收，`4.2 Task 定义（Task Definitions）` 管 Task 验收；`6` 只能索引这些区块并指向证据
- 把 `1.5 执行边界（Execution Boundary）`、`1.6 Initiative 法定引用指派（Initiative Reference Assignment）`、`3.4 Milestone 法定引用指派（Milestone Reference Assignment）`、`4.2 Task 定义（Task Definitions）`、`5.1 默认集成模型（Default Integration Model）` 与 `6.4 证据入口（Evidence Entrypoints）` 视为本文档的结构核心，不能退化成模糊散文
- repo-local formal refs 只保留一种 durable path semantics：repo-root-relative；如果为了人类阅读额外提供 markdown link 或解释，那也不能让 workspace-specific absolute path 成为唯一法定值
- 所谓完全展开，指所有对象、依赖、验收线与集成路径都已明确，而不是堆砌教程式实现细节
- 任何未决裁决都不得进入 `Total Task Doc`

<!-- forgeloop:anchor prohibited-content -->
## 禁止内容

不要把以下内容写进 `Total Task Doc`：

- 被重新打开的设计争论
- 当前态迁移分析
- 未决问题或 TODO 式裁决占位
- 实现教程细节
- reviewer verdict 原文
- runtime 进度日志
- 用 PR 或分支结构掩盖过厚 Milestone 的写法
- 实际上属于 blocker 级未决问题、却伪装成 residual risk 的表述

这些内容应分别放在 `Design Doc`、`Gap Analysis Doc`、planning rolling doc、runtime control docs，或更上层裁决里。

<!-- forgeloop:anchor review-ready-standard -->
## Review-Ready 标准

只有满足以下条件，这份文档才算 review-ready：

- 所有要求的二级标题都存在，或者以有效理由明确标记为 `N/A`
- 上游 planning 引用明确
- `1.3 差距分析引用（Gap Analysis Refs）` 与 sealed `Design Doc` 中的 `Gap Analysis Requirement` 保持一致
- `1.5 执行边界（Execution Boundary）` 明确
- 所有 repo-local formal refs 都使用 repo-root-relative durable value，而不是当前 workspace 或某个 worktree 的绝对路径
- Initiative 成功标准明确
- 完整的 Milestone 结构与依赖明确
- Initiative 与 Milestone 的法定引用指派明确
- Task 账本已完全展开，`4.1` 中的每个 `Task Key` 在 `4.2` 中都恰好有一个匹配定义，且不存在孤儿 Task 定义
- 默认集成模型及任何 `Multi-PR Exception` 的使用都明确
- 验收矩阵与 `6.4` 中的权威证据入口明确
- `6.1`、`6.2`、`6.3` 都能指向首个可审查实物，而不是只回指说明文档
- `6.4` 已覆盖该节定义的 reviewer-first 六类证据入口，或对不适用项给出合法 `N/A`
- `6` 不得重新定义已经由 `2.4`、`3.3` 与 `4.2` 拥有的验收线
- 没有把未解决的设计或 gap 问题藏到下游去
- 只有当 rolling doc 同 round 的最新 `planner_update` 使用 `next_action=request_reviewer_handoff`，并且存在匹配的当前 `total_task_doc_ref` handoff block 时，reviewer dispatch 才正式成立；`review-ready` 本身只说明文档已达到 handoff 条件

<!-- forgeloop:anchor seal-standard -->
## Seal 标准

只有满足以下条件，这份文档才可以 sealed：

- review-ready 条件已经满足
- `total_task_doc_reviewer` 能在不重建隐藏意图的前提下完成判断
- 下游 `coder` 能据此行动，而无需重新打开上游设计裁决
- runtime reviewers 能直接从文档中定位法定引用、对象边界、验收线与证据入口
- 这份文档仍然是一张轻薄的执行控制面地图，而不是一篇影子设计长文
- 如果还有未解决问题，它们也必须是真正的 residual，而不是 blocker
