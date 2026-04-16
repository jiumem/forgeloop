**语言:** [English](README.md) | [简体中文](README.zh-CN.md)

# Forgeloop

Forgeloop 是一套面向 Codex 的正式工程工作流。它的目标不是“给模型多几段提示词”，而是把规划、执行、审查、恢复都压到显式 formal state 上，而不是依赖对话上下文记忆。

`1.0.0` 以 repo-local Codex 插件包的形式发布，根目录位于 [`plugins/forgeloop/`](plugins/forgeloop/)。它不是 Python 包，也不是一组松散 prompt。

## 1.0 的核心形态

Forgeloop 1.0 收敛成一个很小但闭合的 workflow kernel：

- 一个 planning control spine：`Planning State Doc`
- 一个 runtime control spine：`Global State Doc`
- 一个 planning dispatcher：`run-planning`
- 一个 runtime dispatcher：`run-initiative`
- 一个单阶段 planning loop：`planning-loop`
- 一个单对象 runtime loop：`code-loop`

这套模型有几条硬约束：

- planning 未 sealed 前，runtime 不能合法启动
- planning 跨 stage 继续时，必须先 reread formal truth，再 explicit rebind
- runtime 任一时刻只执行一个已绑定 object
- 当前 object 释放控制，不等于自动绑定下一个 object
- 恢复必须来自 formal docs，而不是旧线程记忆

## 控制模型

### Planning Plane

- `run-planning` 是 planning 总入口。
- `planning-loop` 只闭合一个已绑定 stage：`design`、可选 `gap_analysis`、或 `total_task_doc`。
- `Planning State Doc` 是唯一 planning-wide control spine。
- planning rolling doc 只承载 round、handoff、review、seal、reopen 历史，不承载 dispatcher 真值。

### Runtime Plane

- `run-initiative` 是唯一可以绑定当前 runtime object 的 dispatcher。
- `code-loop` 只执行已经绑定好的当前 object。
- runtime 里合法的 object kind 只有 `task`、`milestone`、`initiative`。
- `Global State Doc` 是唯一 runtime-wide control spine。
- runtime rolling doc 只承载 object-local coder / reviewer truth，不承载 dispatcher 真值。

### Object Selection

runtime 不再持久化 `frontier` plane。当前 object 释放控制后，只会把 release fact 写入 formal runtime history；之后由 `run-initiative` 重读 formal truth，并通过共享 selector 绑定下一个 object。

这个 selector 合同位于 [`plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md`](plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md)。

## 打包发布面

### Skills

- `run-planning`：planning 顶层 dispatcher
- `planning-loop`：单 stage planning closure
- `run-initiative`：runtime 顶层 dispatcher
- `code-loop`：统一 runtime object executor
- `rebuild-runtime`：runtime control-plane recovery
- `using-git-worktrees`：workspace 绑定与 execution readiness

### Agents

Forgeloop 在 [`plugins/forgeloop/agents/`](plugins/forgeloop/agents/) 下打包了一组窄角色 custom agents：

- planning：`planner`、`design_reviewer`、`gap_reviewer`、`total_task_doc_reviewer`
- runtime：`coder`、`task_reviewer`、`milestone_reviewer`、`initiative_reviewer`

skill 决定 dispatch policy 与 packet construction；agent manifest 决定该角色如何思考与返回。formal truth 只保留 durable slot/state 字段，session-local reusable worker binding 不进入 control plane。

## 仓库结构

- [`plugins/forgeloop/skills/`](plugins/forgeloop/skills/)：正式发布的 workflow surface
- [`plugins/forgeloop/agents/`](plugins/forgeloop/agents/)：正式发布的 custom role layer
- [`plugins/forgeloop/scripts/`](plugins/forgeloop/scripts/)：bundle、validation、install 辅助脚本
- [`docs/forgeloop/`](docs/forgeloop/)：安装、agents、测试与 release-facing 文档
- [`tests/codex/`](tests/codex/)：Codex-only release gate 与 benchmark

对于 repo-local Initiative，唯一合法的 control-plane root，是 Initiative 文档旁边的 sibling `.forgeloop/`。

## 安装

Forgeloop 的安装分两步：

1. 在 Codex 中安装插件
2. materialize custom agents

推荐流程：

1. 拉取最新仓库状态。
2. 重启 Codex，使其重新加载 repo marketplace。
3. 打开 Codex Plugins 目录或 CLI plugin picker。
4. 选择 repo marketplace `Forgeloop Local`。
5. 安装 `Forgeloop` 插件。
6. 落地打包 agents：

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh
```

如果需要项目级覆盖：

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh --project-dir /path/to/project
```

安装细节见 [docs/forgeloop/install.md](docs/forgeloop/install.md)，agent 说明见 [docs/forgeloop/agents.md](docs/forgeloop/agents.md)。

## Release Validation

1.0 的发布面由 [`tests/codex/`](tests/codex/) 下的 Codex-only gate 保护。最小 release gate 见 [docs/forgeloop/testing.md](docs/forgeloop/testing.md)，当前至少包括：

- `bash tests/codex/p0-validation.sh`
- `bash tests/codex/plugin-smoke.sh`
- `bash tests/codex/verify-codex-only.sh`

formal loops bundle 导出命令：

```bash
python3 plugins/forgeloop/scripts/export_formal_loops_bundle.py
```

## 适用场景

Forgeloop 适合这类团队：

- 需要先规划、再执行、再正式收口
- 希望 control state 可恢复，而不是“继续沿着聊天往下做”
- 需要 object-local review 与 acceptance gate
- 想要 Codex-native workflow，但不希望角色无限膨胀

它不适合轻量 prompt 试验，也不适合即兴 one-shot 编码会话。

## 版本记录

版本历史见 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

MIT。见 [LICENSE](LICENSE)。
