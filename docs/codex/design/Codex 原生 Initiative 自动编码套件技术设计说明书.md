# Codex 原生 Initiative 自动编码套件技术设计说明书

## 封面信息卡

| 项目 | 内容 |
| --- | --- |
| 文档名称 | Codex 原生 Initiative 自动编码套件技术设计说明书 |
| 文档层级 | Codex 落地方案层 / 技术设计层 |
| 文档定位 | 对总体机制与落地方案进行工程化展开的技术定义文档 |
| 适用范围 | 需要实现数据模型、状态机、工件合同、运行时算法与接口边界的仓库 |
| 非目标 | 不重述总体机制映射；不替代专项作战计划；不展开逐 prompt 文案 |

## 0. 文档定位

本文档只回答一个问题：

> 这套 Codex 原生 Initiative 自动编码套件，在工程层面究竟由哪些模型、状态、工件、接口和运行规则组成。

本文档直接服务于：

- schema 与模型定义
- 状态机实现
- skill / agent / script 接口设计
- mock、合同测试与实现代码

本文档默认承接上一层文档中的机制裁决，不再重复证明：

- 为什么 Initiative 是主入口
- 为什么 Task 只作为内部原子
- 为什么内部检查不是 formal R1
- 为什么主线程不能空壳化

本文档采用以下写作约束：

- 只写可实现、可测试、可裁决的技术定义
- 优先复用仓库已有四个核心模型的业务真值地位
- 在此基础上增加 Initiative 级运行时模型，而不是另造平行真值体系
- 明确区分 canonical source 与 rebuildable runtime cache

## 1. 技术目标与设计边界

### 1.1 技术目标

本设计的技术目标固定为五项：

第一，建立一套 Initiative-first 的正式对象层。  
系统必须同时表达 `initiative_plan`、`initiative_state`、`milestone_state` 与 `task_state`，并允许 controller 在不丢失上位法位的前提下做调度。

第二，保留旧四模型的业务真值角色。  
`task_packet`、`coder_result`、`review_result`、`task_state` 仍是 Task 执行闭环里的结构化核心，不因新增 Initiative Runtime 而失效。

第三，把 Task 内部闭环压成显式子状态机。  
Task loop 必须明确区分 `implement -> spec check -> quality check -> READY_FOR_ANCHOR -> G1 -> R1`，而不是把这些动作混进自然语言会话。

第四，保证运行态可重建。  
任何本地缓存都只能是派生状态。删除 `.initiative-runtime/` 后，系统仍应能从总任务文档、Git/PR/CI 证据和正式 gate/review 产物恢复主状态。

第五，保证接口边界清晰。  
skills、custom agents、repo 脚本、App / CLI / GitHub / Automations 都要有明确职责，避免出现“谁都能推进、谁都能裁决”的混乱控制面。

### 1.2 技术非目标

本文档明确不承担以下目标：

- 不把 Codex 原生机制再次抽象成新的上位宪法
- 不把 Task 内部检查提升为第四层 formal review
- 不设计多 milestone 并发写入调度器
- 不把 Automations 变成 blocking 主链的正式执行面
- 不在 v1 引入分布式 worker、队列或常驻服务
- 不把 PR 评论、JSONL 日志或 CLI 自然语言输出视为业务真值

### 1.3 与上位宪法、总体机制文档的关系

三层文档关系固定如下：

- 上位宪法层定义对象法位、角色边界、Gate / Review 法律
- 第一篇总体机制文档定义 Codex 原生机制映射、总体流程与关键约束
- 本文档定义可直接落成代码与测试的模型、状态、工件、算法与接口

因此，凡属“为什么这样设计”的问题，以第一篇为准；凡属“具体要落成什么字段、什么状态、什么算法”的问题，以本文档为准。

## 2. Canonical Sources 与 Runtime Cache

### 2.1 规划真理源

规划真理源只有一类：

- Initiative 总任务文档及其内嵌或并列的结构化 machine block

其职责是表达静态总图，包括：

- initiative 元信息
- milestone 编排
- workstream 责任划分
- task 定义
- reference assignment
- success criteria
- formal gate 默认命令配置

规划真理源必须满足：

- 可被 preflight 做结构校验
- 可被 parser 无歧义解析成 `initiative_plan`
- 不能依赖运行时状态反向补全关键字段

### 2.2 工程真理源

工程真理源由以下对象共同构成：

- Git 工作树与索引
- milestone 分支 / worktree
- 结构化 commit
- PR 及其关联 diff
- 仓库中的正式代码、测试、文档与配置

其中最关键的工程边界是三条：

- Task 的正式工程收口锚点是 `anchor(<milestone>/<task>): ...`
- Task 内修补可用 `fixup(<milestone>/<task>): ...`
- 回退可用 `revert(<milestone>/<task>): ...`

Task 是否真正完成，不能只看 agent 的自然语言说明，必须能在工程真理源中找到对应代码与 anchor 证据。

### 2.3 验证与审查真理源

验证与审查真理源分两层：

- gate 真理源：按既定 profile 执行出的结构化 `gate_result`
- formal review 真理源：按既定 review profile 产出的结构化 `review_result`

以下对象只作为辅助说明，不直接充当业务真值：

- markdown 总结
- PR 评论中的自由文本
- App review pane 的非结构化说明
- 临时分析日志

这些对象可以被保留为 `review_report` 或附属 evidence，但 controller 的裁决只能依赖结构化结果。

### 2.4 Runtime Cache 与可重建原则

`.initiative-runtime/` 的法位固定为：

- 派生状态缓存
- packet / observation / decision / draft 的工作目录
- 对 gate/review 结构化结果的本地副本索引

它不是正式真理源。其删除与重建必须满足：

- `state.json` 可以从 `initiative_plan + Git + formal artifacts` 重建
- `task_state` 的 formal status 可以从 anchor、G1/R1 结果回放
- `milestone_state` 与 `initiative_state` 可以从 task / milestone formal artifacts 重新推导

允许保存在 `.initiative-runtime/` 中但必须视为派生副本的对象包括：

- `state.json`
- packets
- observations
- decisions
- drafts
- local copy 的 gate / review 结果

## 3. 数据模型总览

本设计采用“两层对象模型”：

- 静态规划层：描述做什么、怎么拆、依据什么执行
- 运行收口层：描述当前推进到哪里、最近产生了哪些结构化工件、下一步能做什么

其中旧四模型仍保留在 Task 执行真值层，新引入的 Initiative Runtime 模型负责把多个 Task 组织成可调度的总系统。

### 3.1 静态规划模型

#### `initiative_plan`

`initiative_plan` 是 Initiative 级静态总图，是 parser 输出的主模型。最少必须包含以下语义区块：

- 身份区：`key`、`title`
- 需求摘要区：`requirement_summary.problem`、`requirement_summary.goal`
- 法源区：`design_refs`、`gap_refs`、`sealed_decisions`
- 边界区：`execution_boundary`、`scope`、`non_goals`
- 成功标准区：`success_criteria`
- 结构区：`milestones`、`workstreams`、`tasks`、`pr_plan`
- 收口区：`initiative_reference_assignment`、`g3_commands`
- 风险区：`global_residual_risks`、`follow_ups`

合同要求：

- `initiative_plan` 必须足够让 controller 在不读完整会话历史的情况下重建运行主图
- 任何 Task 关键边界都必须能追溯到 `initiative_plan`
- parser 失败或关键引用失效时，整个 Initiative 进入 `PLANNING_BLOCKED`

#### `milestone_plan`

`milestone_plan` 表达单个 Milestone 的阶段目标与正式收口边界，最少包含：

- `key`
- `goal`
- `depends_on`
- `planned_pr_model`
- `acceptance`
- `reference_assignment`

技术意义：

- 它决定 frontier 的合法顺序
- 它决定 G2 / R2 的收口参照
- 它决定 PR 与 milestone 的对应关系

#### `milestone_reference_assignment`

这是 `milestone_plan.reference_assignment` 的正式语义展开，不单独作为独立顶层对象存储，但在技术上应视为一个明确合同：

- 该 Milestone 的主要引用文档或章节
- 该 Milestone 的目标边界
- 该 Milestone 的验收依据

controller 构建 R2 packet 时，必须把它当作 Milestone formal review 的主法源，而不是只看 task 汇总。

#### `initiative_reference_assignment`

这是 Initiative 交付级 reference assignment 的正式语义展开，最少包括：

- Initiative 交付面向的总设计引用
- 对整体成功标准的汇总引用
- 对 release / rollout candidate 的主要验收依据

它是 G3 / R3 packet 的主法源。

#### `task_definition`

`task_definition` 是由 `initiative_plan.tasks[task_key]` 解析出的静态 Task 定义视图。它不同于 `task_packet`，因为前者是静态规划，后者是执行时裁剪后的局部包。

`task_definition` 至少包含以下字段语义：

- 身份区：`key`、`milestone`、`workstream`
- 任务摘要区：`summary`
- 法源区：`design_refs`、`gap_refs`、`spec_refs`
- 输入输出区：`input`、`action`、`output`
- 边界区：`non_goals`
- 依赖区：`dependencies`
- 局部完成标准区：`acceptance`
- 风险区：`local_risks`
- 执行策略区：`recommended_executor`、`execution_mode`
- Gate 区：`g1_commands`

合同要求：

- `task_definition` 必须足够被 controller 裁成不依赖全文漫游的 `task_packet`
- 不能把必须完成项和必须不做项隐藏在散文段落里
- `dependencies` 只能指向同一 Initiative 中的其他 task key

### 3.2 运行态模型

#### `initiative_state`

`initiative_state` 是 Initiative 运行总状态，是 controller 的主工作台。推荐字段语义如下：

- 身份区：`initiative_key`、`title`
- 正式状态区：`status`
- frontier 区：`current_frontier`
- 索引区：`task_states`、`milestone_states`
- Formal 收口引用区：`latest_g3_ref`、`latest_r3_ref`
- 运行说明区：`notes`

推荐状态枚举：

- `PLANNING_BLOCKED`
- `READY`
- `ACTIVE`
- `WAITING_R2`
- `WAITING_ESCALATION`
- `WAITING_R3`
- `DONE`
- `ABORTED`

#### `milestone_state`

`milestone_state` 负责承接单个 Milestone 的阶段运行态，最少包含：

- `key`
- `status`
- `task_keys`
- `active_branch_ref`
- `latest_pr_ref`
- `latest_g2_ref`
- `latest_r2_ref`
- `blocked_reason`

推荐状态枚举：

- `NOT_READY`
- `READY`
- `ACTIVE`
- `READY_FOR_PR`
- `IN_G2`
- `IN_R2`
- `MERGED`
- `BLOCKED`
- `DEFERRED`

#### `task_state`

`task_state` 仍保留为四个核心模型之一，但要从旧 task-first 结构扩展到 Initiative Runtime 兼容结构。推荐字段分为两层：

- 正式状态层：Task 在 Initiative 中的正式位置
- 局部循环层：Task loop 在 Task 内部走到哪里

最少字段语义如下：

- 身份区：`task_id`、`initiative_key`、`milestone_key`、`workstream_key`
- 正式状态区：`formal_status`
- 局部循环区：`loop_phase`
- 轮次区：`round_no`、`spec_check_round_no`、`quality_check_round_no`
- 依赖区：`depends_on`
- 工件引用区：
  - `latest_task_packet_ref`
  - `latest_coder_result_ref`
  - `latest_spec_check_ref`
  - `latest_quality_check_ref`
  - `latest_g1_ref`
  - `latest_r1_ref`
  - `last_anchor_commit`
- 运行控制区：`probe_count`、`stall_count`、`blocked_reason`、`pending_escalation`
- 通知区：`pending_notification`

推荐 `formal_status` 枚举：

- `NOT_READY`
- `READY`
- `IN_FLIGHT`
- `READY_FOR_ANCHOR`
- `IN_G1`
- `IN_R1`
- `DONE`
- `BLOCKED`
- `DEFERRED`

#### `task_loop_phase`

`task_loop_phase` 是 `task_state` 的内部子状态机枚举，专门表达 Task 内循环，不可与 formal status 混用。

推荐枚举：

- `IDLE`
- `BUILD_PACKET`
- `IMPLEMENT`
- `SPEC_CHECK`
- `FIX_SPEC`
- `QUALITY_CHECK`
- `FIX_QUALITY`
- `READY_FOR_ANCHOR`
- `WAIT_FORMAL_SEAL`
- `BLOCKED`
- `ESCALATED`

设计约束：

- `loop_phase` 只描述 Task 内局部推进，不表达 Milestone / Initiative 收口
- `formal_status=READY_FOR_ANCHOR` 时，`loop_phase` 必须为 `READY_FOR_ANCHOR`
- `formal_status in {IN_G1, IN_R1}` 时，`loop_phase` 必须为 `WAIT_FORMAL_SEAL`

#### `runtime_fact_state`

`runtime_fact_state` 用于表达局部自动循环依赖的运行事实，而不是正式工程真理。最少应包含：

- `fact_key`
- `task_id`
- `kind`
- `source`
- `freshness`
- `evidence_refs`
- `summary`

推荐 `kind` 包括：

- `TEST_OUTPUT`
- `LINT_OUTPUT`
- `TRACE_LOG`
- `ERROR_REPRO`
- `READONLY_DISCOVERY`

其法位是：

- 可支持局部判断
- 可驱动 `REQUEST_RUNTIME_FACTS`
- 不可单独宣布 Task 完成

### 3.3 执行与审查工件模型

#### `task_packet`

`task_packet` 仍为核心模型之一，承担 controller 裁好的执行边界包。它不等于静态 `task_definition`，因为它还包含执行时上下文。

它至少应包含：

- `initiative_context`
- `milestone_context`
- `task_definition`
- `task_runtime`
- `requested_scope`
- `must_not_do`
- `acceptance`
- `dependency_snapshot`
- `repo_snapshot`
- `required_checks`
- `generated_at`

技术裁决：

- implementer 只能以 `task_packet` 为主输入，不允许反向要求其先自行漫游总任务文档
- `task_packet` 是 Task 内实现与修补的唯一 controller-curated 包

#### `task_check_result`

`task_check_result` 是新增的内部检查模型，明确用于 Task 内部检查，而不是 formal review。

推荐字段：

- `task_id`
- `check_kind`
- `round_no`
- `verdict`
- `findings`
- `blocking_findings`
- `evidence_refs`
- `summary`
- `recommended_fix_scope`

推荐 `check_kind` 枚举：

- `SPEC_COMPLIANCE`
- `CODE_QUALITY`

推荐 `verdict` 枚举：

- `PASS`
- `FAIL`
- `ESCALATE`

技术裁决：

- `task_check_result` 不得直接驱动 Task `DONE`
- `SPEC_COMPLIANCE` 必须先于 `CODE_QUALITY`
- `CODE_QUALITY` 只在 spec pass 后触发

#### `coder_result`

`coder_result` 仍为核心模型之一，记录 implementer 在某一轮客观做了什么，不宣布通过。

保留其五面结构：

- 代码面：`files_changed`
- 法位面：`contracts_addressed`
- 清理面：`cleanups_done`
- 验证面：`check_results`
- 边界面：`out_of_scope_notes`

在 Initiative Runtime 中新增两条使用规则：

- `coder_result` 必须始终能回链到生成它的 `task_packet`
- `coder_result` 只能作为后续 `spec_check_packet` 与 `quality_check_packet` 的输入，不得直接替代 formal review

#### `review_result`

`review_result` 仍为核心模型之一，但在新体系中的法位被明确为：

- formal review 的结构化真值模型
- 默认先用于 `R1`
- 结构应支持未来统一表达 `R2`、`R3`

为兼容现有主线，可采用两阶段策略：

- v1 过渡期：保留现有 task-scoped `review_result` 作为 `R1` 真值，并以 `review_report` 承接 `R2` / `R3`
- 收敛目标：将 `review_result` 抽象为 `profile + object_type + object_key` 的统一 formal review 模型

无论采用哪种迁移路径，硬约束都不变：

- `review_result` 只代表 formal review
- `spec_check_result` 与 `quality_check_result` 不得复用 `review_result` 名义

#### `gate_result`

`gate_result` 是 formal gate 的结构化结果，至少应包含：

- `profile`
- `object_key`
- `passed`
- `commands`
- `summary`

其中 `commands[]` 每项最少包含：

- `command`
- `return_code`
- `stdout_ref | stdout`
- `stderr_ref | stderr`

推荐 `profile`：

- `G1`
- `G2`
- `G3`

#### `review_report`

`review_report` 是供人读、供 PR / App / release panel 展示的渲染结果。它不是 controller 真值，但应稳定映射自 formal review 结构化结果。

推荐字段：

- `profile`
- `object_key`
- `verdict`
- `summary`
- `findings`
- `residual_risks`
- `escalations`
- `evidence`

它可以由 `review_result` 或其它正式 review bundle 正规化生成。

## 4. 状态模型

### 4.1 Initiative 状态枚举与跃迁

`initiative_state.status` 的推荐跃迁如下：

| 当前状态 | 条件 | 下一状态 |
| --- | --- | --- |
| `PLANNING_BLOCKED` | preflight 通过 | `READY` |
| `READY` | 选出 frontier 或 ready task | `ACTIVE` |
| `ACTIVE` | milestone 全部进入待 R2 | `WAITING_R2` |
| `ACTIVE` | 发生跨层升级或用户裁决请求 | `WAITING_ESCALATION` |
| `WAITING_R2` | 当前 frontier 完成 R2 / merge | `ACTIVE` 或 `WAITING_R3` |
| `WAITING_R3` | G3 / R3 clean | `DONE` |
| 任意非终态 | 用户终止 | `ABORTED` |

设计约束：

- `initiative_state` 不得直接跳过 Milestone 层进入 `DONE`
- `WAITING_R3` 只在全部 Milestone 已完成正式阶段收口后成立

### 4.2 Milestone 状态枚举与跃迁

`milestone_state.status` 的推荐跃迁如下：

| 当前状态 | 条件 | 下一状态 |
| --- | --- | --- |
| `NOT_READY` | 前置 Milestone 已完成 | `READY` |
| `READY` | 出现 ready task | `ACTIVE` |
| `ACTIVE` | 所有 task `DONE` | `READY_FOR_PR` |
| `READY_FOR_PR` | 开始执行 G2 | `IN_G2` |
| `IN_G2` | gate pass | `IN_R2` |
| `IN_R2` | review clean / PR merged | `MERGED` |
| 任意非终态 | 阻塞或升级 | `BLOCKED` |

技术约束：

- `READY_FOR_PR` 之前不得启动 R2
- `MERGED` 是 Milestone 正式完成态

### 4.3 Task 状态枚举与跃迁

`task_state.formal_status` 的推荐跃迁如下：

| 当前状态 | 条件 | 下一状态 |
| --- | --- | --- |
| `NOT_READY` | 依赖满足 | `READY` |
| `READY` | controller 启动 task loop | `IN_FLIGHT` |
| `IN_FLIGHT` | 通过局部检查并产出 anchor 候选 | `READY_FOR_ANCHOR` |
| `READY_FOR_ANCHOR` | anchor 已切出 | `IN_G1` |
| `IN_G1` | G1 pass | `IN_R1` |
| `IN_R1` | R1 clean | `DONE` |
| 任意非终态 | 外部阻塞 | `BLOCKED` |
| 任意非终态 | 由规划改动延后 | `DEFERRED` |

技术约束：

- `READY` 与 `IN_FLIGHT` 间只允许 controller 驱动，不允许 reviewer 越权
- `DONE` 必须同时具备 `last_anchor_commit`、`latest_g1_ref`、`latest_r1_ref`

### 4.4 Task Loop 内部子状态机

`task_loop_phase` 的推荐流转如下：

```text
IDLE
  -> BUILD_PACKET
  -> IMPLEMENT
  -> SPEC_CHECK
      -> FIX_SPEC -> IMPLEMENT
      -> QUALITY_CHECK
          -> FIX_QUALITY -> IMPLEMENT
          -> READY_FOR_ANCHOR
              -> WAIT_FORMAL_SEAL
```

异常分支：

- 任一阶段缺关键证据：`REQUEST_RUNTIME_FACTS` 型决策，回到 `IMPLEMENT` 或进入 `ESCALATED`
- 任一阶段发现硬阻塞：进入 `BLOCKED`
- 局部循环振荡或超轮次：进入 `ESCALATED`

### 4.5 Upgrade / Blocked / Deferred 条件

以下情况必须触发升级或阻塞，而不是继续局部自动循环：

- `must_do` 与 `must_not_do` 出现直接冲突
- 关键法源引用失效或过时
- 多轮 spec / quality 检查没有收敛
- 需要修改 Milestone / Initiative 级 sealed decision
- 需要新增超出 `task_definition` 边界的广域改造
- 缺失运行事实且超过最大探针次数

推荐策略：

- 局部证据不足但可补采：`pending_escalation=REQUEST_RUNTIME_FACTS`
- 需要人工决定边界：`pending_escalation=NEEDS_HUMAN_RULING`
- 外部依赖未就绪：`formal_status=BLOCKED`
- 规划层主动后移：`formal_status=DEFERRED`

### 4.6 Formal Seal 条件

正式收口条件固定如下：

Task 收口：

- `task_loop_phase=READY_FOR_ANCHOR`
- 已生成 anchor commit
- G1 通过并落盘 `gate_result`
- R1 通过并落盘 `review_result`

Milestone 收口：

- 该 Milestone 全部 Task 为 `DONE`
- 已生成或更新 PR
- G2 通过
- R2 clean 或残余风险已按法定方式记录

Initiative 收口：

- 全部 Milestone 已 `MERGED`
- G3 通过
- R3 clean 或交付候选已被正式裁决

## 5. Packet 与 Artifact 合同

### 5.1 `task_packet` 合同

`task_packet` 是所有写入型 Task 执行的唯一 controller-curated 输入包。建议采用以下结构：

```json
{
  "initiative": {},
  "milestone": {},
  "task": {},
  "task_runtime": {},
  "requested_scope": [],
  "must_not_do": [],
  "acceptance": [],
  "dependency_snapshot": {},
  "repo": {},
  "required_checks": [],
  "generated_at": ""
}
```

合同要求：

- `requested_scope` 必须是明确待完成项，不得只给宽泛目标
- `must_not_do` 必须显式下发，避免 implementer 自行扩大 scope
- `repo.git_status` 仅作环境说明，不能替代 Git 真理源
- 同一 `round_no` 只能对应一个主 `task_packet`

### 5.2 `spec_check_packet` 合同

`spec_check_packet` 用于 `SPEC_COMPLIANCE` 检查，最少应包含：

- `task_id`
- `round_no`
- `what_was_requested`
- `task_acceptance`
- `must_not_do`
- `coder_claim`
- `files_changed`
- `code_refs`
- `evidence_refs`

技术裁决：

- spec reviewer 必须直接读代码与结构化输入，不得只信 implementer 摘要
- 输出必须规范化为 `task_check_result(kind=SPEC_COMPLIANCE)`

### 5.3 `quality_check_packet` 合同

`quality_check_packet` 用于 `CODE_QUALITY` 检查，最少应包含：

- `task_id`
- `round_no`
- `what_was_implemented`
- `base_sha`
- `head_sha`
- `files_changed`
- `commands_run`
- `known_residual_risks`
- `evidence_refs`

技术裁决：

- `base_sha` / `head_sha` 应明确界定审查差异面
- 若未经过 spec pass，不得生成 quality check packet

### 5.4 `review_packet` 合同

`review_packet` 专用于 formal review。最少应包含：

- `profile`
- `object_type`
- `object_key`
- `reference_assignment`
- `references`
- `evidence`
- `gate_result_ref`
- `candidate_ref`
- `generated_at`

推荐 `object_type`：

- `TASK`
- `MILESTONE`
- `INITIATIVE`

技术裁决：

- R1 packet 默认以 task anchor 与 G1 结果为主要 evidence
- R2 packet 默认以 PR、Milestone reference assignment 与 G2 结果为主要 evidence
- R3 packet 默认以 release / rollout candidate、Initiative reference assignment 与 G3 结果为主要 evidence

### 5.5 report / bundle / runtime facts 合同

各类辅助工件推荐合同如下：

`observation`：

- 表达局部观察结果
- 允许包括 closure signal、entropy signal、required runtime facts
- 不直接决定 formal 通过

`decision`：

- 表达 controller 对 observation 的局部裁决
- 至少包含 `action`、`why`、`next_required_facts`

`runtime_fact`：

- 表达补采得到的运行事实
- 需带 `source`、`freshness`、`evidence_refs`

`bundle`：

- 表达某次 gate / review 聚合的引用和证据清单
- 用于让 reviewer 和后续工具读取，而不充当主真值

### 5.6 结构化 commit / anchor / fixup 合同映射

本系统要求 commit subject 满足结构化前缀：

- `anchor(<milestone>/<task>): <summary>`
- `fixup(<milestone>/<task>): <summary>`
- `revert(<milestone>/<task>): <summary>`

映射关系固定为：

- `anchor` 对应 Task 正式工程锚点
- `fixup` 对应 anchor 前后局部修补
- `revert` 对应正式回退

技术约束：

- 只有 `anchor` 可以驱动 `READY_FOR_ANCHOR -> IN_G1`
- 运行时重建必须优先扫描这些结构化 subject，而不是推测 branch diff

## 6. 核心运行算法

### 6.1 `planning_preflight()`

输入：

- Initiative 文档路径
- repo root

职责：

- 提取 machine block
- 校验关键字段完整性
- 校验引用文件存在性
- 校验 milestone / task dependency 图合法性

输出：

- `passed`
- `errors[]`
- `initiative_doc`

失败后行为：

- 不进入任何运行主链
- Initiative 状态置为 `PLANNING_BLOCKED`

### 6.2 `rebuild_initiative_state()`

输入：

- `initiative_plan`
- repo root

职责：

- 扫描 Git anchors
- 扫描 formal gate / review 结构化结果
- 计算 task formal status
- 汇总 milestone / initiative status
- 生成新的 `initiative_state`

技术裁决：

- `state.json` 只可作为加速索引，不可覆盖重建结果
- 重建优先级应为 `formal artifacts > Git anchors > cache hints`

### 6.3 `select_frontier()`

职责：

- 在有序 milestone 列表中选择第一个未收口、依赖已满足的 frontier

选择原则：

- 优先级按 `initiative_plan.milestones` 顺序
- `BLOCKED` frontier 不自动跳过，除非已有正式升级裁决
- 不允许同时把两个写入型 milestone 设为活动 frontier

### 6.4 `select_ready_tasks()`

职责：

- 在当前 frontier 内选择 ready task 集合

选择规则：

- `formal_status=READY`
- 依赖 task 已 `DONE`
- 同一 Milestone 默认最多一个写入型 task
- read-only task 可在不污染工作树的前提下并行

输出：

- `write_tasks[]`
- `readonly_tasks[]`

### 6.5 `run_task_loop()`

职责：

- 驱动 Task 内局部收口直到：
  - `READY_FOR_ANCHOR`
  - `BLOCKED`
  - `ESCALATED`

核心步骤：

1. 构建 `task_packet`
2. 调度 `task_worker`
3. 规范化 `coder_result`
4. 构建并执行 `spec_check_packet`
5. 规范化 `task_check_result(kind=SPEC_COMPLIANCE)`
6. 若通过，再构建并执行 `quality_check_packet`
7. 规范化 `task_check_result(kind=CODE_QUALITY)`
8. 若全部通过，则切 anchor 并进入 formal seal

停止条件：

- 达到 `READY_FOR_ANCHOR`
- 超过最大局部修补轮次
- 进入 `BLOCKED`
- 需要人工裁决

### 6.6 `seal_milestone()`

职责：

- 确认 Milestone 全部 Task 已 `DONE`
- 生成或更新 milestone branch / PR
- 执行 G2
- 构建 R2 packet 并生成 formal review 结果
- 更新 `milestone_state`

输出：

- `latest_pr_ref`
- `latest_g2_ref`
- `latest_r2_ref`

### 6.7 `seal_initiative()`

职责：

- 确认全部 Milestone 已 `MERGED`
- 生成 release / rollout candidate
- 执行 G3
- 构建 R3 packet 并生成 formal review 结果
- 更新 `initiative_state`

### 6.8 `replay_or_resume_runtime()`

职责：

- 从 canonical source 完整重建主状态
- 恢复最近一轮 packet / observation / decision 索引
- 让主线程能在 crash、重启或 cache 清空后继续推进

技术裁决：

- 恢复逻辑不能假设上一轮 agent 会话仍存在
- controller 恢复后必须以结构化工件重新接管，而不是依赖聊天历史

## 7. Task Loop 详细技术设计

### 7.1 Build Packet

输入：

- `task_definition`
- `task_state`
- frontier 上下文
- 依赖完成快照

输出：

- `task_packet`

要求：

- 只下发当前轮需要的边界
- 明确列出 `must_do`、`must_not_do`、`acceptance`
- 显式带上 task 当前最新 formal / local 状态

### 7.2 Implement

执行者：

- `task_worker`

输入：

- `task_packet`

输出：

- `coder_result`

要求：

- 必须回报实际改动文件与已执行检查
- 不得宣称 Task 已 formal pass
- 若发现 scope 不足，只能上报，不得自行重写规划

### 7.3 Spec Check

执行者：

- `spec_reviewer`

输入：

- `spec_check_packet`
- `coder_result`

输出：

- `task_check_result(kind=SPEC_COMPLIANCE)`

通过条件：

- `must_do` 已覆盖
- `must_not_do` 未被违反
- `acceptance` 至少达到可进入工程质量检查的程度

失败后行为：

- `loop_phase=FIX_SPEC`
- controller 生成新的 implement round

### 7.4 Quality Check

执行者：

- `quality_reviewer`

输入：

- `quality_check_packet`
- `coder_result`
- spec pass 证据

输出：

- `task_check_result(kind=CODE_QUALITY)`

通过条件：

- 无阻断级工程问题
- 必需检查已执行或给出合法跳过原因
- diff 边界内不存在明显回归与噪音

失败后行为：

- `loop_phase=FIX_QUALITY`
- controller 生成新的 implement round

### 7.5 READY_FOR_ANCHOR

进入条件：

- 最新一轮 implement 已完成
- spec check pass
- quality check pass
- 无待补 runtime facts
- 无待升级边界冲突

此时 controller 的唯一允许动作是：

- 切 `anchor(<milestone>/<task>)`
- 更新 `task_state.last_anchor_commit`
- 推进到 `IN_G1`

### 7.6 Anchor / G1 / R1 正式收口

`READY_FOR_ANCHOR` 之后的动作不再属于 Task 内部检查，而属于 formal seal：

1. 创建 anchor commit
2. 执行 G1，并记录 `gate_result(profile=G1)`
3. 构建 R1 packet
4. 执行 formal review，并记录 `review_result(profile=R1)` 或其过渡兼容表示
5. 若 R1 clean，则 `formal_status=DONE`

任何一个 formal seal 失败，都不得回写为“内部检查失败”；必须回到正式状态机处理：

- G1 fail：回到 `IN_FLIGHT`
- R1 fail：回到 `IN_FLIGHT`
- review 无法判断：进入升级路径

## 8. skills / agents / scripts 接口边界

### 8.1 skills 清单与输入输出

推荐 skill 集如下：

- `run-initiative`
- `planning-preflight`
- `task-loop`
- `cut-anchor`
- `g1-task-gate`
- `r1-task-review`
- `open-milestone-pr`
- `g2-milestone-gate`
- `r2-milestone-review`
- `g3-initiative-gate`
- `r3-initiative-review`
- `collect-runtime-facts`

输入输出原则：

- skill 输入应是结构化 packet 或对象 key
- skill 输出应是结构化结果引用，不以大段自然语言为主
- 同一 formal gate / review skill 不允许隐式决定后续调度

### 8.2 custom agents 清单与职责

推荐 custom agents：

- `task_worker`
  - 负责实现与修补
  - 可写仓库
  - 不宣布 formal passage
- `spec_reviewer`
  - 负责规范符合性检查
  - 只读
  - 只输出 `SPEC_COMPLIANCE` 结果
- `quality_reviewer`
  - 负责代码质量检查
  - 只读
  - 只输出 `CODE_QUALITY` 结果

可选辅助角色：

- `runtime_observer`
  - 只读
  - 补采日志、测试输出和局部运行事实

### 8.3 Python 脚本清单与职责

建议把确定性内核保留在 repo 脚本中，最少包括：

- `planning_parser`
- `state_rebuilder`
- `scheduler`
- `packet_builder`
- `gate_runner`
- `review_bundle_builder`
- `artifact_normalizer`
- `git_indexer`

这些脚本的职责是：

- 解析与校验结构化输入
- 维护状态机与调度规则
- 规范化 gate / review / check 工件
- 降低 skill 与 agent prompt 对业务真值的直接耦合

### 8.4 显式调用与隐式调用边界

硬约束如下：

- subagent dispatch 必须显式触发
- gate / review 不得依赖“可能会自动触发的 background reviewer”
- Automations 不得作为 formal gate 唯一执行入口
- GitHub review 可作为辅助 evidence，但正式通过要以结构化结果落盘

### 8.5 App / CLI / GitHub / Automations 接口接缝

接缝法位固定如下：

- App：日常主控制面，适合并行线程、review pane、worktree 管理
- CLI：技能与脚本调用面
- GitHub：PR 协作与辅助 review 面
- Automations：shadow 巡检、提醒、重复分析面

禁止事项：

- 不把 App 会话历史当业务真值
- 不把 GitHub 评论线程当 formal state machine
- 不把 Automations 生成的摘要直接当 formal gate 结论

## 9. 持久化、目录与工件布局

### 9.1 目录结构

推荐运行目录：

```text
.initiative-runtime/
└─ <initiative_key>/
   ├─ state.json
   ├─ packets/
   ├─ reports/
   ├─ facts/
   ├─ observations/
   ├─ decisions/
   └─ drafts/
```

其中：

- `packets/` 存执行包与 review packet
- `reports/` 存 gate / review 结构化结果与渲染输出
- `facts/` 存运行事实
- `observations/` 存局部观察
- `decisions/` 存 controller 局部裁决
- `drafts/` 存临时草稿，不参与业务真值

### 9.2 命名规范

推荐命名：

- `packets/task-<task_key>-r<round>.json`
- `packets/spec-<task_key>-r<round>.json`
- `packets/quality-<task_key>-r<round>.json`
- `reports/g1-<task_key>.json`
- `reports/r1-<task_key>.json`
- `reports/g2-<milestone_key>.json`
- `reports/r2-<milestone_key>.json`
- `reports/g3-<initiative_key>.json`
- `reports/r3-<initiative_key>.json`

要求：

- 文件名必须能反推出对象类型、对象 key 与轮次
- 一次 formal seal 最多产出一个同 profile 主结果

### 9.3 持久化策略

持久化原则：

- JSON 统一 UTF-8 编码
- 写入尽量原子化
- 引用优先保存 repo 相对路径或对象 key，再必要时补绝对路径
- `state.json` 在每次 controller 关键跃迁后覆写

### 9.4 清理与恢复策略

清理策略：

- `.initiative-runtime/` 默认加入 `.gitignore`
- 允许整体删除后重建
- 删除前若需保留展示材料，应先导出 formal reports 到 durable plane

恢复策略：

- 先重跑 `planning_preflight`
- 再执行 `rebuild_initiative_state()`
- 最后恢复最近 packet / decision 索引供继续调度

### 9.5 Git / branch / PR / candidate 索引策略

推荐索引规则：

- milestone branch：`codex/<initiative_key>/<milestone_key>`
- Task anchor：结构化 commit subject
- Milestone PR：保存在 `milestone_state.latest_pr_ref`
- Initiative candidate：保存在 `initiative_state.notes` 或独立 candidate ref

技术裁决：

- branch / PR / candidate 是工程收口载体，不是对象层本身
- controller 只能把它们当 evidence index，不得把它们误当 `milestone_state` 或 `initiative_state`

## 10. 错误模型与升级协议

### 10.1 输入不合法错误

包括：

- machine block 缺字段
- 引用路径失效
- 依赖指向未知对象
- 非法枚举值

处理：

- 立即 preflight fail
- 禁止启动运行主链

### 10.2 状态冲突错误

包括：

- `task_state.formal_status` 与现有 artifacts 不一致
- `loop_phase` 与 formal status 组合非法
- milestone / initiative 状态无法由下层状态推出

处理：

- 以重建结果为准
- 若仍冲突，进入 `WAITING_ESCALATION`

### 10.3 运行事实不足错误

包括：

- 无法确认缺陷是否真实
- 缺少必要测试输出
- 需运行环境数据但无法获得

处理：

- 先请求 `runtime_fact`
- 超过上限后升级人工

### 10.4 跨层升级错误

包括：

- Task 修复需要改写 Milestone reference assignment
- Milestone 收口要求变更 Initiative success criteria
- review 发现 sealed decision 已不成立

处理：

- 不在 Task 内自动吞掉
- 升级到对应上层裁决点

### 10.5 用户断点与人工裁决入口

必须保留的人工入口：

- planning blocked
- frontier blocked
- 关键边界冲突
- R2 / R3 前的正式断点
- release / rollout candidate 交付断点

### 10.6 不可恢复错误与 fail-safe 策略

遇到以下情况时，controller 必须停止自动推进：

- 结构化工件损坏且无法重建
- Git 工作树处于不可解释的冲突态
- formal review 与 gate 证据彼此矛盾
- 当前仓库状态已越过 `must_not_do` 明确边界

fail-safe 原则：

- 停在最近可解释对象层
- 输出结构化错误
- 不做隐式回退或隐式强推

## 11. 测试与验证设计

### 11.1 schema / model tests

最低覆盖：

- `initiative_plan` parser / validator
- `task_packet`
- `task_check_result`
- `coder_result`
- `review_result`
- `task_state`

### 11.2 state machine tests

最低覆盖：

- Task formal status 跃迁
- Task loop phase 跃迁
- Milestone seal 跃迁
- Initiative seal 跃迁
- blocked / deferred / escalation 分支

### 11.3 contract tests

最低覆盖：

- packet builder 输出
- gate runner 输出
- review bundle 输出
- artifact normalizer 输出

### 11.4 scenario tests

建议至少覆盖以下场景：

- 单 Milestone 单 Task 完整闭环
- spec fail 后修补再通过
- quality fail 后修补再通过
- 缺 runtime facts 后补采再继续
- Milestone seal 成功
- Initiative seal 成功

### 11.5 minimal Codex smoke tests

仅在核心合同测试通过后执行，目标是验证：

- skill 能按预期接收 packet
- custom agent 能按预期返回结构化结果
- 显式 subagent 调度链可跑通一轮

### 11.6 文档与实现一致性检查

应建立最少两类一致性检查：

- 文档中的状态枚举与代码枚举一致
- 文档中的 artifact 命名规则与实现输出一致

## 12. 待决技术问题

当前仍保留三项非阻断待决问题：

第一，`review_result` 是否在首轮实现中直接统一覆盖 `R2 / R3`。  
若实现成本过高，可先保留 `R1` 统一、`R2 / R3` 过渡适配，但目标模型已在本文档明确。

第二，Initiative machine block 的最终承载形态是否长期保留在 markdown fenced block。  
若后续迁移到独立 JSON / YAML 文件，必须保持 parser 输出的 `initiative_plan` 合同不变。

第三，read-only runtime observer 是否需要成为单独 custom agent。  
v1 可先复用通用只读 agent，只要其输出能落成标准化 `runtime_fact` 即可。
