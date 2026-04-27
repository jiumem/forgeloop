# Forgeloop

Forgeloop 是一个面向 Codex 的轻量级 Agent 编程工作流插件。它的目标不是替代工程师，也不是把项目管理工具搬进代码仓库，而是把一次软件专项从「下一步做什么」到「如何规划」再到「如何逐阶段交付」压缩成一套清晰、可复用、可审查的流程。

Forgeloop 2.0 的核心判断是：随着大模型的代码理解、规划和审查能力增强，工作流不应该再依赖冗长的提示词、复杂的文档 anchor、繁重的 gate 体系或多层运行态状态机。更有效的方式是保留少量硬边界：以 Initiative 作为用户入口，以 Milestone 作为交付单元，以 Git 作为证据锚点，以 Reviewer 裁决作为推进条件，以极简 `LEDGER.md` 作为恢复记录。

## 为什么创建 Forgeloop

在真实的 Agent 编程场景里，常见问题通常不是「模型不会写代码」，而是：

- 用户不知道当前项目下一步最值得做什么；
- 需求被直接丢给代码 Agent，缺少可执行的阶段计划；
- 实现完成后没有稳定的审查协议，容易把 build 通过、commit、push 或截图打包误当成验收；
- UI、Schema、测试、架构边界等问题经常在最后才暴露；
- 会话中断后很难恢复到正确的执行位置；
- 多 Agent 协作时，Coder、Reviewer、Scheduler 的职责边界容易混在一起。

Forgeloop 解决的是这些「执行收敛」问题。它让 Codex 在项目中按一个简单流程工作：先推荐专项，再写计划，最后按里程碑推进，每个里程碑都由 Coder 交付、Reviewer 审查，只有 Reviewer 明确 `PASS` 才进入下一阶段。

## 核心模型

### Initiative 是用户入口

Initiative 表示一次完整目标闭环，例如一个 UI 专项、一个组件库改造、一个 Schema 治理、一个测试加固专项。用户通常会说「按这个 PLAN 执行这个专项」或「看看这个项目接下来最该做哪些专项」。

### Milestone 是交付单元

Forgeloop 2.0 不再默认以 Task 作为调度单元。Task 可以作为 Coder 的内部施工分解存在，但 Scheduler 只按 Milestone 推进。

一个好的 Milestone 通常包含 3 到 5 个 Work Items，并且必须有明确的验收标准、验证方式和 Reviewer 关注点。一个 Initiative 通常建议 3 到 8 个 Milestone，不建议超过 10 个。对于重要或高风险业务能力，可以在功能 Milestone 后增加一个 Acceptance & Hardening Milestone，专门用于验收、测试补强、架构整理、大文件拆分和第二路径清理。

### Reviewer 是质量核心

Forgeloop 不强制维护一套复杂 gate 系统。现代代码 Agent 通常已经会主动运行类型检查、测试、构建和截图确认。Forgeloop 真正强调的是 Reviewer 协议。

Reviewer 必须从三个角度审查 Milestone：

1. 产品经理角度：功能是否真的可用，用户路径是否成立，关键状态是否覆盖；
2. 测试工程师角度：测试和验证是否真实覆盖验收标准，有没有浅层 smoke test、弱断言、跳过测试或伪验证；
3. 架构师角度：核心 Schema 变更是否合理，大文件是否需要拆分，是否出现第二路径、重复状态、重复 schema、影子逻辑或错误的模块边界。

Reviewer 最终只能给出：

```text
PASS
REPAIR_REQUIRED
```

只有 `PASS` 才能推进下一个 Milestone。

### Git 是证据，不是放行

Commit 和 push 用于记录差异、形成恢复点、支持审查和回滚。它们不是完成证明，也不是阶段放行信号。

Forgeloop 的推进条件是 Reviewer `PASS`，不是：

- 代码已经 commit；
- 分支已经 push；
- build 通过；
- 测试通过；
- zip 已经打包；
- Coder 自己说完成。

## 三个技能入口

Forgeloop 只暴露三个核心技能。

### 1. `recommend-initiatives`

基于当前源码基线，推荐后续最值得做的 3 到 5 个专项序列。

它会查看项目结构、文档、测试、关键源码区域和已有 initiative 记录，然后按产品价值、工程杠杆、风险降低和执行就绪度排序。它不会开始编码，也不会为每个候选专项写完整 PLAN。

常见用法：

```text
请使用 Forgeloop 看一下当前项目源码基线，推荐接下来最值得做的 3-5 个专项。
```

输出通常写入：

```text
docs/initiatives/recommendations/<date>-<topic>.md
```

### 2. `write-plan`

把用户选中的专项或需求写成可执行的 `PLAN.md`。

`PLAN.md` 是 `run-initiative` 消费的唯一规划契约。Design 文档、ADR、Gap 文档、审计文档和用户需求都只是参考输入，不是 Forgeloop 生命周期对象。

常见用法：

```text
请使用 Forgeloop 为这个专项写一份 PLAN.md，后续要按里程碑执行。
```

输出通常写入：

```text
docs/initiatives/active/<initiative-slug>/PLAN.md
docs/initiatives/active/<initiative-slug>/LEDGER.md
```

### 3. `run-initiative`

按 `PLAN.md` 执行一个 Initiative。执行过程以 Milestone 为单位，每个 Milestone 都经过 Coder 交付和 Reviewer 审查。

常见用法：

```text
请使用 Forgeloop 执行 docs/initiatives/active/<initiative-slug>/PLAN.md，一直推进到专项完成。
```

推荐执行流：

```text
读取 PLAN.md 和 LEDGER.md
确认或创建分支 codex/<initiative-slug>
定位第一个非 PASS Milestone
给 Coder 发送自包含任务包
Coder 读文档、实现、验证、截图、commit、push
Scheduler 更新 LEDGER.md 到 REVIEW
给 Reviewer 发送自包含审查包
Reviewer 从产品、测试、架构三视角审查真实 diff
REPAIR_REQUIRED 则回到 Coder 修复
PASS 则记录 verdict 并进入下一个 Milestone
全部 Milestone PASS 后跑最终验证
写 DELIVERY.md，准备 PR summary，移动到 completed/
```

## 运行时存储结构

Forgeloop 的插件代码和项目运行记录是分开的。

插件代码位于：

```text
plugins/forgeloop/
```

项目实例数据由技能在目标仓库中按需创建：

```text
docs/initiatives/
  recommendations/
    <date>-<topic>.md
  active/
    <initiative-slug>/
      PLAN.md
      LEDGER.md
      evidence/
  completed/
    <initiative-slug>/
      PLAN.md
      LEDGER.md
      DELIVERY.md
      evidence/
  archived/
    <initiative-slug>/
```

其中：

- `PLAN.md` 是执行规划契约；
- `LEDGER.md` 是极简恢复账本；
- `evidence/` 存放可选截图、验证记录和审查证据；
- `DELIVERY.md` 是完成后的交付摘要和 PR summary 基础；
- recommendation 文件只是推荐快照，不是执行契约。

## 安装

Forgeloop 是 repo-local Codex plugin，不是 Python 包，也不需要 npm/pnpm 安装。

### 方式一：直接使用本仓库

1. 将本仓库 clone 或下载到本地。
2. 确认仓库根目录包含：

```text
.agents/plugins/marketplace.json
plugins/forgeloop/.codex-plugin/plugin.json
plugins/forgeloop/skills/
```

3. 重启 Codex，让 Codex 重新读取 repo-local marketplace。
4. 在 Codex 的插件界面中安装 `Forgeloop Local` / `forgeloop`。

### 方式二：复制到已有项目

如果你想把 Forgeloop 作为某个项目的本地插件，可以复制以下内容到项目根目录：

```text
.agents/plugins/marketplace.json
plugins/forgeloop/
```

然后重启 Codex 并安装该 repo-local plugin。

## 目录结构

本仓库刻意保持极简，只保留插件核心和 README：

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── plugins/
│   └── forgeloop/
│       ├── .codex-plugin/
│       │   └── plugin.json
│       └── skills/
│           ├── recommend-initiatives/
│           ├── write-plan/
│           └── run-initiative/
├── LICENSE
└── README.md
```

没有保留开发过程中的专项记录、封板 evidence、测试脚本、旧版 anchor 机制、旧版 custom agent manifests 或历史运行态控制面。

## 常见用法示例

### 推荐后续专项

```text
请使用 Forgeloop 基于当前源码基线推荐后续 3-5 个最值得做的专项序列。
```

适合在你刚接手一个项目、完成一个版本、或者想让 Agent 帮你判断下一步优先级时使用。

### 为选中的专项写 PLAN

```text
请使用 Forgeloop 为「组件库 Studio v1」写一份 PLAN.md。以 Milestone 为交付单元，每个 Milestone 3-5 个 Work Items，重要功能后加验收与加固 Milestone。
```

适合在你已经知道要做什么，但还没有形成可执行结构时使用。

### 按 PLAN 执行专项

```text
请使用 Forgeloop 执行 docs/initiatives/active/component-studio-v1/PLAN.md。复用一个 Coder subagent 和一个 Reviewer subagent，不要把调度者上下文 fork 给 subagent。每个 Milestone 完成后 commit/push，Reviewer PASS 后继续下一个 Milestone。
```

适合直接进入编码交付阶段。

### 恢复中断的专项

```text
请使用 Forgeloop 恢复 docs/initiatives/active/component-studio-v1/ 的执行，从 LEDGER.md 里第一个非 PASS Milestone 继续。
```

Forgeloop 会读取 `PLAN.md`、`LEDGER.md`、`git status` 和最近提交，而不是依赖聊天记忆。

### 只做审查导向的修复循环

```text
请使用 Forgeloop 继续当前 Initiative。上一轮 Reviewer 给了 REPAIR_REQUIRED，只修复 blocking issues，修复后重新 review。
```

适合在 Milestone 审查未通过时继续推进。

## Subagent 使用方式

Forgeloop 2.0 不内置 custom agent TOML。Coder 和 Reviewer 由 `run-initiative` 技能中的任务包定义：

```text
plugins/forgeloop/skills/run-initiative/references/coder-packet.md
plugins/forgeloop/skills/run-initiative/references/reviewer-packet.md
```

在支持 subagent 的 Codex 环境中，推荐使用通用 subagent：

- Coder：`default` 或 `worker`，高 reasoning effort；
- Reviewer：`default`，高 reasoning effort；
- `fork_context=false`；
- 每个 Initiative 尽量复用同一个 Coder 和同一个 Reviewer；
- `task_name` 使用 snake-normalized 名称，例如 `saaskit-ui-v1` 对应 `coder_saaskit_ui_v1` 和 `reviewer_saaskit_ui_v1`。

如果当前环境没有 subagent 工具，Scheduler 可以在用户允许的情况下继续执行，但必须把 review provenance 明确记录为 `explicit solo best-effort`，不得伪称已经由 subagent Reviewer 放行。

## 适合与不适合的场景

适合：

- UI 专项；
- 组件库或设计系统改造；
- 文档站、demo、studio 类项目；
- Schema / registry / API 契约治理；
- 测试真实性与架构加固；
- 已有需求，需要压成 PLAN 并持续交付的工程工作。

不适合：

- 一次性脚本；
- 极小 bug 修复；
- 不需要计划、不需要审查的临时实验；
- 需要严格组织级合规流程但不允许 Agent 参与审查的项目。

## 设计原则

Forgeloop 遵循几个原则：

1. 入口少：只保留 `recommend-initiatives`、`write-plan`、`run-initiative`。
2. 热路径短：默认不引入旧版文档 anchor、spec slice、复杂 gate 或多层运行态控制面。
3. 交付单元清楚：用户入口是 Initiative，执行推进靠 Milestone。
4. 审查协议强：Reviewer 的三视角裁决比形式化 gate 更重要。
5. 状态极简：恢复只依赖 `PLAN.md`、`LEDGER.md`、Git 和必要 evidence。
6. Git 不冒充验收：commit / push 只是证据和恢复点，不是放行。
7. 文档只保留执行价值：Design、ADR、Gap、Audit 是参考输入，不是生命周期对象。

## 许可证

MIT. See [LICENSE](LICENSE).
