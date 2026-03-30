**语言:** [English](README.md) | [简体中文](README.zh-CN.md)

# Forgeloop

Forgeloop 是一个仅面向 Codex 的 workflow layer，由一组可组合 skills 构成。它把 Codex 约束成一套更严格的工程流程：先设计，再规划，再按小步验证实现，并在继续之前完成审查。

`0.2.0` 版本有意只作为 Codex skill pack 发布，不作为 Python 包发布。

## 来源

Forgeloop 基于 [obra/superpowers](https://github.com/obra/superpowers) 的源码进行定制适配。这个仓库保留了其核心 workflow 思路，但把整体能力收束并重接成了更适合 Codex-only 场景和本项目工程约束的版本。

## 工作流

1. `brainstorming` 把粗略需求整理成经过审查的设计。
2. `using-git-worktrees` 在工作不适合直接落在当前树时创建隔离工作区。
3. `writing-plans` 把设计拆成细粒度、明确的实现步骤。
4. `run-initiative` 是 runtime 总入口：它绑定当前 Initiative，并恢复到正确的收口 loop。
5. `task-loop`、`milestone-loop`、`initiative-loop` 分别负责 Task、Milestone、Initiative 层收口；`flat-tasks-loop` 继续保留给有明确边界的平面任务计划执行。
6. `test-driven-development`、`requesting-code-review`、`verification-before-completion` 在实现过程中提供质量闸门。
7. `finishing-a-development-branch` 在结束时处理 merge、PR、保留或丢弃分支等决策。

这些 skills 不是可选建议，而是预期中的强约束工作流。

套件自带的 custom agent manifest 位于 [`agents/`](agents)。当前覆盖规划角色 `planner`、`design_reviewer`、`gap_reviewer`、`plan_reviewer`，runtime workflow 主角色 `coder`、`task_reviewer`、`milestone_reviewer`、`initiative_reviewer`，以及 `design_challenger`、`code_reviewer` 等辅助角色；安装脚本会把它们落到目标项目的 `.codex/agents/`。

## 安装

如果你已经在当前仓库目录内：

```bash
bash scripts/install.sh --yes
```

如果你希望把仓库托管在 `~/.codex/forgeloop`：

```bash
git clone https://github.com/jiumem/forgeloop.git ~/.codex/forgeloop
bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop
```

如果你还要把同一套 agent 层启用到某个 Codex 项目：

```bash
bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop --project-dir /path/to/project
```

更详细的安装说明见 [docs/forgeloop/install.md](docs/forgeloop/install.md)。
custom agent 清单见 [docs/forgeloop/agents.md](docs/forgeloop/agents.md)。

## 内置 Skills

**规划与执行**
- `using-forgeloop`
- `brainstorming`
- `run-planning`
- `planning-loop`（内部 planning stage skill）
- `writing-plans`
- `run-initiative`
- `task-loop`
- `milestone-loop`
- `initiative-loop`
- `flat-tasks-loop`
- `dispatching-parallel-agents`
- `using-git-worktrees`
- `finishing-a-development-branch`

**质量**
- `test-driven-development`
- `requesting-code-review`
- `receiving-code-review`
- `verification-before-completion`
- `systematic-debugging`

## 验证

Codex 相关验证步骤见 [docs/forgeloop/testing.md](docs/forgeloop/testing.md)。

## 方法论

- 测试优先。
- 显式计划优于临场 improvisation。
- 任务相互独立时使用隔离 agent。
- 尽早审查，避免问题层层累积。
- 用证据验证行为，而不是相信口头声明。

## 许可证

MIT License。见 [LICENSE](LICENSE)。
