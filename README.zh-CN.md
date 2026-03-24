**语言:** [English](README.md) | [简体中文](README.zh-CN.md)

# Forgeloop

Forgeloop 是一个仅面向 Codex 的 workflow layer，由一组可组合 skills 构成。它把 Codex 约束成一套更严格的工程流程：先设计，再规划，再按小步验证实现，并在继续之前完成审查。

`0.1.1` 版本有意只作为 Codex skill pack 发布，不作为 Python 包发布。

## 来源

Forgeloop 基于 [obra/superpowers](https://github.com/obra/superpowers) 的源码进行定制适配。这个仓库保留了其核心 workflow 思路，但把整体能力收束并重接成了更适合 Codex-only 场景和本项目工程约束的版本。

## 工作流

1. `brainstorming` 把粗略需求整理成经过审查的设计。
2. `using-git-worktrees` 在工作不适合直接落在当前树时创建隔离工作区。
3. `writing-plans` 把设计拆成细粒度、明确的实现步骤。
4. `task-loop` 或 `executing-plans` 执行计划。
5. `test-driven-development`、`requesting-code-review`、`verification-before-completion` 在实现过程中提供质量闸门。
6. `finishing-a-development-branch` 在结束时处理 merge、PR、保留或丢弃分支等决策。

这些 skills 不是可选建议，而是预期中的强约束工作流。

项目级 custom agents 位于 [`.codex/agents`](.codex/agents)。当前包含 `design_challenger`、`plan_reviewer`、`implementer`、`spec_reviewer`、`code_reviewer` 等边界明确的角色。

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

更详细的安装说明见 [docs/forgeloop/install.md](docs/forgeloop/install.md)。
custom agent 清单见 [docs/forgeloop/agents.md](docs/forgeloop/agents.md)。

## 内置 Skills

**规划与执行**
- `using-forgeloop`
- `brainstorming`
- `writing-plans`
- `task-loop`
- `executing-plans`
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
