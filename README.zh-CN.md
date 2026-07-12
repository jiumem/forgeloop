# Forgeloop 中文手册

Forgeloop 是一套面向 Codex 的 Tracker 驱动交付插件。它不替代 Codex，也不建立第二套项目管理系统；它把 Codex 已有的任务、子任务、Git 与 Tracker 能力组织成一条可恢复、可评审、可验收的工程交付路径。

> 当前版本：`3.0.0` · 20 个正式 Skill · 11 个用户入口 · 9 个模型可调用能力

[快速开始](README.md) · [3.0 发布说明](docs/releases/3.0.0-release-notes.md) · [3.0 迁移指南](docs/migrations/2.5.0-to-3.0.0.md)

## 目录

- [架构原则](#架构原则)
- [安装](#安装)
- [初始化项目](#初始化项目)
- [三条常用路径](#三条常用路径)
- [20 个正式 Skill](#20-个正式-skill)
- [run-initiative 如何闭环](#run-initiative-如何闭环)
- [状态、暂停与恢复](#状态暂停与恢复)
- [Tracker 与持久化](#tracker-与持久化)
- [迁移到 3.0](#迁移到-30)
- [维护与验证](#维护与验证)

## 架构原则

### 一份事实，一个归属

| 事实 | 唯一来源 | Forgeloop 的边界 |
| --- | --- | --- |
| Spec、Ticket、依赖、认领、运行状态 | Tracker | 读写正式工作项，不维护平行计划账本 |
| 分支、提交、PR、检查、合并 | Git 与托管平台 | 验证真实提交状态，不把 Tracker 文本当作 Git 状态 |
| 行为与质量 | 代码和测试 | 以可执行证据判断，不以描述代替验证 |
| 术语与架构决策 | 项目上下文文档与 ADR | 按需维护，不为流程预建空文档 |

Forgeloop 不再维护 `PLAN.md`、`LEDGER.md` 或同义的第二状态系统。结构化状态只写入 Tracker；最小恢复信息写入运行记录。

### 薄 Scheduler，强边界

`run-initiative` 的 Scheduler 只做五类事情：读取当前状态、选择下一个 Ticket、组装角色任务包、验证边界、推进状态。实现判断交给 Coder，评审判断交给两个 Reviewer，产品歧义交回用户。

它遵循以下约束：

- 严格串行：任意时刻只推进一个 Ticket。
- 一个 Ticket 一个新上下文：跨 Ticket 不复用 Coder 或 Reviewer。
- 同一 Ticket 的修复轮次复用原上下文，保留问题与评审历史。
- 每个 Ticket 最多两轮修复；超过预算就暂停并暴露证据。
- Scheduler 不替子角色实现代码，也不替 Reviewer 改写评审结论。

### 角色任务包，不是 Agent 类型系统

Forgeloop 使用 Codex 的通用子任务能力，并通过 Role Task Pack 描述本轮目标、输入、约束和返回格式。Skill 不声明 Agent 类型、模型或推理强度，因为这些不是 Forgeloop 的运行控制面。

用户在 Codex 主任务中选择当前模型；子任务沿用宿主提供的运行机制。Forgeloop 只负责把工作委派清楚。

## 安装

### 前置条件

- 支持插件的 Codex 客户端。
- 目标项目使用 Git。
- GitHub Tracker 使用已登录的 `gh`；GitLab Tracker 使用已登录的 `glab`；Local Tracker 不需要远端账号。
- Python 3 只用于维护者运行验证脚本，不是日常调用 Skill 的前置条件。

### 从本仓库安装

本仓库已经通过 [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) 声明 Repo-local Marketplace，插件源码位于 [`plugins/forgeloop`](plugins/forgeloop)。

1. 克隆仓库，并在 Codex 中打开仓库根目录。
2. 在 Codex 中打开 `/plugins`。
3. 在 `forgeloop-local` Marketplace 中选择 `forgeloop` 并安装。
4. 新建一个 Codex 任务，使插件在新任务中加载。

如果本地 Marketplace 没有出现，先确认 Codex 打开的目录就是仓库根目录，并且 `.agents/plugins/marketplace.json` 可见。不要手工复制单个 Skill 目录；插件清单、元数据和脚本必须保持同一版本。

Codex 官方说明：[插件安装与使用](https://developers.openai.com/learn/developers-codex-plugin)；[按用户或仓库安装本地插件](https://learn.chatgpt.com/docs/changelog#install-plugins-per-user-or-per-repo)。

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

GitHub 与 GitLab 模式把远端 Tracker 作为正式工作项来源；Local 模式把 `.scratch/<feature>/` 作为本地 Tracker。项目中的 `docs/agents/issue-tracker.md` 记录的是接入契约与操作方式，不是另一套 Issue 数据库。

初始化完成后，可以用以下入口确认配置：

```text
$ask-forgeloop 当前 Tracker、集成策略和可执行入口是什么？
```

## 三条常用路径

### 路径一：目标已经澄清，直接交付

```text
$to-spec 把这份已澄清需求写成正式 Spec
$to-tickets 把该 Spec 拆成可独立验证的 Ticket
$run-initiative 执行这个 Spec
```

`to-spec` 负责结构化已经解决的上下文，不承担漫长访谈。如果关键信息仍然缺失，它应明确返回上下文不足；此时先回到探索入口。

### 路径二：目标模糊，先做发现

按问题类型选择一个最小入口：

- `$wayfinder`：不知道下一步最值得做什么。
- `$recommend-initiatives`：希望从当前代码库提出 1–3 个候选 Initiative。
- `$grill-with-docs`：已经有方案，希望结合项目文档进行压力测试。
- `$improve-codebase-architecture`：希望发现并设计架构改进机会。

探索得出明确结论后，再进入 `to-spec`。不要把研究、争论和范围发现延迟到 `run-initiative`。

### 路径三：已有变更或故障

- `$review-change`：评审一个分支、PR 或指定基点之后的变更。
- `$diagnosing-bugs`：定位复杂 Bug、失败或性能退化的根因。
- `$triage`：整理一组待办、故障或反馈并决定下一步。
- `$handoff`：把当前工作压缩成另一个任务可以继续的交接包。

其中 `review-change` 和 `diagnosing-bugs` 也允许在其他 Workflow 中按需复用，因此不是仅用户调用入口。

## 20 个正式 Skill

Skill 的 `description` 只回答“什么时候加载”；完整流程规则留在各自的 `SKILL.md` 中。

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
| `to-tickets` | 把 Spec 拆为 Ticket，或调和 Spec 修订与验收修复 |
| `run-initiative` | 严格串行执行一个正式 Spec 或多 Spec Initiative |
| `triage` | 对工作项、问题或反馈进行分诊 |
| `handoff` | 为另一个 Codex 任务生成可继续的交接上下文 |

这些入口必须显式调用，不应因为普通任务描述而自动注入。

### 模型可调用的完整 Workflow（2）

| Skill | 合适的触发场景 |
| --- | --- |
| `review-change` | 评审分支、PR、工作区变更或指定基点之后的改动 |
| `diagnosing-bugs` | 诊断故障、异常、失败或性能回退 |

它们本身是完整流程，但也能被 `run-initiative` 或直接任务复用。

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

“模型可调用”表示 Codex 可以根据任务语义加载，或由另一个 Workflow 复用；它不代表专用 Agent 类型。

## run-initiative 如何闭环

`run-initiative` 只接受正式 Spec 或多 Spec Initiative。它不是需求发现入口，也不会边做边发明新的工作项结构。

### 单 Ticket 循环

```text
读取 Tracker 与 Git 状态
        ↓
选择唯一可执行 Ticket
        ↓
Coder 实现并提交候选变更
        ↓
冻结 Base / Head 与输入快照
        ↓
Standards Reviewer ─┐
                    ├→ Scheduler 合并结果
Spec Reviewer ──────┘
        ↓
PASS：集成并推进 Tracker
FAIL：原 Coder 修复，再重新双审
```

两个 Reviewer 彼此隔离、只读工作，并从相同的冻结输入评审：

- Standards Reviewer 判断代码是否符合仓库标准和工程约束。
- Spec Reviewer 判断实现是否满足 Ticket 和所属 Spec。

Scheduler 必须在评审前验证候选变更已经形成真实提交，并冻结 Branch Head、Base、Head 和任务输入。如果任何共享输入发生变化，两项评审都必须重跑，不能拼接不同版本的结论。

### 修复预算

每个 Ticket 最多两轮修复。评审指出的实现问题回到原 Coder，因为它保留本 Ticket 的完整上下文。修复后重新运行两项评审。

候选提交自身导致的测试或契约失败也回到原 Coder；外部权限、远端服务或环境故障则暂停，不能伪装成代码缺陷消耗修复轮次。

### 集成与验收

Scheduler 独占 push、PR、检查和合并动作。子任务不得自行集成。

单 Spec 在全部 Ticket 集成后执行 Spec Acceptance，通过后关闭 Spec。多 Spec Initiative 先让所有成员 Spec 的 Ticket 集成，再让所有成员针对同一个最终提交分别验收；成员 Spec 暂不关闭。只有 Initiative Acceptance 通过后，才按“成员 Spec 在前、父 Initiative 在后”的顺序关闭。

如果 Initiative Acceptance 发现缺口，修复必须归属已有成员 Spec，不得创建直接挂在 Initiative 下的 Ticket，也不得重开已关闭工作项。修复集成后，所有成员 Spec 都重新验收。

### 规格修订不是运行时猜测

执行中出现实质性 Spec 修订时，`run-initiative` 暂停并要求显式调用 `to-tickets` 做调和：

- 已完成或已关闭的 Ticket 保持历史事实。
- 只对开放 Ticket 做保留、更新、替代或新增决策。
- 变更经用户批准后写回 Tracker。
- 调和结束不自动恢复执行，由用户明确继续原运行。

验收修复同样由 `to-tickets` 处理。每条缺口使用稳定的 `repair_key`，从而保证重复调用不会制造重复 Ticket。

## 状态、暂停与恢复

| 终态或暂停态 | 含义 | 用户下一步 |
| --- | --- | --- |
| `COMPLETED` | Ticket、Spec 或 Initiative 已完成闭环 | 检查最终链接和交付摘要 |
| `FAILED_PRECONDITION` | Tracker、Git、权限或配置不满足启动条件 | 修复明确列出的前置条件后重新启动 |
| `PAUSED` | 存在可恢复的环境、检查或集成阻塞 | 处理阻塞，再继续同一运行 |
| `CONTRACT_BLOCKER` | 产品、Schema 或架构意图发生冲突 | 由用户裁决并更新正式契约 |
| `PAUSED_FOR_ACCEPTANCE_REPAIR` | 验收发现缺口，需要生成归属明确的修复 Ticket | 显式调用 `to-tickets`，再继续原运行 |
| `CANCELLED` | 用户取消，或运行被明确终止 | 保留现状，按需重新启动新的运行 |

运行记录只保存恢复所需的最小 Checkpoint、Claim 和错误证据。恢复时重新从 Tracker 与 Git 读取现实状态；不能仅凭旧日志假设某一步已经完成。

## Tracker 与持久化

Forgeloop 支持三种 Tracker：

| 模式 | 正式工作项 | 适用场景 |
| --- | --- | --- |
| GitHub | GitHub Issues 与相关字段 | 项目已经使用 GitHub 协作 |
| GitLab | GitLab Issues 与相关字段 | 项目已经使用 GitLab 协作 |
| Local | `.scratch/<feature>/` | 本地实验、离线项目或尚未接入远端 Tracker |

三种模式遵循同一状态语义。切换适配器不应改变 Workflow 的产品行为。

Claim 用于防止两个运行同时推进同一个工作项。成功完成、暂停、取消和失败都必须留下可解释的状态；能够安全释放时释放 Claim，不能释放时记录恢复证据，避免静默遗留锁。

## 迁移到 3.0

3.0 将旧入口收敛到 20 个正式 Skill：

| 旧 Skill | 3.0 替代 |
| --- | --- |
| `grill-initiative` | `grill-with-docs`；需要找方向时使用 `wayfinder` |
| `plan-initiative` | `to-spec` + `to-tickets` |
| `run-initiative-sequences` | 新 `run-initiative` 的多 Spec Initiative 路径 |
| 上游 `implement` | `run-initiative` 内部的 Ticket Coder 角色 |
| 上游 `code-review` | `review-change` 与 Ticket 双 Reviewer 协议 |
| 上游 `research` | `primary-source-research` |

不保留活动的 `legacy-*` Skill 或同义别名。Harness 教学能力继续属于独立项目 `forge-harness-builder`。

完整迁移步骤见 [`docs/migrations/2.5.0-to-3.0.0.md`](docs/migrations/2.5.0-to-3.0.0.md)。

## 维护与验证

以下命令都从仓库根目录运行。

### 发布验证

```bash
python3 plugins/forgeloop/scripts/validate_suite.py \
  --mode release \
  --plugin-root plugins/forgeloop

python3 -m unittest discover \
  -s plugins/forgeloop/tests \
  -p 'test_*.py'
```

发布验证检查插件清单、20 个 Skill、11/9 调用策略、元数据、引用和运行契约。单元测试覆盖 Tracker 适配器、Fixture 与关键状态转换。

### 单项契约检查

```bash
python3 plugins/forgeloop/scripts/validate_runtime_contract.py
python3 plugins/forgeloop/scripts/refresh_skill_metadata.py --check
python3 plugins/forgeloop/scripts/validate_fixtures.py \
  plugins/forgeloop/fixtures/m1-tracker-paths.json \
  plugins/forgeloop/fixtures/m2-runtime-matrix.json
python3 -m unittest \
  plugins/forgeloop/tests/test_recommend_initiatives.py
```

### 已安装缓存复验

定位 Codex 当前安装的 `forgeloop-local/forgeloop` 最新缓存根目录后运行：

```bash
python3 plugins/forgeloop/scripts/validate_suite.py \
  --mode installed \
  --plugin-root <installed-cache-root>
```

该模式用于确认安装产物仍然包含恰好 20 个 Skill、正确的调用策略与单一 `+codex.` 缓存版本后缀。

### 上游同步审计

```bash
python3 plugins/forgeloop/scripts/sync_upstream.py --check
```

该命令只审计声明为上游映射的内容。若存在有意的本地适配，应更新对应的转换规则或映射基线，而不是手工覆盖已经评审通过的本地语义。

## 许可证

[MIT](LICENSE)
