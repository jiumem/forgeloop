# Anchor-Sliced Dispatch Optimization 差距分析文档（Gap Analysis Doc）

<!-- forgeloop:anchor document-card -->
## 1. 文档卡片（Document Card）
### 1.1 状态与阶段（Status And Stage）
- 状态：`sealed`
- 阶段：`Gap Analysis Doc`

### 1.2 为什么需要 Gap Analysis（Why Gap Analysis Exists）
- sealed `Design Doc` 已明确 `Gap Analysis Requirement: required`，且目标态不是单点实现缺口，而是 planning/runtime 合同、rolling-doc 读取方式、以及冷启动/恢复边界的收敛工程。
- 当前 repo 已有稳定的 planning/runtime 正式合同，但这些合同仍以整文 refs、整份 rolling docs、和对象级 handoff 为主；目标态要求把它们收缩到稳定 text anchors、最小 dispatch packet、与可重建 derived views。
- 若不先把结构缺口与迁移边界写清，`Total Task Doc` 会被迫同时承担设计补洞、兼容裁决、和执行拆分，违反阶段边界。

### 1.3 主要读者（Primary Readers）
- `gap_reviewer`
- 下游 `plan_reviewer`
- 后续消费 sealed planning truth 的 `run-planning`、`run-initiative`、`rebuild-runtime`、`planner`、`coder`、runtime reviewers

<!-- forgeloop:anchor baseline-and-scope -->
## 2. 基线与范围（Baseline And Scope）
### 2.1 目标态引用（Target-State Reference）
- 权威目标态来源：`docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- 该 sealed `Design Doc` 明确写明 `Gap Analysis Requirement: required`，这是本阶段合法性的唯一路由依据。

### 2.2 纳入范围的目标态切片（Target-State Slice In Scope）
- 为 planning docs、runtime docs、review baselines 建立稳定 machine-readable text anchors。
- 把默认 dispatch 输入面收缩为 `authoritative refs + anchor selectors + 最小必要切片`，并保留 cold start、runtime rebuild、anchor legality failure、anchor conflict 时的整文恢复。
- 让 planning/runtime rolling docs 支持 handoff-scoped、attempt-aware、same-handoff supersede、以及 derived current-effective views。
- 为下游执行锁定三个收敛切片，但不在本文件内展开任务拆分：
  - `M1`：anchor / slicing infrastructure
  - `M2`：runtime dispatch contract shrink
  - `M3`：rolling-doc slimming / derived views / validation / migration

### 2.3 当前态覆盖范围（Current-State Coverage）
- planning 侧：`run-planning`、`planning-loop`、planning stage references、planning rolling-doc contract、当前 Initiative 的 `Planning State Doc` 与 rolling docs。
- runtime 侧：`run-initiative`、`rebuild-runtime`、`task-loop`、`milestone-loop`、`initiative-loop`、`Global State Doc` contract、三层 review rolling-doc contracts、以及当前 repo 内 review baseline docs。
- review / agent 侧：`planner`、`gap-reviewer`、`coder`、runtime reviewers 的 executable manifests 与 repo 内 reference mirrors；manifests 用于确认真实运行合同，mirrors 只用于确认对外说明面是否漂移。
- 不纳入范围：具体 parser 实现、packet builder 代码、真实 runtime trace、或尚未存在的本 Initiative runtime docs。

### 2.4 差距闭合目标（Gap-Closure Goal）
- 在安全撰写 `Total Task Doc` 之前，先把以下条件变成明确权威线：
  - 哪些现有合同已可直接复用，哪些必须为 anchor-addressed dispatch 收缩而改写。
  - `M1`、`M2`、`M3` 的阻塞差距分别是什么，以及它们之间的先后依赖。
  - 旧的整文读取路径如何与新切片路径共存、切换、回滚，而不制造第二真理源。
  - 哪些发现必须回流到 `Design Doc` 或留在 Gap 层处理，不能被 `Total Task Doc` 吞掉。

### 2.5 硬约束（Hard Constraints）
- sealed `Design Doc` 仍是目标态与边界裁决的唯一权威源；本文件只能桥接，不得重写设计裁决。
- `Planning State Doc`、`Global State Doc`、planning/runtime rolling docs 的单一真理源地位不能被 sidecar index、projection cache、或 packet 摘要替代。
- 现有 `round`、`handoff_id`、`review_target_ref`、freshness law、repo-root-relative durable refs、以及 stage/runtime routing vocabulary 不能在下游被隐式重命名。
- gap 阶段必须把 blocker 级差距关在本层；不能把“以后再定义 anchor 合法性 / 迁移规则”伪装成执行细节下放到 `Total Task Doc`。

<!-- forgeloop:anchor gap-verdict-summary -->
## 3. 差距裁决摘要（Gap Verdict Summary）
### 3.1 当前态裁决（Current-State Verdict）
- 当前 repo 已经具备强正式合同骨架：planning / runtime supervisor 分层、state docs 薄控制面、rolling-doc freshness law、以及对象级 handoff 规则都已成文。
- 但这些骨架目前仍以“文档级 ref + 整份 rolling doc / 对象级 review target”为默认读取面；除了 Task 层代码审查锚点外，尚不存在一套跨 planning/runtime 正式文档共享的 text-anchor 地址层，也不存在 current-effective derived view 合同。
- 因此，当前态并不是“缺少流程”，而是“现有流程尚未收缩到目标态要求的 anchor-addressed 最小分发面”。

### 3.2 主要差距（Primary Gaps）
- `M1` 差距：目标态要求稳定 text anchors 覆盖 planning/runtime/contracts，但当前 repo 只有 section 标题、repo-root-relative refs、和 Task commit anchors；没有统一 anchor identity / resolution / legality 合同。
- `M2` 差距：当前 dispatch 入口和 loop 输入仍按文档路径与整份 formal surfaces 绑定；没有“默认最小切片、失败时升级整文”的共享 admission contract。
- `M3` 差距：rolling docs 已有 append-only / freshness 规则，但没有 current-effective derived view、切片物化、validation、或 migration/cutover contract，无法安全瘦身热路径读取。

### 3.3 胜出收敛切法（Winning Convergence Cut）
- 保留现有 planning/runtime 正式合同与 routing vocabulary 作为骨架。
- 先补 `M1` 的地址层与对象覆盖矩阵，再在此基础上收缩 `M2` dispatch packet，最后处理 `M3` derived views、validation、与 migration/cutover。
- 任何阶段只要 anchor legality、dispatch shrink、或 derived-view authority line 无法在不增设第二真理源的前提下成立，就必须在 Gap 层或更上游停住，而不是继续下放到执行计划。

<!-- forgeloop:anchor current-state-snapshot -->
## 4. 当前态快照（Current-State Snapshot）
### 4.1 现有拓扑（Existing Topology）
- planning 侧是两层 supervisor 结构：`run-planning` 负责绑定 Initiative 与 active stage，`planning-loop` 负责单 stage authoring / handoff / review routing。
- planning 正式物包括 stage artifact、`Planning State Doc`、和对应 planning rolling doc；当前 Initiative 已存在 sealed `design.md`、`planning-state.md`、`design-rolling.md`、`gap-rolling.md`、`plan-rolling.md`。
- runtime 侧是 `run-initiative` + `rebuild-runtime` + `task-loop` / `milestone-loop` / `initiative-loop` 的控制面，配套一个 update-only `Global State Doc` 与三层 append-only review rolling docs。
- 运行时对象层已经区分 Task / Milestone / Initiative 三个 review/repair loop，并用对象级 `handoff_id + review_target_ref + round` 维持 freshness。

### 4.2 现有关键表面（Existing Critical Surfaces）
- `run-planning` 与 `planning-loop` 要求 planner / reviewer 读取 stage artifact、`Planning State Doc`、active planning rolling doc、以及 sealed upstream planning artifact；当前合同绑定的是文档 refs，不是 anchor selectors。
- `run-initiative` 的 planning admission 先读 `total_task_doc_ref`，再读 sealed `design_ref`，必要时读 `gap_analysis_ref`；runtime routing 依赖 `Global State Doc` 和当前 rolling doc，而不是派生切片视图。
- `rebuild-runtime` 在冲突或缺失时重读 static truth trio、`Global State Doc`、以及三层 rolling docs 来恢复当前 frontier；当前恢复法没有 anchor-resolution contract，只能靠现有 formal blocks 与对象优先级裁决。
- Task review rolling doc 已有 `anchor_ref` / `fixup_ref`，但它们的对象是 commit handoff，不是 formal markdown text anchors；Milestone/Initiative handoff 也只绑定对象级 `review_target_ref`。
- planning rolling-doc contract 与 runtime rolling-doc contracts都已支持 same-handoff freshness / supersede law，但尚未定义 current-effective derived view 作为正式辅助投影。

### 4.3 现有约束与历史包袱（Existing Constraints And Legacy Burdens）
- repo 当前已经强绑定“薄控制面 + 正式 rolling docs 承载正文事实”的治理模型；任何新方案都必须复用这条骨架，而不能把索引或 packet 变成新的权威层。
- runtime 侧已有 `anchor` 一词用于 Task commit handoff，若引入 text anchors 而不做语义隔离，极易与现有 reviewer/coder vocabulary 混淆。
- `run-initiative` 明确要求 durable refs 保持 repo-root-relative 形式；因此 anchor-addressed 读取不能把绝对路径或 worktree materialization 写回 planning truth。
- 当前 repo 的本 Initiative 尚无 runtime `Global State Doc` 或 review rolling docs 实例，说明 gap 判断当前只能建立在 repo 合同与现有 planning 文档上，而不是运行样本上。

### 4.4 证据边界与未知项（Evidence Boundary And Unknowns）
- 已验证事实：
  - sealed `design.md` 明确要求 `Gap Analysis Requirement: required`，并把 target state 固定为 stable text anchors + minimal dispatch + rebuildable derived views。
  - planning/runtime skills 与 contract refs 已明确当前对象级 handoff、freshness、薄控制面、以及 repo-root-relative ref 语义。
  - `.forgeloop/anchor-sliced-dispatch-optimization/` 目前只有 planning-stage docs，没有 runtime control-plane docs。
- 合理推断：
  - 在没有 text-anchor contract 与 derived-view contract 的情况下，当前 hot path 仍以整文或整份 rolling doc 读取为主，因为 repo 中没有等价的新读取合同可绑定。
- 仍未知：
  - 最终 anchor 语法、命名规则、解析器落点、物化载体。
  - 在真实 runtime trace 下，哪些消费者最需要更细粒度切片；当前 repo 证据只能证明“缺少合同”，不能证明“最终粒度”。

<!-- forgeloop:anchor gap-ledger -->
## 5. 差距账本（Gap Ledger）
### 5.1 边界与职责差距（Boundary And Ownership Gaps）
- 现有 planning/runtime supervisor 已清晰区分 control plane 与 rolling-doc body，但“谁负责 anchor identity / resolution / legality”尚无权威归属；若不先补齐，后续实现会把 parser、dispatcher、reviewer admission 混成一层。
- 现有 Task `anchor_ref` 属于 commit handoff 语义；目标态 text anchor 属于 formal-doc address 语义。两者当前没有命名隔离或 authority line。
- planning docs、runtime control docs、review baselines 各自有合同，但没有统一的“哪些正式表面必须 anchor 化、哪些只消费上游 anchor”覆盖矩阵。

### 5.2 状态与契约差距（State And Contract Gaps）
- 当前 stage/runtime dispatch 合同接受的是 doc refs、rolling-doc paths、和对象级 review target；没有 `doc_ref + anchor selector + slice` 的 canonical packet shape。
- 现有 rolling-doc contracts定义了 freshness law，却没有“current-effective derived view”的构造规则、失效规则、或 authority line。
- cold start / rebuild 只定义了何时整文恢复、如何从 formal blocks 恢复当前 frontier；没有定义 anchor legality failure / conflict 时的升级策略细节。
- reviewer / coder 的当前输入面允许读取必要 formal surfaces，但没有统一限制“默认只读当前 handoff 对应切片，何时才允许升级整文”。

### 5.3 兼容与迁移差距（Compatibility And Migration Gaps）
- 旧路径默认是整文 refs；新路径要求 anchor-addressed minimal packet。二者之间缺少显式 coexistence law，无法判断哪些消费者必须先双读、哪些可以直接切换。
- runtime / planning rolling docs 目前没有 slimming 或 derived-view 物化表面；如果直接让下游只看临时切片，会先打破恢复路径，再谈不上迁移。
- 现有 repo 示例与 reviewer contracts 都围绕对象级 `review_target_ref` 编写；若新 anchor 地址层改变这些字段语义，就会破坏现有 freshness / supersede law。
- 本 Initiative 当前没有 runtime doc 样本，意味着 migration planning 必须先定义验证法，再允许下游实施；否则只能靠实现时猜测。

### 5.4 不得泄漏到下游的阻塞差距（Blocking Gaps That Must Not Leak Downstream）
- `B1 / M1`：必须先固定 anchor coverage matrix 与 authority line。
  - 需要回答哪些正式文档表面必须暴露稳定 text anchors，哪些只需消费上游 anchor，以及如何避免与 Task commit anchors 混义。
  - 若这点不先定，`Total Task Doc` 无法合法拆分 parser、builder、validator、consumer 的执行边界。
- `B2 / M2`：必须先固定 dispatch contract shrink 的 admission law。
  - 需要回答 planner、runtime supervisor、coder、reviewer 默认拿到的最小输入面是什么，以及在何种明确条件下升级为整文读取。
  - 若这点不先定，下游执行会把“最小 packet”降格成不稳定 prompt 摘要。
- `B3 / M3`：必须先固定 rolling-doc slimming / derived view / validation / migration 的 authority line。
  - 需要回答 current-effective view 如何从正式 rolling docs 推导、何时失效、如何验证、如何与旧整文读取共存、以及迁移失败如何回滚。
  - 若这点不先定，`Total Task Doc` 会被迫同时承担新投影层设计与执行计划，造成阶段泄漏。

<!-- forgeloop:anchor convergence-strategy -->
## 6. 收敛策略（Convergence Strategy）
### 6.1 桥接形态（Bridge Shape）
- 桥接不是重做 planning/runtime 骨架，而是在现有骨架上叠加一个受限地址层与可失效投影层。
- 收敛顺序固定为：
  - 先做 `M1`：确定 anchor identity、resolution、coverage、legality。
  - 再做 `M2`：把 planning/runtime dispatch contract 从整文默认切到 anchor-addressed minimal packet 默认。
  - 最后做 `M3`：在不改变权威源的前提下，加入 rolling-doc derived views、validation、slimming、与 migration/cutover。
- 该顺序是结构依赖，不是任务分解：`M2` 依赖 `M1` 的地址层；`M3` 依赖 `M1` 与 `M2` 的合法目标面。

### 6.2 切换与共存规则（Cutover And Coexistence Rules）
- 在 `M1` 未完成前，旧的整文 refs 与现有 rolling-doc 读取仍是唯一合法默认路径；不得提前让下游依赖未定型 anchor 语法。
- `M2` 切换时，新 packet 只能作为“显式 authoritative refs + anchor selectors + 必要切片”的收缩层；若 selector 缺失、冲突、过期、或 legality 无法证明，必须立即升级为整文读取，而不是猜测性继续。
- `M3` 上线前，derived current-effective views 只能是可丢弃投影；不得写回 `Planning State Doc`、`Global State Doc`、或替代 rolling docs 成为 durable truth。
- 共存期内，旧字段 `review_target_ref`、`handoff_id`、`round`、`next_action` 的 freshness law 不变；若新设计需要改变这些字段语义，应视为 Design reopen，而不是 Gap 内兼容。

### 6.3 回滚与安全红线（Rollback And Safety Lines）
- 任一新切片路径若不能从正式文档重建，必须立即回滚到整文路径，不得保留半权威缓存。
- 任一 anchor 解析若出现重复、漂移、失配、或 consumer 之间解释不一致，必须停止最小分发并进入整文恢复或显式 blocker。
- 回滚后仍必须保持现有 planning/runtime control plane 可恢复：`Planning State Doc`、`Global State Doc`、和 rolling docs 的合法块形态不能被新层污染。
- 不允许通过在 state docs 中补充摘要字段、临时索引字段、或 materialized absolute paths 来“快速修复”新路径。

### 6.4 下游绑定影响（Downstream Binding Effects）
- `Total Task Doc` 必须把 `M1`、`M2`、`M3` 当作执行切片边界，但它只能展开执行结构，不能重新裁决这些切片的 authority line。
- 下游 coding/routing 工作必须把“整文恢复是显式 fallback，不是默认路径”作为绑定事实，同时也必须把“fallback 永远合法”作为安全事实。
- 任何实现提案若试图把 packet、projection cache、或 slim view 提升为新的 durable source，应直接判定超出本 Gap 文档允许范围。

<!-- forgeloop:anchor correctness-surface -->
## 7. 正确性表面（Correctness Surface）
### 7.1 迁移不变量（Migration Invariants）
- 正式 planning artifacts、state docs、rolling docs 始终是唯一权威源。
- `round`、`handoff_id`、`review_target_ref`、freshness / supersede law 在迁移过程中持续有效。
- cold start、runtime rebuild、以及 planning/runtime supervisor recovery 在任何阶段都必须能退回整文恢复。
- repo-root-relative durable refs 持续保留；anchor-addressed 读取只能增加地址层，不能替换 durable ref 语义。

### 7.2 数据与兼容红线（Data And Compatibility Red Lines）
- 不得把 text anchors 与 Task commit anchors 混成同一法律对象；若共享术语不可避免，必须在权威合同内明确 namespace 与消费边界。
- 不得改变 `review_target_ref`、`handoff_id`、`next_action` 的既有 freshness 语义来偷渡新切片机制。
- 不得让 current-effective / slim / derived 视图成为 `Planning State Doc`、`Global State Doc`、或 rolling docs 之外的第二真理源。
- 不得要求 cold start 或 rebuild 依赖先前缓存、临时文件、或不可重建 projection 才能恢复。

### 7.3 允许的实现变体（Allowed Implementation Variation）
- anchor 的具体 markdown 语法、命名细则、解析器落点、以及 slice materialization 载体可以在下游执行中选择。
- legality check 可以落在 parser、dispatcher、reviewer admission、或 projection builder，只要失败后会回到本文件定义的安全边界。
- derived views 可以按 planning 或 runtime 消费面采用不同粒度，只要 authority line 与失效规则一致。

### 7.4 回流触发器（Reroute Triggers）
- 若 `M1` 发现稳定 text anchors 不能在不改动 sealed 设计不变量的前提下覆盖必要正式表面，必须回流到 `Design Doc`。
- 若 `M2` 发现最小 dispatch packet 只有通过新增 durable state、改写 routing vocabulary、或修改 freshness law 才能成立，必须回流到 `Design Doc`。
- 若 `M3` 发现 derived views 无法保持“可重建、可失效、非权威”的三条件，则不得继续下游执行；应在 Gap 层修复或建议 reopen 到 Design。
- 若下游只能靠未证实的 runtime trace 假设来决定切片粒度或切换顺序，应先回到 Gap 层补足验证/迁移边界，而不是直接进入执行计划。

<!-- forgeloop:anchor residual-risks -->
## 8. 残余风险与后续事项（Residual Risks And Follow-Ups）
### 8.1 可接受残余风险（Accepted Residual Risks）
- 由于当前 repo 缺少本 Initiative 的 runtime doc 样本，`Total Task Doc` 仍需为验证矩阵补足实例化检查点；本文件只证明合同级缺口，不证明最终实现粒度。
- `M1` 初版 anchor coverage 可能先偏粗，再经实现验证细化；只要不突破本文件的 authority line，这属于可接受残余。
- 共存期内部分消费者仍会暂时走整文 fallback，这与目标态一致，只要 fallback 是显式合法而不是默认偷懒路径。

### 8.2 延后清理项（Deferred Cleanups）
- 统一 reference mirrors 与 executable manifests 中关于 anchor-addressed dispatch 的措辞，使 agent mirrors 更接近最终 runtime 合同。
- 为 planning/runtime 参考文档补充示例，展示 text anchors、minimal packet、以及 derived current-effective view 的推荐样式。
- 在未来执行阶段形成真实 runtime docs 后，再校准是否需要更细的 consumer-specific slice granularity。
