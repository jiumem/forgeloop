# Forgeloop 中文手册

Forgeloop 是一套面向 Codex 的 Tracker 驱动交付插件。它不替代 Codex，也不建立第二套项目管理系统；它把需求澄清、Spec、Ticket、实现、审查、验证和集成组织成一条可恢复的工程交付路径。

> 当前版本：`4.3.0` · 20 个正式 Skill · 11 个用户入口 · 9 个模型可调用能力

[快速开始](README.md) · [4.3.0 发布说明](docs/releases/4.3.0-release-notes.md) · [4.2.1 → 4.3.0 迁移指南](docs/migrations/4.2.1-to-4.3.0.md)

## 目录

- [架构原则](#架构原则)
- [安装](#安装)
- [初始化项目](#初始化项目)
- [三条常用路径](#三条常用路径)
- [20 个正式 Skill](#20-个正式-skill)
- [run-initiative 如何闭环](#run-initiative-如何闭环)
- [状态、暂停与恢复](#状态暂停与恢复)
- [Tracker 与持久化](#tracker-与持久化)
- [从 4.2.1 升级到 4.3.0](#从-421-升级到-430)
- [维护与验证](#维护与验证)

## 架构原则

### 一份事实，一个归属

| 事实 | 唯一来源 | Forgeloop 的边界 |
| --- | --- | --- |
| Spec、Ticket、依赖和交付证据 | Tracker | 读写正式工作项，不维护平行计划账本 |
| 分支、提交、PR、检查和合并 | Git 与托管平台 | 验证真实提交状态，不把 Tracker 文本当作 Git 状态 |
| 行为与质量 | 代码和测试 | 以可执行证据判断，不以描述代替验证 |
| 术语与架构决策 | 项目上下文文档与 ADR | 按需维护，不为流程预建空文档 |

Forgeloop 不维护 `PLAN.md`、`LEDGER.md` 或同义的第二状态系统。Review 报告与 Finding 处置使用 Tracker 既有 Comment/Note/记录面持久化；它们是恢复证据，不是新的 Event、Verdict 或状态机。

### 一个 Delivery Worker 负责到底

`run-initiative` 的主任务是唯一 Delivery Worker。它负责读取契约、规划 Slice、编辑代码、维护分支和 Commit、判断 Review Findings、运行最终 Gate、提交 PR 并按仓库策略完成集成。

它不会再创建独立 Supervisor 或 Coder 子任务。只有 Spec Reviewer 和 Standards Reviewer 作为隔离、只读子任务存在，并且每条交付分支只运行一次双轴 Review。

### 检查完整，报告克制

双轴 Review 遵循两层取向：

- 检查面必须完整。Reviewer 要覆盖冻结范围、批准的 Spec、仓库规范、成功与失败路径、边界交互和证据可信度，不能为了省字漏掉真实问题。
- Finding 出口必须狭窄。纯命名或格式偏好、没有当前风险的 smell、工具已可靠覆盖的问题、推测性加固，以及当前批准产品模型之外的未来规模或拓扑都不报告。

因此 4.3.0 不再限制 Reviewer 报告为 400 字以内，也不靠 Finding 数量或字数控制成本。干净报告是合法结果；技术深度只有在证明当前变更的具体后果时才有价值。

## 安装

### 前置条件

- 支持插件的 Codex 客户端。
- 目标项目使用 Git。
- GitHub Tracker 使用已登录的 `gh`；GitLab Tracker 使用已登录的 `glab`；Local Tracker 不需要远端账号。
- Python 3 只用于维护者运行验证脚本，不是日常调用 Skill 的前置条件。

### 从本仓库安装

本仓库通过 [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) 声明 Repo-local Marketplace，插件源码位于 [`plugins/forgeloop`](plugins/forgeloop)。

1. 克隆仓库，并在 Codex 中打开仓库根目录。
2. 在 Codex 中打开 `/plugins`。
3. 在 `forgeloop-local` Marketplace 中选择 `forgeloop` 并安装。
4. 新建一个 Codex 任务，使插件在新任务中加载。

如果本地 Marketplace 没有出现，先确认 Codex 打开的目录就是仓库根目录，并且 `.agents/plugins/marketplace.json` 可见。不要手工复制单个 Skill 目录；插件清单、元数据和 Skills 必须保持同一版本。

Codex 官方说明：[插件安装与使用](https://developers.openai.com/learn/developers-codex-plugin)。

## 初始化项目

安装后，在目标项目的新任务中显式调用：

```text
$setup-forgeloop
```

初始化会确认四类契约：

1. Tracker：GitHub、GitLab 或 Local。
2. Integration Policy：分支、PR、检查与合并边界。
3. Triage 标签：安装了 `triage` 时确认标签词表。
4. 项目上下文：领域文档位置和必要的工作约定。

项目中的 `docs/agents/issue-tracker.md` 记录接入契约与操作方式，不是另一套 Issue 数据库。

## 三条常用路径

### 路径一：目标已经澄清，正式交付

```text
$to-spec 把这份已澄清需求写成正式 Spec
$to-tickets 把该 Spec 拆成可验证的 Tickets
$run-initiative 执行这个 Spec
```

`to-spec` 负责把已解决的上下文写成可验收契约。`to-tickets` 把 Spec 拆成最小、可观察的纵向结果；这些 Tickets 在执行时成为同一 Spec 分支上的实现 Slices，而不是独立分支、Review、Gate 和 PR。

多个 Ticket、实现会话或 Reviewer 必须共享一组系统设计决定时，`grill-with-docs` 负责创建或原位修订正式 Design Document。`to-spec` 保存稳定引用，`to-tickets` 不把共享决定复制到每张 Ticket。

### 路径二：目标模糊，先做发现

- `$wayfinder`：不知道下一步最值得做什么。
- `$recommend-initiatives`：希望从当前代码库提出 1–3 个候选 Initiative。
- `$grill-with-docs`：已经有方案，希望结合项目文档进行压力测试。
- `$improve-codebase-architecture`：希望发现并设计架构改进机会。

探索得到明确结论后再进入 `to-spec`。不要把研究、争论和范围发现延迟到执行阶段。

### 路径三：已有变更或故障

- `$spec-standards-review`：从预期行为与仓库规范两轴审查范围明确的已实现代码。
- `$diagnosing-bugs`：定位复杂 Bug、失败或性能退化的根因。
- `$triage`：整理待办、故障或反馈并决定下一步。
- `$handoff`：把当前工作压缩成另一个任务可以继续的交接包。

## 20 个正式 Skill

### 仅用户调用的 Workflow（11）

| Skill | 合适的触发场景 |
| --- | --- |
| `setup-forgeloop` | 为项目初始化或修复 Forgeloop 配置 |
| `ask-forgeloop` | 查询项目当前的 Forgeloop 配置、状态或用法 |
| `recommend-initiatives` | 从代码库提出 1–3 个值得推进的 Initiative |
| `improve-codebase-architecture` | 发现并设计一项架构改进 |
| `grill-with-docs` | 结合仓库文档拷打一个计划或设计 |
| `wayfinder` | 当前方向不明确，需要找到下一步 |
| `to-spec` | 把已经澄清的上下文固化为正式 Spec |
| `to-tickets` | 把 Spec 拆为最小、可观察的 Tickets |
| `run-initiative` | 交付一个大 Ticket、正式 Spec 或有界 Initiative |
| `triage` | 对工作项、问题或反馈进行分诊 |
| `handoff` | 为另一个 Codex 任务生成可继续的交接上下文 |

这些入口必须显式调用，不应因为普通任务描述自动注入。

### 模型可调用的完整 Workflow（2）

| Skill | 合适的触发场景 |
| --- | --- |
| `spec-standards-review` | 从预期行为与仓库规范两轴审查范围明确的已实现代码 |
| `diagnosing-bugs` | 诊断故障、异常、失败或性能回退 |

### 模型可调用的 Primitive（7）

| Skill | 合适的触发场景 |
| --- | --- |
| `grilling` | 对计划或设计进行高强度追问 |
| `domain-modeling` | 澄清领域语言、模型边界或架构决策 |
| `primary-source-research` | 基于高可信一手来源完成研究 |
| `prototype` | 用可丢弃原型回答设计问题 |
| `tdd` | 以测试驱动方式实现功能或修复 Bug |
| `codebase-design` | 设计深模块、接口与可测试边界 |
| `resolving-merge-conflicts` | 在恢复双方意图后解决合并或变基冲突 |

## run-initiative 如何闭环

### 支持的交付形态

`run-initiative` 每次选择且只选择一种形态：

- 大 Ticket：Ticket 本身达到 Spec 级复杂度，需要多个连贯 Slices。整个 Ticket 使用一个分支、一次 Review、一个最终 Gate 和一个 PR。
- Spec：Spec 的 Tickets 直接成为实现 Slices。整个 Spec 使用一个分支；每个 Ticket 在 Review 前对应一个完整逻辑 Commit，或一条 `NO_CHANGE_REQUIRED` 证据。
- 有界 Initiative：由多个 Specs 组成，但不能包含另一个 Initiative。每个 Spec 独立使用一个分支和一个 PR，并按依赖顺序交付；整个 Initiative 复用同一对 Reviewer 子任务。

小 Ticket 不走这个 Workflow。一个现有 Seam、没有新增状态或事实源、没有权限/迁移/兼容/恢复语义，并且一个窄验证即可观察结果的改动，应直接实现。多个 Initiatives 也不能合并成一次运行。

### 单分支快速实现

```text
读取 Tracker、契约与 Git
        ↓
Delivery Worker 规划 Slices
        ↓
在一个分支上依次实现逻辑 Commits
        ↓
冻结完整分支 Base / Head
        ↓
Spec Reviewer ──────┐
                    ├→ 一次性 Findings
Standards Reviewer ─┘
        ↓
Worker 逐项处置并持久化
        ↓
最终 Gate → 单一 PR → 集成与关闭
```

Slice 期间不运行双轴 Review、完整仓库 Gate、CI、集成检查或 PR 检查。Delivery Worker 可以运行能明显缩短反馈周期的窄而快的局部检查；这些检查不是交付 Gate，也不需要 Tracker checkpoint。

临时或 fixup Commit 可以在编码期间存在。进入 Review 前，历史必须收敛为每个变更 Slice/Ticket 一个完整、可解释的逻辑 Commit。已经满足批准结果的 Slice/Ticket 使用 `NO_CHANGE_REQUIRED` 和可观察证据，不制造空 Commit。

### 唯一一次双轴 Review

全部 Slices 完成后，Delivery Worker 冻结完整分支的 Base、Head、Diff、Slice 证据映射、批准契约与仓库规范，再调用两个隔离、只读 Reviewer：

- Standards Reviewer 检查仓库规范和当前变更的具体工程风险。
- Spec Reviewer 检查实现是否完整、正确地满足批准结果，且没有越界行为。

两份报告只收集一次。Reviewer 不返回合并许可，不产生 `PASS`、`REPAIR_REQUIRED` 或持久 Verdict，也不参加修复后的重新审查。

对于有界 Initiative，第一个 Spec 到达 Review 时创建 Reviewer 对；后续 Specs 继续使用同一对任务，并重新绑定当前 Spec、Base、Head、分支、契约和 Diff。保留自然会话历史，但当前审查范围仍以重新绑定的输入为准。

### Worker 一次性处置 Findings

每个 Finding 必须有一种处置：

- `FIXED`：确认是当前交付问题，完成最小完整修复并记录 Commit 与验证证据。
- `REJECTED`：证据表明 Finding 缺少当前权威、可达后果、具体风险或违反项，或者当前实现已经满足要求。
- `CONTRACT_BLOCKER`：问题真实，但正确解决必须改变批准的 Spec、Scope、ADR、公共接口或产品行为。

冻结点和两份完整 Review 报告先写入 Tracker 的普通 Comment/Note/记录；全部处置完成后，再把处置理由、修复 Commits、验证证据和结果 Head 写入第二条记录。恢复时可从这些事实继续，不需要联系 Reviewer。

永远不运行第二次 Review。若修复仍在契约内，但必须推翻 Slice 计划或核心实现设计，停止为 `REPLAN_REQUIRED`；若必须改变契约，停止为 `CONTRACT_BLOCKER`。

### 最终 Gate、PR 与完成

全部 Findings 有处置后，Delivery Worker 才运行仓库要求的完整 Gate。候选代码造成的失败由 Worker 诊断和修复，直至 Gate 通过；Gate 修复形成明确 Commit，但不重新启动 Review。

本地 Gate 通过后创建一个覆盖完整大 Ticket 或 Spec 的 PR。后续检查、修复和合并遵循仓库 Integration Policy、保护规则、Required Checks 与权限；不会因为 PR 检查而重新打开 Review。

PR 集成后才完成工作项：大 Ticket 直接关闭；Spec 先验证所有 Ticket 的逻辑 Commit 或 `NO_CHANGE_REQUIRED` 证据和验收结果，再关闭 Tickets 与 Spec；有界 Initiative 在全部成员 Specs 交付后关闭。

`run-initiative` 不授权发布、部署或生产迁移。若 Spec 声明 `Release Boundary`，完成报告只指出剩余 Post-delivery action 和 Tracking reference，不操作外部工作项。

## 状态、暂停与恢复

| 终态 | 含义 | 用户下一步 |
| --- | --- | --- |
| `COMPLETED` | 分支已集成、必需检查通过、Finding 处置完整，Tracker 反映真实交付 | 检查最终链接和交付摘要 |
| `REPLAN_REQUIRED` | 契约仍足够，但当前候选需要实质不同的 Slice 计划或实现设计 | 保留分支并重新规划，不自动再 Review |
| `CONTRACT_BLOCKER` | 正确交付需要改变批准的产品结果、Scope、ADR、公共接口或失败行为 | 由用户裁决并更新正式契约 |
| `BLOCKED` | 权限、基础设施、外部证据、目标状态或其他可恢复条件阻止推进 | 修复条件后从现有事实恢复 |
| `CANCELLED` | 用户明确停止交付 | 保留已有 Git 证据，按需重新开始 |
| `FAILED_PRECONDITION` | 启动前缺少有效输入或权限 | 修复列出的前置条件后重试 |

恢复只读取正式 Tracker 工作项、Review 与处置记录、分支、Commit 历史、已有 PR 和当前检查。缺少关键事实时不猜测、不重建旧 Scheduler/repair-cycle 协议，也不做破坏性清理。

## Tracker 与持久化

Forgeloop 支持三种 Tracker：

| 模式 | 正式工作项 | Review/处置证据 |
| --- | --- | --- |
| GitHub | GitHub Issues 与关系 | Issue Comments |
| GitLab | GitLab Issues 与关系 | Issue Notes |
| Local | `.scratch/<feature>/` | 现有 Agent Run 记录区 |

三种模式遵循同一交付语义。切换适配器不应改变分支、Review、Gate、PR 或完成边界。

## 从 4.2.1 升级到 4.3.0

4.3.0 删除每 Ticket Scheduler/Coder/双 Reviewer 修复循环，以及对应的运行 References、Checkpoint Event 和 Acceptance Seal 协议。现有运行不能在新版本中继续解释；请保留其 Git 与 Tracker 证据，并按新的大 Ticket、Spec 或有界 Initiative 形态重新启动。

完整步骤与行为差异见 [`docs/migrations/4.2.1-to-4.3.0.md`](docs/migrations/4.2.1-to-4.3.0.md)。

## 维护与验证

以下命令都从仓库根目录运行。

`plugins/forgeloop/` 是 Codex 实际安装的运行包，只包含 `.codex-plugin/` 与 `skills/`。生成配置、维护脚本、测试和跨 Tracker 规划 Fixture 位于 `tooling/forgeloop/`。

### 发布验证

```bash
python3 tooling/forgeloop/scripts/validate_suite.py \
  --mode release \
  --plugin-root plugins/forgeloop

python3 -m unittest discover \
  -s tooling/forgeloop/tests \
  -p 'test_*.py'
```

发布验证检查插件清单、20 个 Skills、11/9 调用策略、集中元数据、引用、上游同步和 4.3 运行契约。

### 单项契约检查

```bash
python3 tooling/forgeloop/scripts/validate_runtime_contract.py
python3 tooling/forgeloop/scripts/refresh_skill_metadata.py --check
python3 tooling/forgeloop/scripts/validate_fixtures.py \
  tooling/forgeloop/fixtures/m1-tracker-paths.json
python3 tooling/forgeloop/scripts/sync_upstream.py --check
```

### Agent 行为评估

```bash
FORGELOOP_RUN_AGENT_EVALS=1 python3 -m unittest discover \
  -s tooling/forgeloop/tests \
  -p 'test_*_agent_eval.py'
```

该评估需要已认证的全局 `codex` CLI，并在临时沙箱中验证路由与语义判断，不访问真实 Tracker。

### 已安装缓存复验

定位 Codex 当前安装的 `forgeloop-local/forgeloop` 最新缓存根目录后运行：

```bash
python3 tooling/forgeloop/scripts/validate_suite.py \
  --mode installed \
  --plugin-root <installed-cache-root>
```

该模式确认安装产物仍然包含恰好 20 个 Skills、正确调用策略和单一 `+codex.` 缓存版本后缀。

## 许可证

[MIT](LICENSE)
