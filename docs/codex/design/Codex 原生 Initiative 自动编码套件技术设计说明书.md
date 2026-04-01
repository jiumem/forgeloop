# Codex 原生 Initiative 自动编码套件技术设计说明书

## 封面信息卡

| 项目 | 内容 |
| --- | --- |
| 文档名称 | Codex 原生 Initiative 自动编码套件技术设计说明书 |
| 文档层级 | Codex 落地方案层 / 技术设计层 |
| 文档定位 | 对总体机制文档中的两个 workflow 做工程化落地的技术定义文档 |
| 适用范围 | 需要实现运行文档、路径布局、machine block、subagent 落位、解析脚本与恢复逻辑的仓库 |
| 非目标 | 不重述总体机制法位；不展开专项排期；不直接撰写 subagent 系统提示词正文 |

## 0. 文档定位

本文档只回答一个问题：

> 第一篇里已经封板的两个 workflow，在工程层面究竟落成什么文档、什么路径、什么 machine block、什么 subagent 边界、什么恢复与校验逻辑。

本文档不再沿用旧的 `packet-first / brief-note-report` 组织方式。
新的技术主轴固定为：

- 先定义两个 workflow 在工程层的落位
- 再定义 `Global State Doc` 与三层 `Review Rolling Doc`
- 再定义这些文档的路径、命名和内部结构
- 再定义 subagent、skills、scripts 如何围绕这些文档工作
- 最后才定义状态、循环算法、恢复与测试

本文档与相邻文档的关系固定如下：

- 第一篇总体机制文档负责机制、角色、责任、交接协议与总循环
- 本文档负责路径、结构、machine block、subagent 接缝与算法
- subagent 的系统提示词将单独落到多篇文档中，不内嵌在本文档
- 专项实施作战计划书只负责排期、PR、验收和推进，不再重复定义技术合同

## 1. 技术目标与设计边界

### 1.1 技术目标

本设计的技术目标固定为七项：

第一，**第二篇必须成为两个 workflow 的实现设计文档，而不是旧 artifact 清单文档。**  
文档结构、状态、路径和算法都必须围绕 `设计规划循环` 与 `编码执行循环` 组织。

第二，**运行中的主通信面必须收敛成最小集合。**  
v1 只承认以下四份主运行文档：

- `Global State Doc`
- `Task Review Rolling Doc`
- `Milestone Review Rolling Doc`
- `Initiative Review Rolling Doc`

第三，**formal 输出必须内嵌在滚动文档里，而不是再拆出平行文件。**  
`G1 / G2 / G3` 与 `R1 / R2 / R3` 的正式结构化结果，都应作为 typed machine block 追加在对应 rolling doc 中；JSON 只做派生视图，不再做第二真理源。

第四，**repo 内正式文档面与本地派生面必须分离。**  
repo 内的运行文档是协作真理源；本地如需生成 JSON 视图、解析缓存和恢复辅助数据，也只能是实现私有派生面，不进入正式路径合同。

第五，**编码执行循环必须体现“单一持续 coder / 每轮 fresh reviewer”。**  
coder 是 Initiative 执行期内持续持有实现 ownership 的单一角色；reviewer 在每次 `R1 / R2 / R3` 时都 fresh 派生。

第六，**subagent 的系统提示词应单列为独立文档资产。**  
本文档只定义它们放在哪里、如何装配进 Codex agent 存储、如何与 skills / scripts 接线，不直接承载提示词正文。

第七，**运行态必须可从文档与工程真理源重建。**  
任何本地派生视图或缓存丢失后，系统仍应能从 Initiative 总任务文档、repo 内运行文档、Git/PR 事实与结构化 commit 恢复主状态。

### 1.2 技术非目标

本文档明确不承担以下目标：

- 不把第一篇已经封板的机制法位重写一遍
- 不回到 `task_brief / implementation_note / review_brief / review_report` 多文档并列模型
- 不把 `gate_result`、`review_result` 继续设计成平行独立文件
- 不把 `spec check / quality check / READY_FOR_ANCHOR` 旧状态机重新写回 v1
- 不在 v1 引入分布式 worker、队列或常驻后台服务
- 不在本文档直接给出 coder / reviewer 的完整系统提示词
- 不把任何本地派生缓存重新升格为真理源

### 1.3 与第一篇总体机制文档的衔接

本文档直接承接第一篇中已经封板的这些裁决：

- 运行主形态是 `Supervisor + bounded subagents`
- 系统主轴是两个 workflow
- 当前真正要落地的是 `编码执行循环`
- `Global State Doc + 三层 Review Rolling Doc` 是正式协作通信面
- `coder` 是持续执行者，`reviewer` 每轮 fresh 派生
- `Supervisor` 不编码，只负责编排、状态维护、升级裁决与用户断点

因此，凡属下列问题，以第一篇为准，本文档只做工程展开：

- 为什么要有两个循环
- 为什么 `Supervisor` 不亲自编码
- 为什么 `Task -> Milestone -> Initiative` 要做三段对抗式循环
- 为什么运行中的主通信面不能退化成接口调用链

## 2. 两个 workflow 的技术落位

### 2.1 设计规划循环：先保留骨架，不展开正文

`设计规划循环` 在 v1 的技术落位先做保留位，不在本文档展开完整算法。
但它的技术骨架必须先预留，防止第二篇以后再次重构。

当前只做一条技术裁决：

- 规划循环未来也必须走“单一主文档 + machine block + derived view”路线，而不是再重新长出平行 packet 体系

### 2.2 编码执行循环：第二篇当前真正要实现的核心

`编码执行循环` 是本文档当前真正要落地的核心。
它的工程骨架固定为三层：

第一层，**repo 内正式运行文档层**  
保存 `Global State Doc` 与三层 `Review Rolling Doc`，这是 Agent 协作的主通信面。

第二层，**工程真理源层**  
保存 Git 工作树、结构化 commit、分支、PR、测试和实际代码。

第三层，**skills / subagents / scripts 执行层**  
围绕正式文档读写与工程真理源操作工作，但本身不成为真理源。

`编码执行循环` 的工程设计必须回答以下问题：

- 四份主运行文档落在 repo 的哪里
- 文档内部怎样组织成可读、可追加、可解析的结构
- coder、reviewer、Supervisor 各自往哪些文档追加什么
- subagent 提示词源文档放在哪里，实际 runtime manifest 放在哪里
- scripts 怎样只解析 machine block，而不是依赖隐式上下文记忆
- 系统如何从文档与 Git 恢复当前执行状态

### 2.3 当前技术裁决

围绕 `编码执行循环`，本文档做以下技术裁决：

第一，**不再设计独立的 `task_brief / implementation_note / gate_evidence_note / review_brief / review_report` 文件。**  
这些概念如果继续存在，只能作为 rolling doc 内部的 machine block 类型，而不是一级文件类型。

第二，**`gate_result` 与 `review_result` 仍然存在，但它们的法位改成“rolling doc 中的正式结构化 block”。**  
脚本如有需要可以做临时结构化提取，但不能再要求 reviewer 额外写一份平行结果文件。

第三，**`Global State Doc` 不是自由文本日志，而是最小可更新状态脊柱。**  
它必须足够让 Supervisor 更新全局位置与下一动作，但不能重新长成第二套过程账本。

第四，**三层 `Review Rolling Doc` 是 append-mostly 文档。**  
创建后的 header 与 contract snapshot 固定；后续主要以回合为单位追加；不允许反复覆盖历史回合。

第五，**`G1` 只出现在 `Task Review Rolling Doc` 内。**  
`G2` 只出现在 `Milestone Review Rolling Doc` 内。  
`G3` 只出现在 `Initiative Review Rolling Doc` 内。

第六，**三层 loop 默认同构；代码修补默认留在当前对象内完成。**  
`Task / Milestone / Initiative` 中的 coder 默认都应在当前对象内继续修补并重跑对应 gate。只有修补已经需要独立 `Task` 合同、明确新对象边界，或明显超出当前对象收口半径时，才通过 `Global State Doc` 对象化为新的 repair task，再由同一个 coder 回落到 `Task loop`。

## 3. 真理源与落盘平面

### 3.1 单一真理源划分

本设计只承认三类真理源：

| 类别 | 真理源 | 说明 |
| --- | --- | --- |
| 规划真理源 | Initiative 总任务文档 | 描述 Initiative / Milestone / Task 的静态总图 |
| 协作真理源 | `Global State Doc` + 三层 `Review Rolling Doc` | 描述当前执行状态、回合、裁决、交接与升级 |
| 工程真理源 | Git 工作树、结构化 commit、分支、PR、测试 | 描述真实代码与正式工程封口 |

任何技术设计都必须遵守这条硬边界：

> 文档负责表达协作与裁决。  
> Git 负责表达真实代码变化。  
> cache 只负责加速解析与恢复。

### 3.2 repo 内正式落盘平面

repo 内正式落盘平面固定为：

```text
docs/codex/runtime/<initiative_key>/
  global-state.md
  reviews/
    task/<milestone_key>/<task_key>.md
    milestone/<milestone_key>.md
    initiative/<initiative_key>.md
```

这里的每个 markdown 文档都属于正式协作文档，不是缓存副本。
它们的特征是：

- 人可读
- Agent 可持续追加
- scripts 可通过 machine block 稳定解析
- 可以随分支一起演化与审计

### 3.3 派生视图与本地缓存不设固定目录合同

v1 仍允许实现按需生成临时结构化提取、parser 缓存或恢复辅助对象。

但本文档不再为这些对象规定固定目录。
原因只有一个：

> 这些对象不是真理源，也不该继续占据用户心智中的正式法位。

因此，第二篇只保留两条硬约束：

- 不复制 `global-state.md` 或三层 rolling doc 的 markdown 正文
- 不再落一套平行的 `briefs/notes/results` 正式目录

### 3.4 formal 输出如何存在

为了避免“滚动文档”和“formal result 文件”双真值，formal 输出存在方式固定如下：

- `G1` 的正式结果是 `Task Review Rolling Doc` 中的 `g1_result` block
- `R1` 的正式结果是 `Task Review Rolling Doc` 中的 `r1_result` block
- `G2` 的正式结果是 `Milestone Review Rolling Doc` 中的 `g2_result` block
- `R2` 的正式结果是 `Milestone Review Rolling Doc` 中的 `r2_result` block
- `G3` 的正式结果是 `Initiative Review Rolling Doc` 中的 `g3_result` block
- `R3` 的正式结果是 `Initiative Review Rolling Doc` 中的 `r3_result` block

JSON 里的 `gate_result_view`、`review_result_view` 只是从这些 block 导出的结构化视图。

## 4. 目录、路径与命名

### 4.1 repo 内正式目录布局

第二篇定义的目标目录布局如下：

```text
docs/
  codex/
    runtime/
      <initiative_key>/
        global-state.md
        reviews/
          task/
            <milestone_key>/
              <task_key>.md
          milestone/
            <milestone_key>.md
          initiative/
            <initiative_key>.md
    agents/
      README.md
      coder.md
      task-reviewer.md
      milestone-reviewer.md
      initiative-reviewer.md
```

这里有两组路径必须区分：

- `docs/codex/runtime/` 是正式运行文档面
- `docs/codex/agents/` 是 subagent 系统提示词源文档面

### 4.2 runtime manifest 与装配路径

subagent 的**可执行 manifest 真理源**固定为：

```text
plugins/forgeloop/agents/
```

实际 Codex 运行时，默认应 materialize 到全局 Codex agent 存储：

```text
~/.codex/agents/
```

如需项目级覆盖，可改为 materialize 到：

```text
<project>/.codex/agents/
```

推荐装配关系如下：

- `plugins/forgeloop/agents/coder.toml` -> `~/.codex/agents/coder.toml`
- `plugins/forgeloop/agents/task_reviewer.toml` -> `~/.codex/agents/task_reviewer.toml`
- `plugins/forgeloop/agents/milestone_reviewer.toml` -> `~/.codex/agents/milestone_reviewer.toml`
- `plugins/forgeloop/agents/initiative_reviewer.toml` -> `~/.codex/agents/initiative_reviewer.toml`

`docs/codex/agents/*.md` 只保留 reference mirror 法位；可执行提示词正文只认 `plugins/forgeloop/agents/*.toml`。

### 4.3 命名规则

路径命名规则固定为：

- Initiative 级目录名使用 `initiative_key`
- Milestone 级目录名或文件名使用 `milestone_key`
- Task 级文件名使用 `task_key`
- 不在文件名中嵌入回合号；回合由文档内部 heading 与 machine block 字段表达
- 不在文件名中嵌入 verdict；verdict 只在 block 里表达

正式文档文件名固定如下：

- `global-state.md`
- `reviews/task/<milestone_key>/<task_key>.md`
- `reviews/milestone/<milestone_key>.md`
- `reviews/initiative/<initiative_key>.md`

### 4.4 旧模型迁移规则

旧模型中的下列路径与文件类型，统一视为迁移前遗留设计：

- `briefs/`
- `notes/`
- `results/`
- `facts/`
- `observations/`
- `decisions/`
- `drafts/`
- 独立的 `task_packet_view / review_packet_view / gate_bundle_view` 文件树

它们在 v1 新设计里不再是正式结构。
如果为了兼容工具链仍需生成，只能作为临时派生输出存在，不构成固定路径合同。

## 5. 文档工件与内部结构设计

### 5.1 通用 machine block 语法

所有正式运行文档都采用统一的“markdown 叙述 + `forgeloop` machine block”语法。
标准形式如下：

````markdown
```forgeloop
kind: r1_result
round: 2
author_role: reviewer
created_at: 2026-03-27T14:30:00+08:00
verdict: changes_requested
functional_correctness: pass
validation_adequacy: fail
local_structure_convergence: pass
local_regression_risk: medium
findings:
  - id: R1-001
    severity: major
    summary: 缺失异常路径测试
next_action: continue_task_repair
```
````

统一规则如下：

- machine block 的 fenced code info string 固定为 `forgeloop`
- body 使用 YAML
- 每个 block 都必须有 `kind`
- `header` 与 `contract_snapshot` block 必须携带对象身份字段
- append-only 的正式事实块必须携带 `round`、`author_role`、`created_at`
- 同一份 rolling doc 内的对象身份默认由 header 继承，不要求每个事实块重复写 `doc_key`
- prose 可自由书写，但脚本只读取 `forgeloop` block

### 5.2 可替换块与追加块的边界

围绕“第一篇 update-only、后三篇 append-only”这条原则，machine block 分成两类：

第一类，**update-only 块**  
只允许出现在 `Global State Doc` 中，由 Supervisor 原地更新，脚本只认当前文档里的最新版本。

第二类，**append-only 块**  
只允许出现在三层 `Review Rolling Doc` 中；一旦写入，不应回改，只能在末尾继续追加。

`Global State Doc` 允许出现的 update-only 块只有这些：

- `global_state_header`
- `current_snapshot`
- `next_action`
- `last_transition`

三层 rolling doc 允许出现的 append-only 块固定为：

- `task_review_header` / `milestone_review_header` / `initiative_review_header`
- `task_contract_snapshot` / `milestone_contract_snapshot` / `initiative_contract_snapshot`
- `coder_update`
- `g1_result` / `g2_result` / `g3_result`
- `anchor_ref` / `fixup_ref`
- `r1_result` / `r2_result` / `r3_result`

其中：

- header 与 contract snapshot 只写一次
- 之后每一轮只追加正式事实块
- 不再引入 `coder_round_open`、`reviewer_round_open`、`supervisor_transition`、事件账本这类仪式性块
- `Global State Doc.next_action` 必须直接复用当前 runtime loop 的正式路由词表；不要再发明平行 supervisor 动作名，例如 `dispatch_coder_continue_task`

### 5.3 `Global State Doc` 结构

`Global State Doc` 是全局状态脊柱，不是自由文本工作日志。
它的推荐结构固定如下：

````markdown
# <initiative_key> Global State

[Section] Summary
<人类可读摘要>

```forgeloop
kind: global_state_header
initiative_key: INIT-001
total_task_doc_ref: docs/initiatives/INIT-001.md
created_at: ...
updated_at: ...
```

```forgeloop
kind: current_snapshot
active_plane: task
initiative_key: INIT-001
milestone_key: MS-002
task_key: TASK-002-API
coder_slot: CODER-1
round: 1
```

```forgeloop
kind: next_action
action: continue_task_coder_round
blocking_reason: null
updated_at: ...
```

```forgeloop
kind: last_transition
updated_at: ...
from_action: enter_r1
to_action: task_done
reason: r1_clean
```
````

`Global State Doc` 的技术职责只有五项：

- 提供当前最小快照
- 指向当前活跃对象
- 给出下一步调度动作
- 记录最近一次关键转换
- 为恢复算法提供单一入口

它不承担这些职责：

- 不保存 reviewer 的详细 findings 主文
- 不保存 coder 的实现细节主文
- 不维护 Milestone / Task 的完整状态表
- 不复制 Git diff、日志全文、测试输出全文

### 5.4 `Task Review Rolling Doc` 结构

`Task Review Rolling Doc` 是 `Task` 半径内唯一正式运行文档。
它同时承载：

- Task 合同快照
- coder 连续实现与 G1 尝试
- `anchor / fixup` 正式封口
- `R1` 结果
- Task 级回合交接

推荐结构固定如下：

````markdown
# Task Review Rolling Doc: <task_key>

```forgeloop
kind: task_review_header
initiative_key: INIT-001
milestone_key: MS-002
task_key: TASK-002-API
doc_key: TASK-002-API
coder_slot: CODER-1
created_at: ...
```

```forgeloop
kind: task_contract_snapshot
summary: ...
spec_refs:
  - ...
acceptance:
  - ...
g1_commands:
  - npm test -- api
```

[Round 1]

```forgeloop
kind: coder_update
round: 1
author_role: coder
created_at: ...
files_touched:
  - src/api.ts
  - tests/api.test.ts
summary: ...
```

```forgeloop
kind: g1_result
round: 1
author_role: coder
created_at: ...
profile: G1
verdict: pass
commands:
  - npm test -- api
evidence_refs:
  - local://...
```

```forgeloop
kind: anchor_ref
round: 1
author_role: coder
created_at: ...
commit: anchor(ms-002/task-002-api): ...
sha: abc123
```

```forgeloop
kind: r1_result
round: 1
author_role: reviewer
created_at: ...
verdict: clean
functional_correctness: pass
validation_adequacy: pass
local_structure_convergence: pass
local_regression_risk: low
findings: []
next_action: task_done
```
````

技术边界要点：

- `Task Review Rolling Doc` 是 append-only，已写入的 round 不回改
- header 绑定对象身份与当前逻辑 `coder_slot`，用于恢复 continuity
- `G1` 失败时，不进入 reviewer；coder 继续在同一 round 下追加 `coder_update` 与新的 `g1_result`
- `G1` 通过后才允许写入 `anchor_ref` 或 `fixup_ref`
- `R1` 只审已经写入的正式锚点块
- 一个 Task round 只有在 `r1_result` 写入后才算闭合；若 `R1` 要求修补，同一个 coder 在下一 round 继续

### 5.5 `Milestone Review Rolling Doc` 结构

`Milestone Review Rolling Doc` 是 `G2 / R2` 对抗循环的唯一正式文档。
它同时承载：

- Milestone 合同快照
- 已纳入审查的 Task / anchor 集合
- coder 的阶段级验证结果
- reviewer 的 `R2` 裁决
- 若需代码修补时的回落记录

推荐结构固定如下：

````markdown
# Milestone Review Rolling Doc: <milestone_key>

```forgeloop
kind: milestone_review_header
initiative_key: INIT-001
milestone_key: MS-002
doc_key: MS-002
coder_slot: CODER-1
created_at: ...
```

```forgeloop
kind: milestone_contract_snapshot
goal: ...
acceptance:
  - ...
g2_commands:
  - npm test
task_scope:
  - TASK-002-API
  - TASK-003-UI
```

[Round 1]

```forgeloop
kind: g2_result
round: 1
author_role: coder
created_at: ...
profile: G2
verdict: pass
anchors:
  - TASK-002-API@abc123
  - TASK-003-UI@def456
commands:
  - npm test
residual_risks: []
```

```forgeloop
kind: r2_result
round: 1
author_role: reviewer
created_at: ...
verdict: changes_requested
stage_structure_convergence: fail
mainline_merge_safety: fail
evidence_adequacy: pass
residual_risks:
  - 兼容层仍保留双真值
required_follow_ups:
  - continue_milestone_repair
  - rerun_g2_after_stage_boundary_fix
```
````

技术边界要点：

- `Milestone Review Rolling Doc` 是 append-only，header 与 contract snapshot 固定后不回改
- header 绑定对象身份与当前逻辑 `coder_slot`，用于恢复 continuity
- `G2` 由同一个 coder 负责执行并写块，`Supervisor` 不直接写 `g2_result`
- `R2` 发现代码问题时，不允许 reviewer 直接修补代码
- 若 `G2` 自身已经给出 `continue_milestone_repair` 一类结论，默认仍留在当前 Milestone 内修补并重跑 `G2`
- 只有修补已经需要独立 Task 合同、明确新对象边界或明显超出当前 Milestone 收口半径时，才对象化为新的 repair task，并在 `Global State Doc` 中更新当前状态
- 若已对象化为 repair task，回修完成后，回到同一份 `Milestone Review Rolling Doc` 追加下一 round

### 5.6 `Initiative Review Rolling Doc` 结构

`Initiative Review Rolling Doc` 是 `G3 / R3` 对抗循环的唯一正式文档。
它同时承载：

- Initiative 交付合同快照
- 进入交付候选的 Milestone 集合
- coder 的交付级验证结果
- reviewer 的 `R3` 裁决
- 若需再次回落修补时的升级记录

推荐结构固定如下：

````markdown
# Initiative Review Rolling Doc: <initiative_key>

```forgeloop
kind: initiative_review_header
initiative_key: INIT-001
doc_key: INIT-001
coder_slot: CODER-1
created_at: ...
```

```forgeloop
kind: initiative_contract_snapshot
goal: ...
success_criteria:
  - ...
g3_commands:
  - npm run release:check
milestone_scope:
  - MS-001
  - MS-002
```

[Round 1]

```forgeloop
kind: g3_result
round: 1
author_role: coder
created_at: ...
profile: G3
verdict: pass
commands:
  - npm run release:check
residual_risks: []
```

```forgeloop
kind: r3_result
round: 1
author_role: reviewer
created_at: ...
verdict: clean
delivery_readiness: pass
release_safety: pass
evidence_adequacy: pass
residual_risks: []
```
````

技术边界要点：

- `Initiative Review Rolling Doc` 是 append-only，header 与 contract snapshot 固定后不回改
- header 绑定对象身份与当前逻辑 `coder_slot`，用于恢复 continuity
- `G3` 也由同一个 coder 执行
- 若 `G3` 自身已经给出 `continue_initiative_repair` 一类结论，默认仍留在当前 Initiative 内修补并重跑 `G3`
- `R3` 发现要改代码时，也默认先留在当前 Initiative 内修补；只有修补已经需要独立 Task 合同、明确新对象边界或明显超出当前 Initiative 收口半径时，才对象化为 repair task
- `R3 clean` 后，`Global State Doc` 才能把 Initiative 标记为 `DONE`

## 6. subagents、提示词与执行边界

### 6.1 角色与运行时落位

角色落位固定如下：

| 角色 | 运行时位置 | 是否 custom agent | 主职责 |
| --- | --- | --- | --- |
| Supervisor | 主线程 | 否 | 维护 `Global State Doc`、选择对象、编排循环、派发 subagent、处理升级与用户断点 |
| Coder | subagent | 是 | 持续实现、修补、运行 `G1 / G2 / G3`、向 rolling doc 追加 coder 与 gate block |
| Task Reviewer | subagent | 是 | fresh 派生，执行 Task review 并写入 `r1_result` |
| Milestone Reviewer | subagent | 是 | fresh 派生，执行 Milestone review 并写入 `r2_result` |
| Initiative Reviewer | subagent | 是 | fresh 派生，执行 Initiative review 并写入 `r3_result` |
这里有一个非常关键的技术约束：

> coder 是“逻辑上的单一持续角色”，不是“每轮重新定义的新角色”。

v1 的优先实现方式应是：

- 优先复用同一个 coder agent thread
- 如果运行时必须重建 thread，Supervisor 必须在 `Global State Doc` 中记录其继任关系
- 即使物理 thread 变了，逻辑 `coder_slot` 也不能变成新的角色

### 6.2 系统提示词源文档位置

subagent 系统提示词的**可执行真理源**固定为：

```text
plugins/forgeloop/agents/
```

设计追踪与阅读导航可保留在：

```text
docs/codex/agents/
```

推荐最小执行集合如下：

- `planner.toml`
- `coder.toml`
- `task_reviewer.toml`
- `milestone_reviewer.toml`
- `initiative_reviewer.toml`

这些 manifest 负责定义：

- 角色职责
- 输出纪律
- 允许读取的文档面
- 禁止越权的边界

`docs/codex/agents/*.md` 如保留，只承担 reference mirror 职责。

### 6.3 runtime manifest 位置

真正供 Codex runtime 识别的 custom agent manifest 位置固定为 Codex agent 存储：

```text
~/.codex/agents/
```

如需项目级覆盖，则使用：

```text
<project>/.codex/agents/
```

manifest 至少负责表达：

- `name`
- `description`
- `model`
- `reasoning_effort`
- `developer_instructions` 或其引用方式

这些 manifest 应从 `plugins/forgeloop/agents/*.toml` materialize 进入目标项目。
如果需要维护 `docs/codex/agents/*.md` reference mirror，应由专门脚本或明确治理流程同步。
本文档不允许人工维护两套独立 prompt 真源。

### 6.4 skills 与 scripts 的边界

workflow 入口与执行边界固定如下：

- skills 负责选择什么时候进入某个 workflow 阶段
- custom agents 负责 bounded role behavior
- scripts 负责解析 markdown machine block、执行确定性校验与 Git 帮助动作

明确禁止：

- 让 skills 成为业务真理源
- 让 subagent 靠隐式上下文口口相传主要法源
- 让 scripts 直接发明新的业务状态并回写主文档

### 6.5 当前推荐 skill / script 接缝

当前推荐最小接缝如下：

- `run-initiative`：Supervisor 入口 skill
- `continue-task-coding`：驱动 coder 继续当前 Task
- `run-r1-review`：派发 fresh reviewer 执行 `R1`
- `run-r2-review`：派发 fresh reviewer 执行 `R2`
- `run-r3-review`：派发 fresh reviewer 执行 `R3`
- `rebuild-resume-hints`：从文档与 Git 重建最小恢复提示

这些名字是技术目标名，不要求当前仓库已经全部存在。

## 7. 编码执行 workflow 的恢复机制与循环算法

### 7.1 最小恢复机制

这套系统不应再定义一组厚重的 `initiative_state / milestone_state / task_state` 运行对象。
对 Codex 原生工作流来说，ROI 最高的恢复机制是：

第一，**优先复用原有 Codex thread。**  
如果 `Supervisor` 主线程和当前 coder thread 仍然存在，最优恢复方式就是直接回到原 thread，用户输入 `go on` 或等价续跑指令继续推进。

第二，**thread 不可用时，再用文档重建最小恢复提示。**  
新的 `Supervisor` 线程只需要读取：

- Initiative 总任务文档
- `Global State Doc`
- 三层 `Review Rolling Doc`
- Git / PR / commit 事实

然后回答四个问题即可继续：

- 当前停在哪一层循环
- 当前活跃的 Milestone / Task 是什么
- 当前应该续写哪一篇 rolling doc
- 下一步动作是什么

第三，**局部结构化提取只做恢复加速，不定义业务状态对象。**  
如果实现想生成临时 JSON、局部索引或恢复提示，可以生成；但它们只是 `resume hints`，不是正式状态模型。

因此，本文档对恢复层只保留一个最小合同：

- `Global State Doc` 提供“当前位置 + 下一动作”
- 三层 rolling doc 提供“已经发生过哪些正式事实”
- Codex thread resume 是第一优先级
- 文档重建是 thread 丢失时的兜底路径

### 7.2 Task 执行子循环算法

`Task` 子循环的最小算法如下：

1. `Supervisor` 从 `Global State Doc` 选择当前 active task，并把 `next_action` 更新为继续当前 Task。
2. 同一个 coder 读取：
   - Initiative 总任务文档中的 Task 定义
   - `Global State Doc`
   - 当前 `Task Review Rolling Doc`
3. coder 在当前 round 下追加一个或多个 `coder_update`。
4. coder 在当前实现轮中执行 `G1`，并追加 `g1_result`。
5. 若 `G1 fail`：
   - 不进入 reviewer
   - `Global State Doc` 保持当前 Task 为 active task
   - 同一个 coder 继续追加新 `coder_update` 与新 `g1_result`
6. 若 `G1 pass`：
   - coder 切出 `anchor / fixup`
   - 在文档中追加 `anchor_ref / fixup_ref`
   - `Global State Doc` 把 `next_action` 切到进入 `R1`
7. `Supervisor` 派发 fresh `Task Reviewer`
8. reviewer 读取相同文档与对应锚点，追加 `r1_result`
9. 若 `R1 clean`：
   - `Supervisor` 更新 `Global State Doc`
   - `next_action` 切到选择下一个 ready object
10. 若 `R1 changes_requested`：
   - `Supervisor` 更新 `Global State Doc`
   - `next_action` 切到继续当前 Task 修补
   - 同一个 coder 进入下一 round

这里要特别强调：

- `G1` 是 coder 运行指令，不是独立子流程
- `R1` 是 fresh reviewer 裁决，不是 coder 自证
- round 的边界由 `r1_result` 是否已经写入决定，不由单次 G1 尝试决定

### 7.3 Milestone 的 G2 / R2 循环算法

`Milestone` 循环的最小算法如下：

1. `Supervisor` 判断 Milestone 进入阶段审查窗口：
   - 所需 Task 已 `DONE`
   - `Global State Doc` 当前没有更高优先级的阻断
2. `Supervisor` 打开或续写该 `Milestone Review Rolling Doc`
3. 同一个 coder 读取：
   - `Global State Doc`
   - Milestone 合同快照
   - 已完成 Task 的 anchor / fixup 集合
4. coder 执行 `G2` 所需验证，并追加 `g2_result`
5. 若 coder 在 `G2` 过程中发现需要代码修补：
   - 默认不进入 `R2`
   - 若仍在当前 Milestone 收口半径内，同一个 coder 继续当前 Milestone 修补并重跑 `G2`
   - 只有修补已需要独立 Task 合同、明确新对象边界或明显超出当前 Milestone 半径时，`Supervisor` 才在 `Global State Doc` 中创建 repair task，并由同一个 coder 回落到 Task 子循环
6. 若 `G2 pass`：
   - `Supervisor` 派发 fresh `Milestone Reviewer`
7. reviewer 追加 `r2_result`
8. 若 `R2 clean`：
   - `Global State Doc` 更新当前 frontier
9. 若 `R2 changes_requested`：
   - 若仍在当前 Milestone 收口半径内，同一个 coder 在下一 round 继续当前 Milestone 修补
   - 只有修补已需要独立 Task 合同、明确新对象边界或明显超出当前 Milestone 半径时，才通过 repair task 回落到 Task 子循环
   - 若已回落，回修完成后回到同一份 Milestone 文档追加下一 round

### 7.4 Initiative 的 G3 / R3 循环算法

`Initiative` 循环与 `Milestone` 循环同构，只是对象半径更大。
最小算法如下：

1. `Supervisor` 判断 Initiative 进入交付审查窗口
2. 打开或续写 `Initiative Review Rolling Doc`
3. 同一个 coder 执行 `G3` 所需验证并追加 `g3_result`
4. 若发现需要代码修补：
   - 若仍在当前 Initiative 收口半径内，同一个 coder 继续当前 Initiative 修补并重跑 `G3`
   - 只有修补已需要独立 Task 合同、明确新对象边界或明显超出当前 Initiative 半径时，`Supervisor` 才创建 repair task，并由同一个 coder 回落到 Task 子循环
5. 若 `G3 pass`：
   - `Supervisor` 派发 fresh `Initiative Reviewer`
6. reviewer 追加 `r3_result`
7. 若 `R3 clean`：
   - `Global State Doc` 更新为交付完成
8. 若 `R3 changes_requested`：
   - 若仍在当前 Initiative 收口半径内，同一个 coder 在下一 round 继续当前 Initiative 修补
   - 只有修补已需要独立 Task 合同、明确新对象边界或明显超出当前 Initiative 半径时，才回落为 repair task
   - 若已回落，修补完成后回到同一份 Initiative 文档追加下一 round

### 7.5 中断、升级与恢复

这套算法必须覆盖四类非 happy path：

第一，**用户中断**  
`Supervisor` 需要更新 `Global State Doc` 中的 `next_action` 与 `last_transition`，把系统切到等待用户裁决。

第二，**跨层升级**  
`R1` 若发现阶段级裂缝，只能写入升级建议并由 `Supervisor` 在 `Global State Doc` 中提升到 Milestone 层处理；reviewer 不直接修改层级。

第三，**coder thread 丢失**  
若物理 coder thread 丢失，`Supervisor` 可以派生继任 coder，但必须：

- 复用原 `coder_slot`
- 在 `Global State Doc` 的 `last_transition` 中记录继任关系
- 不得把它写成新角色

第四，**Codex thread 丢失或本地派生缓存丢失**  
系统必须允许仅凭：

- Initiative 总任务文档
- `Global State Doc`
- 三层 rolling doc
- Git/PR 事实

重建最小恢复提示并继续执行。

## 8. 解析脚本、Git 帮助动作与验证设计

### 8.1 parser 的职责

parser 不再解析一堆零散 artifact 文件，而只做三件事：

- 读取 `Global State Doc`
- 读取三层 `Review Rolling Doc`
- 提取 `forgeloop` machine block，生成派生视图

parser 明确禁止：

- 依赖 prose 中的隐式语义推断关键状态
- 反向把 JSON 视图写回正式 markdown 文档
- 自行发明文档里不存在的新状态

### 8.2 Git 帮助动作的职责

Git 帮助动作只承接确定性工程操作：

- 查询当前分支、提交、PR ref
- 切出 `anchor / fixup / revert`
- 校验结构化 commit 命名
- 收集 `G1 / G2 / G3` 所需命令执行证据 ref

但它们不承担：

- reviewer 裁决
- 业务状态推进
- 直接修改 `Global State Doc` 的主逻辑

### 8.3 最小验证集

第二篇定义的最小验证集固定如下：

第一，**文档语法测试**

- `forgeloop` block 能被稳定解析
- block 缺失必填字段时，parser 能报错

第二，**路径与命名测试**

- 正式文档路径符合本设计
- 不会生成第二套 markdown 正文

第三，**恢复测试**

- 从 `Global State Doc` + rolling docs 能重建最小恢复提示
- 删除任意本地辅助缓存后恢复成功

第四，**Task 回合测试**

- `G1 fail` 时不会错误进入 reviewer
- `G1 pass` 后才允许 `anchor / fixup`
- `R1 fail` 会回到同一个 coder 的下一 round

第五，**Milestone / Initiative 循环测试**

- `G2 continue_milestone_repair / G3 continue_initiative_repair` 与 `R2 / R3 changes_requested` 在当前对象半径内时，会继续留在当前 loop 修补
- 只有修补需要对象化时，才会回落 repair task
- 不允许 reviewer 或 Supervisor 越权直接改代码

第六，**文档与工程一致性测试**

- `anchor_ref / fixup_ref` 对应 commit 确实存在
- `r1_result / r2_result / r3_result` 引用的对象与当前文档对象一致

## 9. 当前待决与后续延伸

### 9.1 当前待决但不阻断封板的问题

第一，`设计规划循环` 还未展开正文。  
但其“单文档 + machine block”方向已经钉住，不阻断第二篇对编码执行循环封板。

第二，subagent manifest 从当前仓库既有角色迁移到 `coder / task-reviewer / milestone-reviewer / initiative-reviewer` 的具体计划，还需后续治理 PR 落地。  
这不阻断第二篇的技术设计成立，因为本文档只定义目标装配面。

第三，是否需要为 `Milestone Review Rolling Doc` 与 `Initiative Review Rolling Doc` 增加更细的 evidence ref 规范，后续可以在不改主骨架的前提下追加。  
当前只要 `g2_result / g3_result` 能稳定记录命令、对象范围和 evidence refs 即可。

### 9.2 明确禁止回退到的旧设计

本文档封板后，以下旧设计视为禁止回归：

- `packet-first` 主协议
- `brief / note / report` 并列一级文档
- `gate_result / review_result` 独立文件化
- `spec check / quality check / READY_FOR_ANCHOR`
- 为本地派生缓存设计固定正式路径合同
- 把 `Supervisor` 写成直接执行 `G2 / G3` 的编码者
- 把 `coder` 写成每层循环都重新定义的新角色

### 9.3 与后续文档的衔接

本文档封板后，下游文档应按以下方式承接：

- `plugins/forgeloop/agents/*.toml` 负责写可执行系统提示词与 manifest
- `~/.codex/agents/*.toml` 负责承接默认全局 runtime 副本
- `<project>/.codex/agents/*.toml` 在需要时承接项目级覆盖副本
- `docs/codex/agents/*.md` 如保留，只负责 reference mirror 与设计追踪
- skill 设计与构建规范负责定义 skills 如何调用这些角色
- 专项实施作战计划书负责把本技术设计拆成具体 PR 序列

## 10. 封板结论

第一，第二篇现在不再是旧式 artifact/state-machine 杂糅文档，而是严格围绕两个 workflow 的技术设计文档。  
其中 `设计规划循环` 先保留骨架，`编码执行循环` 完整展开。

第二，运行中的主通信面已被压缩到最小集合：  
一份 `Global State Doc`，三份分层 `Review Rolling Doc`。  
其余结果、视图、索引都降级为这些文档中的 machine block 或派生视图。

第三，repo 内正式路径与本地派生面已经分离：  
`docs/codex/runtime/<initiative_key>/` 承担正式协作真理源；本地派生缓存如需存在，也不再占据固定正式路径。

第四，subagent 的落位已经明确：  
`Supervisor` 在主线程，`coder` 是持续单一角色，`reviewer` 在每次 `R1 / R2 / R3` 时 fresh 派生；可执行提示词真理源固定在 `plugins/forgeloop/agents/`，默认运行时 materialize 到 `~/.codex/agents/`，需要时再落项目级覆盖。

第五，formal Gate / Review 的存在方式已经收敛：  
不再单独造文件，而是作为 typed machine block 追加在对应 rolling doc 中。

第六，这份技术设计已经足以支撑后续写：

- subagent 系统提示词文档
- parser / Git helper
- skill 接口与运行脚本
- 专项实施 PR 计划
