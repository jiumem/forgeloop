# Codex 原生 Initiative 自动编码—审查执行体系

**状态**：Sealed / v1
**定位**：面向 Codex 原生能力的正式落地方案
**适用范围**：已经完成方案设计、必要时完成差距分析、并具备单篇总任务文档的大型软件工程 Initiative
**非目标**：不引入外部 MCP 控制服务；不把自然语言需求直接当执行入口；不把 Task 暴露为终端用户的主操作对象

---

## 0. 封板结论

> **用户入口是 Initiative。**
> **阶段收敛边界是 Milestone。**
> **内部最小执行原子是 Task。**
> **Skill 是核心编排面。**
> **Repo 内脚本是确定性执行核。**
> **AGENTS.md / `.codex/` / `.agents/` 是仓库内治理层，而不是运行时状态层。**

这个结论与 Codex 当前原生能力是同向的。Codex 的定制层本来就由 `AGENTS.md`、skills、MCP、subagents 四层组成；其中 `AGENTS.md` 用于持久项目规则，skills 适合承载可复用 workflow，subagents 适合显式委派的专门化并行工作。skills 支持 `SKILL.md`、`scripts/`、`references/`、`assets/` 与 `agents/openai.yaml`，并采用 progressive disclosure；Codex App 原生支持 parallel threads、worktrees、automations 与内置 Git。([OpenAI开发者][1])

---

## 1. 总体法位：四层而不是三层

这套最终体系必须按四层理解，而不是把所有规则塞进一个“超级 controller”。

| 层                  | 正式职责                                                    | 真理源                   | 在 Codex 中的承载物                                   |
| ------------------ | ------------------------------------------------------- | --------------------- | ----------------------------------------------- |
| **规划输入层**          | 把需求压成可执行总图                                              | 方案设计文档、差距分析文档、单篇总任务文档 | `docs/design/`、`docs/gap/`、`docs/initiatives/`  |
| **执行宪法层**          | 规定对象、触发、Gate、Review、交付                                  | 你的三份 sealed 法典        | 仓库文档本体                                          |
| **Initiative 调度层** | 选择当前 Milestone frontier，组织 Workstream，决定下一批 Ready Tasks | 总任务文档 + Git/PR/CI 证据  | `run-initiative` 系列 skills + repo 脚本            |
| **Task 控制层**       | 控制单个 Task 的局部收敛、防熵增、防振荡，直到进入正式 Task 收口                  | 当前 Task packet + 运行事实 | `task-loop` 系列 skills + custom agents + repo 脚本 |

这里必须特别强调一条：**旧控制法现在只能叫 Task Controller 法，而不能再自称整个系统的唯一控制器**。因为 Initiative 级别的调度、Milestone frontier 推进、PR 节奏与交付断点，已经由上位执行模型和规划模型正式接管。

---

## 2. 最终架构图

```text
用户
  │
  ▼
$run-initiative <INIT_KEY>
  │
  ├── 读取单篇总任务文档
  ├── Planning Preflight
  ├── Rebuild Initiative State
  ├── 选择当前 Milestone Frontier
  ├── 按 Workstream / 依赖挑选 Ready Tasks
  │
  ├── 对每个 Ready Task 调用内部 task-loop
  │      ├── build task packet
  │      ├── sensor_primary
  │      ├── deterministic transition
  │      ├── task_worker patch/proof/escalate
  │      ├── READY_FOR_ANCHOR
  │      ├── cut anchor commit
  │      ├── G1
  │      └── R1
  │
  ├── 若当前 Milestone 收口：open/update PR → G2 → R2
  ├── 若达到 Initiative 交付候选：G3 → R3
  └── 仅在 Milestone、交付、跨层冲突处请求用户裁决
```

这套图的关键不是“多 agent”，而是**入口粒度与执行原子粒度分离**：

* 面向用户：Initiative-driven
* 面向调度：Milestone-oriented
* 面向执行：Task-atomic

---

## 3. 为什么最终选择 Skill 作为核心编排面

这条路线现在可以正式封板。

Codex 官方把 skills 定义为复用 workflow 与领域能力的主要承载体；skill 可以携带 instructions、optional scripts、references、assets，并支持显式 `$skill-name` 调用与基于 `description` 的隐式匹配。skills 可用在 CLI、IDE extension 与 Codex App；仓库内 skills 的标准扫描位置是 `.agents/skills`，从当前目录一直向上扫到 repo root。([OpenAI开发者][2])

OpenAI 自己在 Agents SDK 仓库的做法也与此一致：repo-local skills、`AGENTS.md` 与 GitHub Actions 被用来固化 verification、release preparation、integration testing 与 PR review；官方总结出的实践是，**`AGENTS.md` 决定哪些 workflow 是必需的，skills 承载 workflow，`scripts/` 负责确定性部分，模型负责上下文判断。**([OpenAI开发者][3])

因此，本方案对 Codex 的最终裁决是：

> **Skill 是 Profile Plane 的主承载物。**
> **Repo 脚本是 Execution Surface 的确定性内核。**
> **Custom agents 是模型角色面。**
> **AGENTS.md 是仓库治理法。**

不引入 MCP，不是因为 MCP 不行，而是因为你的目标明确是**更高内聚、更低部署摩擦、更少系统外部件**。在这个目标下，纯 Codex 原生四件套更合适：

* `AGENTS.md`
* `.codex/config.toml`
* `.codex/agents/*.toml`
* `.agents/skills/*`

---

## 4. 一个必须先钉死的工程约束

默认 `workspace-write + on-request approvals` 是 Codex 对 version-controlled 项目的推荐运行方式；同时，在默认 `workspace-write` 策略下，`.git`、`.agents/`、`.codex/` 都是递归只读保护路径。([OpenAI开发者][4])

这条约束直接决定了最终方案的目录法位：

### 4.1 可变与不可变必须分层

| 区域                  | 法位                 | 运行中是否允许写入 |
| ------------------- | ------------------ | --------- |
| `AGENTS.md`         | 仓库长期规则             | 默认不写      |
| `.codex/`           | 项目配置、custom agents | 默认不写      |
| `.agents/`          | skills、脚本、模板、规则资产  | 默认不写      |
| `docs/initiatives/` | 规划真理源              | 只通过治理变更修改 |
| 业务代码目录              | 交付对象               | 正常写入      |
| 运行时 cache 目录        | 临时派生状态             | 正常写入      |

### 4.2 这带来的正式裁决

> **`.codex/` 与 `.agents/` 是治理层，不是运行态。**
> **运行时状态绝不能落在这两个目录里。**

这反而是好事：系统不会在普通交付循环中偷偷改写自己的技能、配置与角色协议。

---

## 5. 仓库落地结构

下面这份目录结构就是推荐的正式实现，不再抽象。

```text
repo/
├─ AGENTS.md
├─ .codex/
│  ├─ config.toml
│  └─ agents/
│     ├─ sensor_primary.toml
│     ├─ task_worker.toml
│     ├─ task_reviewer.toml
│     ├─ architect.toml
│     ├─ closer.toml
│     └─ pragmatist.toml
├─ .agents/
│  ├─ skills/
│  │  ├─ run-initiative/
│  │  │  ├─ SKILL.md
│  │  │  ├─ agents/openai.yaml
│  │  │  ├─ scripts/
│  │  │  │  ├─ planning_preflight.py
│  │  │  │  ├─ rebuild_state.py
│  │  │  │  ├─ select_frontier.py
│  │  │  │  ├─ select_ready_tasks.py
│  │  │  │  └─ summarize_initiative.py
│  │  ├─ task-loop/
│  │  │  ├─ SKILL.md
│  │  │  ├─ agents/openai.yaml
│  │  │  └─ scripts/
│  │  │     ├─ build_task_packet.py
│  │  │     ├─ validate_observation.py
│  │  │     ├─ step_transition.py
│  │  │     ├─ collect_runtime_facts.py
│  │  │     └─ summarize_task_status.py
│  │  ├─ cut-anchor/
│  │  ├─ g1-task-gate/
│  │  ├─ r1-task-review/
│  │  ├─ open-milestone-pr/
│  │  ├─ g2-milestone-gate/
│  │  ├─ r2-milestone-review/
│  │  ├─ g3-initiative-gate/
│  │  ├─ r3-initiative-review/
│  │  ├─ shadow-check/
│  │  ├─ shadow-review/
│  │  └─ escalation-panel/
│  └─ lib/
│     ├─ planning_parser.py
│     ├─ state_model.py
│     ├─ transition_rules.py
│     ├─ review_packet.py
│     ├─ gate_runner.py
│     └─ report_render.py
├─ docs/
│  ├─ design/
│  ├─ gap/
│  └─ initiatives/
│     ├─ INIT-001.md
│     └─ INIT-002.md
├─ .initiative-runtime/
│  ├─ .gitignore
│  └─ <INIT_KEY>/
│     ├─ state.json
│     ├─ packets/
│     ├─ reports/
│     └─ facts/
└─ src/...
```

这套结构与 Codex 当前原生规则是兼容的：Codex 会在 repo 中扫描 `.agents/skills`；skills 目录支持 `SKILL.md`、`scripts/`、`references/`、`assets/`、`agents/openai.yaml`；project-scoped custom agents 放在 `.codex/agents/`；project-scoped config 放在 `.codex/config.toml`；`AGENTS.md` 会在会话开始前按 root-to-leaf 链式加载。([OpenAI开发者][2])

---

## 6. 真理源与运行态的正式分离

这部分必须理解透，否则后面会反复返工。

### 6.1 正式真理源

正式真理源只有三类：

| 类别           | 载体                                            |
| ------------ | --------------------------------------------- |
| **规划真理源**    | 方案设计文档、差距分析文档、单篇总任务文档                         |
| **工程真理源**    | 代码、结构化 commit、branch、PR、tag、release candidate |
| **验证与审查真理源** | G1/G2/G3 结果、R1/R2/R3 报告、PR review、真实环境验收记录    |

### 6.2 运行时 cache

`.initiative-runtime/` 只是**派生状态缓存**，不是正式真理源。

原因有两个：

第一，默认 delivery 模式下 `.codex/` 和 `.agents/` 不可写，所以运行态必须放到别处。第二，Codex App 的 Handoff 依赖 Git 操作，而 `.gitignore` 文件里的内容**不会**随着 thread handoff 在 Local 与 Worktree 间移动。([OpenAI开发者][4])

因此正式规定如下：

> **`.initiative-runtime/` 必须 gitignore。**
> **它可以丢。**
> **任何关键状态都必须可从总任务文档、Git 对象、PR 与验证证据重建。**

### 6.3 重建原则

每个正式入口 skill 的第一步都必须是：

```text
if runtime cache missing or stale:
    rebuild from canonical sources
```

也就是：

1. 解析总任务文档，得到 Milestone / Workstream / Task Ledger
2. 扫描 commit 历史中的 `anchor/fixup/revert` 结构化锚点
3. 扫描当前 branch / PR 对应关系
4. 读取最近的 gate / review / report 结果
5. 重建 Initiative / Milestone / Task 派生状态

这条规则解决了 three-way 问题：

* worktree handoff 丢失 gitignored cache
* 多 worktree / 多线程下 cache 不一致
* 运行中断后的可恢复性

---

## 7. 正式入口与内部入口

### 7.1 用户唯一主入口

终端用户只使用一个核心入口：

```text
$run-initiative <INIT_KEY>
```

它绑定的是**Initiative 总任务文档**，而不是某个 Task。

### 7.2 其他入口的法位

| 入口                                              | 法位                     | 是否用户主入口 |
| ----------------------------------------------- | ---------------------- | ------- |
| `$run-initiative`                               | Initiative runtime 主入口 | **是**   |
| `$advance-milestone`                            | 专家/恢复入口                | 否       |
| `$task-loop`                                    | 内部执行入口                 | 否       |
| `$cut-anchor`                                   | 内部 Task 收口入口           | 否       |
| `$g1-task-gate` / `$r1-task-review`             | 正式 Task 质量入口           | 否       |
| `$g2-milestone-gate` / `$r2-milestone-review`   | 阶段收敛入口                 | 否       |
| `$g3-initiative-gate` / `$r3-initiative-review` | 交付收口入口                 | 否       |
| `$shadow-check` / `$shadow-review`              | 后台预警入口                 | 否       |

最终用户的心智应被压缩为：

> “我启动一个 Initiative。系统持续推进。
> 只有在里程碑收口、跨层冲突、交付决策时才来找我。”

---

## 8. Initiative Runtime：正式主循环

这部分给出最终主循环，不再留空白。

### 8.1 `run-initiative` 的固定步骤

#### Step 1：Planning Preflight

检查总任务文档是否具备进入实施的合法输入质量：

* Design Refs 是否存在
* Gap Refs（如适用）是否存在
* Sealed Decisions 是否存在
* Initiative / Milestone / Task 字段是否齐全
* Milestone Reference Assignment 与 Initiative Reference Assignment 是否已唯一指派
* 是否仍存在未裁决问题

若失败，直接停止，返回：

```text
PLANNING_BLOCKED
```

#### Step 2：Rebuild Initiative State

按第 6 节规则，从正式真理源重建派生状态。

#### Step 3：Select Milestone Frontier

选择**最早的、尚未完成且依赖已满足**的 Milestone 作为当前 frontier。

#### Step 4：Expand Ready Tasks

在当前 frontier 内，根据 Workstream 与 Task dependencies 展开 Ready Tasks。

#### Step 5：Apply Parallelism Policy

* 读并行：允许 exploration、gap check、proof gathering、log analysis
* 写串行：同一 Milestone branch 上只允许一个写入型 Task 进入 patch 阶段

Codex 官方对 subagents 的建议与此一致：subagents 必须显式触发；更适合 read-heavy 的 exploration、tests、triage、summarization；对 parallel write-heavy workflow 要更谨慎，因为会增加冲突与协调成本。([OpenAI开发者][5])

#### Step 6：Run Internal Task Loops

对每个 Ready Task 调用内部 `task-loop`。
注意：这里不是把所有 task 全并行写，而是按上一步的并行策略调度。

#### Step 7：Update Frontier

完成一批 tasks 后，重新计算 Milestone frontier。

#### Step 8：Milestone Seal Check

若当前 Milestone 所需 tasks 全部完成，且无 unresolved escalation，则进入：

```text
READY_FOR_PR
```

随后触发：

* `open-milestone-pr`
* `g2-milestone-gate`
* `r2-milestone-review`

#### Step 9：Initiative Seal Check

若所有必需 Milestone 均成立，进入交付候选阶段，触发：

* `g3-initiative-gate`
* `r3-initiative-review`

#### Step 10：User Intervention Only at Formal Breakpoints

系统只在以下三类断点打断用户：

1. Milestone 收口与 PR 合入前
2. 跨层冲突升级
3. Initiative 交付候选形成

---

## 9. Task Loop：内部最小执行原子

### 9.1 核心判断

Task 不是用户入口，但仍然是内部最小闭环。
没有 Task-atomic，以下机制全部失去稳定基础：

* anchor commit
* G1 / R1
* 局部回滚
* fixup
* 差异归因
* 熵增抑制

### 9.2 `task-loop` 的固定步骤

```text
build packet
→ sensor_primary
→ deterministic transition
→ task_worker patch/proof/escalate
→ repeat
→ READY_FOR_ANCHOR
→ cut-anchor
→ G1
→ R1
→ mark task done / blocked / deferred
```

### 9.3 Packet 组成

`build_task_packet.py` 必须只装载当前 Task 所需最小输入：

* Task Definition
* Design Refs
* Gap Refs
* Spec-Refs
* 当前 diff / 相关文件
* 最近 runtime facts
* 当前 Task-local acceptance
* 当前 Task-local non-goals

禁止把整个 Initiative 对话历史、大量无关代码、无关日志一股脑塞进去。Codex 官方工作流文档明确强调：Codex 在“显式上下文 + 明确定义 done”的前提下效果最好；CLI 中通常还需要显式指明路径或提及文件。([OpenAI开发者][6])

### 9.4 Sensor 与 R1 的边界

这里再正式重复一次：

| 对象               | 法位           |
| ---------------- | ------------ |
| `sensor_primary` | Task 内部离散传感器 |
| `R1 Task Review` | 正式 Task 审查   |

前者只负责观测当前快照。
后者必须在 anchor commit 形成后，读取：

* 结构化 commit 文本
* G1 结果
* Spec-Refs
* commit diff
* 必要源码上下文

### 9.5 Task 终态修正

旧控制法中的 `PROCEED_TO_NEXT_TASK` 现正式废止。
Task loop 的最高正向终态必须改为：

```text
READY_FOR_ANCHOR
```

它的含义是：

> 当前 Task 的局部实现已经收敛，
> 可以进入正式 Task 收口，
> 但 Task 还没有被正式判定完成。

---

## 10. Skill 目录与职责表

skills 既然是主编排面，就必须一次性写清，不允许后续再长第二套路由体系。

### 10.1 MVP 必备 skill 集

| Skill                  | 法位                |          是否显式 | 核心输入                      | 核心输出                             |
| ---------------------- | ----------------- | ------------: | ------------------------- | -------------------------------- |
| `run-initiative`       | 主入口               |             是 | `INIT_KEY`                | 当前 Initiative 进展、下一批动作、需用户裁决点    |
| `planning-preflight`   | 规划准入              |             是 | Initiative doc            | preflight verdict                |
| `task-loop`            | 内部执行              |     否（由主入口调用） | `TASK_KEY`                | task status                      |
| `cut-anchor`           | Task 正式收口         |             否 | Task packet               | anchor commit                    |
| `g1-task-gate`         | Task gate         |             否 | anchor commit             | G1 result                        |
| `r1-task-review`       | Task review       |             否 | commit + G1 + refs        | R1 report                        |
| `open-milestone-pr`    | PR 收敛             |      是/由主入口调用 | `MILESTONE_KEY`           | PR draft / update                |
| `g2-milestone-gate`    | Milestone gate    |      是/由主入口调用 | PR / branch diff          | G2 result                        |
| `r2-milestone-review`  | Milestone review  |      是/由主入口调用 | PR + G2 + refs            | R2 report                        |
| `g3-initiative-gate`   | Initiative gate   |      是/由主入口调用 | release/rollout candidate | G3 result                        |
| `r3-initiative-review` | Initiative review |      是/由主入口调用 | G3 + completion matrix    | R3 report                        |
| `shadow-check`         | 预警校验              | 是（automation） | branch checkpoint         | green/yellow/red                 |
| `shadow-review`        | 预警审查              | 是（automation） | checkpoint + shadow check | green/yellow/red                 |
| `escalation-panel`     | 跨层升级              |             否 | escalation packet         | architect/closer/pragmatist 汇总结论 |

### 10.2 invocation policy

正式入口 skill 全部应在 `agents/openai.yaml` 中设为：

```yaml
policy:
  allow_implicit_invocation: false
```

因为你的上位法已经规定：**正式触发必须来自法定状态或法定事件，而不是模型“觉得现在差不多了”。**
Codex 官方也支持通过 `agents/openai.yaml` 关闭隐式触发，同时保留显式 `$skill-name` 调用。([OpenAI开发者][2])

### 10.3 helper skill

只有非正式辅助技能可以允许隐式触发，例如：

* docs helper
* log parser
* code map
* spec locator

---

## 11. Custom Agents：角色面最终定义

Codex 自带 `default`、`worker`、`explorer` 三个内建 agent；项目级 custom agents 放在 `.codex/agents/`，每个 TOML 文件至少定义 `name`、`description`、`developer_instructions`，其余模型、sandbox、skills 等配置可以继承父会话。([OpenAI开发者][7])

### 11.1 本方案的正式 agent 集

| Agent            | 角色本质      | 推荐 sandbox      | 推荐 reasoning         | 触发方式                           |
| ---------------- | --------- | --------------- | -------------------- | ------------------------------ |
| `sensor_primary` | 无状态离散传感器  | read-only       | high                 | 由 `task-loop` 显式调用             |
| `task_worker`    | 单决策执行器    | workspace-write | medium               | 由 `task-loop` 显式调用             |
| `task_reviewer`  | R1 正式审查器  | read-only       | high                 | 由 `r1-task-review` 调用          |
| `architect`      | 熵增/边界裁决   | read-only       | high                 | 由 `escalation-panel` / `r2` 调用 |
| `closer`         | 闭环/逆向路径裁决 | read-only       | high                 | 由 `escalation-panel` / `r2` 调用 |
| `pragmatist`     | 最小代价推进裁决  | read-only       | high                 | 由 `escalation-panel` / `r2` 调用 |
| `explorer`       | 大范围只读探索   | read-only       | default / low-medium | 由主线程显式 spawn                   |

### 11.2 使用原则

Codex 不会自动 spawn subagents，只有在你明确要求“spawn agents / parallelize / delegate”时才会创建 subagents；并且 subagent 会消耗额外 tokens 与工具调用成本。官方建议主 agent 保持对 requirements、decisions、final outputs 的专注，把 exploration、tests、triage、summarization 这类噪声较大的工作移到 subagents。([OpenAI开发者][5])

因此，本方案的正式用法是：

> **主线程负责 Initiative、Milestone、最终裁决。**
> **subagents 只处理 bounded、read-heavy、可并行的局部工作。**

---

## 12. `AGENTS.md` 的正式职责

Codex 会在开始工作前读取 `AGENTS.md`，并按 `~/.codex` → repo root → 当前目录的路径链构建 instructions chain；更近的目录后拼接，因此能覆盖更外层指导。官方明确建议 `AGENTS.md` 保持 small，并用来承载 build/test 命令、review expectations、repo-specific conventions 与 directory-specific instructions。([OpenAI开发者][8])

### 12.1 根 `AGENTS.md` 应只承载四类内容

1. 仓库级工作纪律
2. 交付模式与禁止事项
3. 正式 workflow 约束
4. review guidelines

### 12.2 推荐最小骨架

```md
# Repository Operating Law

## Default mode
- Work initiative-first.
- Bind every delivery run to one Initiative total-task document.
- Never skip formal G1/R1 and G2/R2 transitions.

## Governance boundaries
- Do not modify `.agents/`, `.codex/`, or repository governance assets during normal delivery runs.
- Changes to skills, custom agents, or config require a governance PR.

## Runtime discipline
- Treat `.initiative-runtime/` as rebuildable cache, not truth.
- Rebuild state from tracked sources when cache is missing or stale.

## Review guidelines
- Flag dual truth sources, shadow state, implicit fallback, no-exit compatibility logic, and leaky abstraction.
- Require Spec-Refs when contracts, fields, interfaces, migrations, or state transitions change.
```

### 12.3 目录级 `AGENTS.override.md`

对于 monorepo 中的 service/package，使用更近的 `AGENTS.override.md` 写局部 build/test/review 特殊规则，而不是在根文档里堆积例外。Codex 支持这种 fallback filename 与 root-to-leaf 覆盖链。([OpenAI开发者][8])

---

## 13. `.codex/config.toml` 的正式定位

项目级 config 是**共享默认值**，不是运行时状态仓。Codex 会在 trusted project 中加载 `.codex/config.toml`，并按 project root 到当前目录的顺序叠加，最近的配置覆盖更远的配置；CLI flags 与 profile 又高于 project config。([OpenAI开发者][9])

### 13.1 本方案建议的 delivery 默认值

* `sandbox_mode = "workspace-write"`
* `approval_policy = "on-request"`

这正是 Codex 对 version-controlled 项目的默认推荐模式。([OpenAI开发者][4])

### 13.2 推荐最小配置

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
project_root_markers = [".git"]
project_doc_fallback_filenames = ["AGENTS.override.md"]
```

### 13.3 关于模型

MVP 建议**不要在全局强 pin 模型**。
原因很简单：Codex 已支持根据任务在不同 agents 之间平衡智能、速度与成本；只有在某个 custom agent 上你明确需要更高一致性时，再在 agent file 中 pin `model` 与 `model_reasoning_effort`。官方文档也明确说明：不 pin 时 Codex 会自动平衡；需要更细粒度控制时，再在 agent file 中设置。([OpenAI开发者][5])

---

## 14. Formal Gate / Review 如何映射到 Codex

### 14.1 G1 / R1

* `cut-anchor` 生成结构化 anchor commit
* `g1-task-gate` 调用本地 gate stack
* `r1-task-review` 生成正式 Task Review report

### 14.2 G2 / R2

* `open-milestone-pr` 在 App 内或 Git 平台上创建/更新 PR
* `g2-milestone-gate` 运行 Milestone gate
* `r2-milestone-review` 读取 PR diff、Milestone Reference、G2 结果，产出正式阶段审查报告

### 14.3 G3 / R3

* `g3-initiative-gate` 面向 release / rollout / deployment candidate
* `r3-initiative-review` 面向 Initiative completion matrix、风险账本与交付证据

### 14.4 GitHub review 的法位

如果仓库接入 GitHub，Codex 原生支持在 PR 评论里使用 `@codex review`，也支持 Automatic reviews；GitHub review 会读取仓库中的 `AGENTS.md` Review guidelines，并按 changed file 就近应用更深层的 `AGENTS.md` 指导；在 GitHub 上，Codex 默认只标 P0/P1。([OpenAI开发者][10])

因此正式裁决如下：

> **GitHub Auto Review 是 R2 的辅助输入，不是 R2 本体。**
> **更不是 R3。**

它负责 PR 缺陷发现、补充证据与外层提醒；正式阶段裁决仍由 `r2-milestone-review` / `r3-initiative-review` 生成。

---

## 15. App / CLI / GitHub / Automations 的分工

### 15.1 App：主控制台

Codex App 是本方案的推荐主操作面，因为它原生支持：

* parallel threads
* worktrees
* automations
* built-in Git
* review pane
* 与 CLI/IDE 共用 skills

官方把 App 定义为“用于并行 threads、内置 worktree、automations、Git 的 focused desktop experience”。([OpenAI开发者][11])

### 15.2 CLI：专家入口

CLI 适合：

* 本地调试某个 skill
* 直接在 terminal 执行显式 workflow
* CI / script / shell 型实验
* 恢复或重放某个内部 step

### 15.3 GitHub：阶段集成与代码评审面

GitHub 适合：

* PR 容器
* `@codex review`
* Automatic reviews
* 外部 reviewer 协作
* 合并记录与发布记录

### 15.4 Automations：Shadow 层，不是 blocking 主链

Codex App 的 automations 能在后台运行，并可与 skills 组合；但它要求 App 保持运行、项目路径在本地可用。对于 Git repo，automation 可在 local project 或 dedicated background worktree 中运行。官方 best practices 明确提出：**skills define the method, automations define the schedule**。([OpenAI开发者][12])

因此本方案正式规定：

| 层                            | 运行位置             |
| ---------------------------- | ---------------- |
| G1/G2/G3                     | 显式同步触发           |
| R1/R2/R3                     | 显式同步触发           |
| Shadow Check / Shadow Review | Automations 后台触发 |

---

## 16. Worktrees 与并行策略

Codex App 的 worktree 能让同一项目中的多个独立任务并行而不互相干扰；automations 默认也可跑在 dedicated background worktree。Worktree 支持 Handoff 在 Local 与 Worktree 间迁移 thread，但要注意两条 Git 约束：**同一 branch 不能在多个 worktree 同时 checkout；`.gitignore` 里的文件不会随着 Handoff 一起移动。**([OpenAI开发者][13])

### 16.1 本方案的正式并行法

| 类型                 | 策略                                       |
| ------------------ | ---------------------------------------- |
| **Initiative 级并行** | 允许多个 Initiative 各自占用独立 thread / worktree |
| **Workstream 级并行** | 允许只读探索、审查、验证前置并行                         |
| **Milestone 内写入**  | 默认串行                                     |
| **同一 branch**      | 禁止在多个 worktree 同时作为写分支                   |

### 16.2 Handoff 法则

> **Handoff 用于前后台切换，不用于规避 branch 冲突。**
> **任何 gitignored runtime cache 都必须可重建。**

---

## 17. Review Pane 与用户体验

Codex App 的 review pane 可以展示 uncommitted diff、branch diff、last-turn diff，并允许：

* inline comments
* stage / unstage / revert at file/hunk level
* 读取 `/review` 结果的 inline comments

它只基于 Git 仓库工作。([OpenAI开发者][14])

这直接对应本方案的用户体验目标：

> 用户不需要盯住每个 Task。
> 用户主要在 Milestone 收口、PR 差异收敛、R2/R3 报告处进行裁决。
> review pane 就是这些裁决的主要交互面。

---

## 18. 正式运行状态模型

### 18.1 Initiative State

| 状态                   | 含义                                   |
| -------------------- | ------------------------------------ |
| `PLANNING_BLOCKED`   | 总任务文档不合法，不能进入实施                      |
| `READY`              | 规划输入合法，尚未开跑                          |
| `ACTIVE`             | 当前有 frontier Milestone 正在推进          |
| `WAITING_R2`         | 当前 Milestone 已具备收口条件，等待 G2/R2 / 用户裁决 |
| `WAITING_ESCALATION` | 存在跨层冲突，等待升级裁决                        |
| `WAITING_R3`         | Initiative 交付候选形成，等待 G3/R3 / 用户裁决    |
| `DONE`               | Initiative 正式完成                      |
| `ABORTED`            | Initiative 被取消或回退到规划阶段               |

### 18.2 Milestone State

| 状态             | 含义                     |
| -------------- | ---------------------- |
| `NOT_READY`    | 依赖未满足                  |
| `READY`        | 可进入当前 frontier         |
| `ACTIVE`       | 正在推进                   |
| `READY_FOR_PR` | Task 级收口完成，可开/更新 PR    |
| `IN_R2`        | 正在进行 G2 / R2           |
| `MERGED`       | 合入主干，阶段成立              |
| `BLOCKED`      | 被 escalation 或 gate 拦截 |

### 18.3 Task State

| 状态                 | 含义                           |
| ------------------ | ---------------------------- |
| `NOT_READY`        | 依赖未满足                        |
| `READY`            | 可进入 task-loop                |
| `IN_FLIGHT`        | 正在 task-loop                 |
| `READY_FOR_ANCHOR` | 内部收敛完成，可进入正式 Task 收口         |
| `IN_G1`            | 正在 Task Gate                 |
| `IN_R1`            | 正在 Task Review               |
| `DONE`             | Task 正式完成                    |
| `BLOCKED`          | 当前 task 被阻断                  |
| `DEFERRED`         | 延后到后续 Milestone / Initiative |

---

## 19. 实施序列：可直接开工的 PR 规划

下面给出最短可落地、又不破坏法位的实施序列。

### 19.1 并行作战线

| 作战线   | 目标                                                    | 推荐执行者          |
| ----- | ----------------------------------------------------- | -------------- |
| **A** | 治理骨架：`AGENTS.md`、`.codex/config.toml`、`.codex/agents` | Agent-A + User |
| **B** | 规划输入层：总任务文档模板、parser、preflight                        | Agent-B        |
| **C** | Initiative / Task runtime 脚本与状态重建                     | Agent-C        |
| **D** | skills 编排层                                            | Agent-D        |
| **E** | Gate / Review 报告模板                                    | Agent-E        |
| **F** | App / GitHub / Automations 接入                         | Agent-F        |

### 19.2 PR 序列与依赖

| PR      | 依赖  | 内容                                                        | 验收清单                                                            |
| ------- | --- | --------------------------------------------------------- | --------------------------------------------------------------- |
| **PR1** | 无   | 根 `AGENTS.md`、`.codex/config.toml`、custom agents 骨架       | Codex 能读取项目级 config；agents 能被识别；delivery 模式下不修改治理目录             |
| **PR2** | PR1 | 总任务文档模板、parser、planning preflight                         | 能对一个 Initiative 文档做完整字段校验；未裁决问题会被拦截                             |
| **PR3** | PR2 | `run-initiative` + `rebuild_state` + frontier 选择          | 能从总任务文档与 commit 历史重建派生状态                                        |
| **PR4** | PR3 | `task-loop` + `sensor_primary` + deterministic transition | Task 能推进到 `READY_FOR_ANCHOR`；跨层冲突能升级                            |
| **PR5** | PR4 | `cut-anchor` + `g1-task-gate` + `r1-task-review`          | 单个 Task 能形成 anchor → G1 → R1 正式闭环                               |
| **PR6** | PR5 | `open-milestone-pr` + `g2` + `r2`                         | 单个 Milestone 能进入 PR 收口                                          |
| **PR7** | PR6 | `g3` + `r3` + Initiative completion report                | Initiative 能完成正式交付收口                                            |
| **PR8** | PR3 | Shadow automations + reports                              | push 后能生成 green/yellow/red 预警结果                                 |
| **PR9** | PR6 | GitHub review 接入与 PR 协议                                   | `@codex review`、Automatic reviews、AGENTS Review guidelines 正常协同 |

### 19.3 每个 PR 的形式要求

* 每个 PR 只做一个闭环
* 每个 PR 必须有验收清单
* 每个 PR 必须有最小可验证路径
* 任何治理资产变更必须走专门治理 PR，不混入普通 delivery PR

---

## 20. Minimal Governance Templates

### 20.1 `sensor_primary.toml`

```toml
name = "sensor_primary"
description = "Stateless discrete sensor for Task snapshots. Output strict JSON only."
sandbox_mode = "read-only"
developer_instructions = """
You are a stateless discrete sensor.
Only observe the current Task snapshot.
Never compute trend, convergence, or milestone/initiative progress.
Output strict JSON only.
"""
```

### 20.2 `run-initiative/SKILL.md`

```md
---
name: run-initiative
description: Run one Initiative from its total-task document, advancing the current milestone frontier and delegating internal task loops.
---

1. Validate planning input with `planning_preflight.py`.
2. Rebuild initiative runtime state if cache is missing or stale.
3. Select the current milestone frontier.
4. Select ready tasks by dependency and workstream.
5. Apply read-parallel / write-serial policy.
6. For each selected task, invoke the internal task loop.
7. If the current milestone is sealable, open or update the milestone PR and run G2/R2.
8. If the initiative is deliverable, run G3/R3.
9. Only request user intervention at milestone, escalation, or delivery breakpoints.
```

### 20.3 `run-initiative/agents/openai.yaml`

```yaml
policy:
  allow_implicit_invocation: false
```

---

## 21. 正式禁止事项

### 21.1 入口层

* 禁止把 Task 作为终端用户主入口
* 禁止让用户手动挑下一个 Task 作为常态
* 禁止让自然语言需求直接绕过总任务文档进入执行

### 21.2 真理源层

* 禁止把 `.initiative-runtime/` 当唯一真理源
* 禁止把 `.codex/` 或 `.agents/` 当运行时状态目录
* 禁止让 gitignored cache 决定正式放行

### 21.3 编排层

* 禁止让正式 Gate / Review 依赖隐式 skill 路由
* 禁止让 subagents 自发创建写入型并行 swarm
* 禁止让 GitHub auto review 冒充 R2 或 R3

### 21.4 交付层

* 禁止在普通 delivery run 中修改 `.codex/`、`.agents/`、根治理规则
* 禁止没有 anchor commit 就进入 G1 / R1
* 禁止没有 Milestone Reference 就进入 G2 / R2
* 禁止没有 Initiative Reference 就进入 G3 / R3

---

## 22. 用户、Codex、真实环境的责任边界

### 用户负责

* 封板方案设计与差距分析
* 封板单篇总任务文档
* 设定 acceptance threshold 与 rollout boundary
* 真实环境手测、灰度、回滚、最终合入、最终发布
* 任何治理资产变更的批准

### Codex 负责

* Initiative 调度
* Task 内实现与修补
* 结构化 anchor commit
* G1/G2/G3 的本地执行编排
* R1/R2/R3 报告草拟
* PR 草稿、diff 整理、shadow 预警

### 共享责任

* 重大风险降级
* Milestone 收口判断
* Initiative 是否进入交付候选

---

## 23. 最终推荐的操作方式

### 日常主路径

1. 在 Codex App 中打开项目
2. 选择合适的 project scope
3. 在工作目录下启动：

```text
$run-initiative INIT-001
```

4. 让系统自动推进当前 frontier
5. 在 Milestone 收口时使用 App review pane 与正式 R2 报告做裁决
6. 若接入 GitHub，则在 PR 上启用 Automatic reviews，必要时用 `@codex review` 请求补充视角
7. 到交付阶段触发 G3 / R3，再进行真实环境验证与最终放行

### 后台预警

* 在 Codex App Automations 中配置：

  * `$shadow-check INIT-001`
  * `$shadow-review INIT-001`

Automations 与 skills 可组合使用，适合跑定时、非阻断、可重复的分析类 workflow；但它们要求 App 保持运行，并且项目路径在本地可用。([OpenAI开发者][12])

---

## 24. 一句话收口

> **这套最终方案不是“让 Codex 自动写很多代码”。**
> **它是让 Codex 在一份单篇总任务文档的约束下，以 Initiative 为用户入口、以 Milestone 为收敛边界、以 Task 为内部原子，持续推进一个大专项，并把每一次推进都收敛到可验证、可审查、可合入、可交付的正式结构内。**

如果你按这份文档落地，MVP 的第一步不是继续争论理念，而是直接开 **PR1：治理骨架 + custom agents + skills 目录 + planning preflight**。

[1]: https://developers.openai.com/codex/concepts/customization/ "https://developers.openai.com/codex/concepts/customization/"
[2]: https://developers.openai.com/codex/skills/ "https://developers.openai.com/codex/skills/"
[3]: https://developers.openai.com/blog/skills-agents-sdk/ "https://developers.openai.com/blog/skills-agents-sdk/"
[4]: https://developers.openai.com/codex/agent-approvals-security/ "https://developers.openai.com/codex/agent-approvals-security/"
[5]: https://developers.openai.com/codex/concepts/multi-agents/ "https://developers.openai.com/codex/concepts/multi-agents/"
[6]: https://developers.openai.com/codex/workflows/ "https://developers.openai.com/codex/workflows/"
[7]: https://developers.openai.com/codex/subagents/ "https://developers.openai.com/codex/subagents/"
[8]: https://developers.openai.com/codex/guides/agents-md/ "https://developers.openai.com/codex/guides/agents-md/"
[9]: https://developers.openai.com/codex/config-basic/ "https://developers.openai.com/codex/config-basic/"
[10]: https://developers.openai.com/codex/integrations/github/ "https://developers.openai.com/codex/integrations/github/"
[11]: https://developers.openai.com/codex/app/ "https://developers.openai.com/codex/app/"
[12]: https://developers.openai.com/codex/app/automations/ "https://developers.openai.com/codex/app/automations/"
[13]: https://developers.openai.com/codex/app/worktrees/ "https://developers.openai.com/codex/app/worktrees/"
[14]: https://developers.openai.com/codex/app/review/ "https://developers.openai.com/codex/app/review/"
