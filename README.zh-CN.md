**语言:** [English](README.md) | [简体中文](README.zh-CN.md)

# Forgeloop

Forgeloop 是一个仅面向 Codex 的 workflow layer，由一组可组合 skills 构成。它把 Codex 约束成一套更严格的工程流程：先设计，再规划，再按小步验证实现，并在继续之前完成审查。

`0.7.1` 现在以 repo-local Codex 插件包的方式发布，但仍然不是 Python 包。

## 来源

Forgeloop 基于 [obra/superpowers](https://github.com/obra/superpowers) 的源码进行定制适配。这个仓库保留了其核心 workflow 思路，但把整体能力收束并重接成了更适合 Codex-only 场景和本项目工程约束的版本。

## 工作流

1. `run-planning` 是规划总入口：它绑定当前 Initiative 的 planning 输入与最小控制面，然后路由到已确认的规划阶段。
2. `planning-loop` 是 `run-planning` 内部使用的单阶段规划收口 skill。
3. `run-initiative` 是 runtime 总入口：它绑定当前 Initiative，执行 planning admission，并在需要时调用 `using-git-worktrees` 后恢复到正确的收口 loop。
4. `task-loop`、`milestone-loop`、`initiative-loop` 分别负责 Task、Milestone、Initiative 层收口。
5. `rebuild-runtime` 在运行态控制面缺失、冲突或无法直接恢复时负责重建最小控制面。

这些 skills 不是可选建议，而是预期中的强约束工作流。

对于 repo-local Initiative，planning 与 runtime 两套控制面文档唯一合法的根目录，就是专项文档旁边的 sibling `.forgeloop/`。

套件自带的 custom agent manifest 位于 [`plugins/forgeloop/agents/`](plugins/forgeloop/agents)。当前覆盖规划角色 `planner`、`design_reviewer`、`gap_reviewer`、`plan_reviewer`，以及 runtime workflow 主角色 `coder`、`task_reviewer`、`milestone_reviewer`、`initiative_reviewer`；默认会落到 Codex 全局 agent 目录，只有显式传入 `--project-dir` 时才会落到目标项目的 `.codex/agents/`。

## 安装

Forgeloop 的安装分两步，不是一条脚本全装完：

1. 先在 Codex 里安装插件。
2. 再用脚本落 custom agents。

### 1. 在 Codex 里安装插件

第一步是交互式操作，可以通过：

- Codex 桌面端的 Plugins 目录，或
- Codex CLI 里的 `/plugins`

推荐流程：

1. 拉取最新仓库内容后重启 Codex。
2. 打开 Codex 的 Plugins 目录。
3. 选择 repo marketplace `Forgeloop Local`。
4. 安装 `Forgeloop` 插件。

### 2. 落 custom agents

插件装好后，再执行：

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh
```

这会把 Forgeloop custom agents 落到 Codex 全局 agent 目录里。

如果你需要项目级覆盖，再执行：

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh --project-dir /path/to/project
```

这个脚本不会替你安装插件本体；插件安装仍然是 Codex 内的交互步骤。

更详细的安装说明见 [docs/forgeloop/install.md](docs/forgeloop/install.md)。
custom agent 清单见 [docs/forgeloop/agents.md](docs/forgeloop/agents.md)。

## 内置 Skills

**核心循环 Skills**
- `run-planning`
- `planning-loop`（内部 planning stage skill）
- `run-initiative`
- `using-git-worktrees`
- `rebuild-runtime`
- `task-loop`
- `milestone-loop`
- `initiative-loop`

## 验证

Codex 相关验证步骤见 [docs/forgeloop/testing.md](docs/forgeloop/testing.md)。

## 发布说明

版本变更记录见 [CHANGELOG.md](CHANGELOG.md)。

## 方法论

- 测试优先。
- 显式计划优于临场 improvisation。
- 任务相互独立时使用隔离 agent。
- 尽早审查，避免问题层层累积。
- 用证据验证行为，而不是相信口头声明。

## 许可证

MIT License。见 [LICENSE](LICENSE)。
