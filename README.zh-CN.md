# Forgeloop

Forgeloop 是面向 Codex 的 Tracker 驱动工程 Skill 套件。它把高影响设计决定交给用户，把代码库调查、Spec/Ticket 发布、串行实现、独立双轴审查、修复、集成、恢复和最终验收交给 Agent，同时保持每类系统事实只有一个真理源。

```text
想法或请求
  → 设计澄清 / 大型探索
  → Tracker Spec
  → 有依赖的垂直 Tickets
  → Coder 验证
  → Spec Reviewer + Standards Reviewer
  → 修复与集成
  → Spec / Initiative Acceptance
```

## 核心原则

- GitHub、GitLab 与 Local Markdown 是正式且等价的 Tracker 主路径。
- Ticket 是最小实现和审查单元；一个 Initiative 同时只运行一张 Ticket。
- Coder 负责实现与验证；两个 Reviewer 使用独立上下文；Scheduler 只编排。
- 双 Reviewer 的 Verdict 绑定同一 Base/Head；代码变化后必须重新签发。
- Spec、Ticket、阻塞和运行状态只存在于 Tracker；候选实现存在于 Branch、Commit、PR/MR。
- 不维护与 Tracker 平行的本地执行账本。
- `run-initiative` 必须由用户明确调用，并且只接受正式 Spec 或持久化 Initiative 引用。

## 20 个 Skills

仅用户调用的入口：

- `setup-forgeloop`：配置 Tracker、Integration Policy、Triage 标签和领域文档。
- `ask-forgeloop`：只推荐合适入口，不自动启动其他用户工作流。
- `recommend-initiatives`：只读推荐 3–5 个有仓库证据的候选。
- `improve-codebase-architecture`：扫描真实 Deepening Opportunity。
- `grill-with-docs`：逐项澄清设计并按需维护领域术语与 ADR。
- `wayfinder`：把跨会话的大型模糊问题建立为探索 Map。
- `to-spec`：把已充分讨论的上下文发布为 Tracker Spec。
- `to-tickets`：把批准的 Spec 拆为带 Blocking 的垂直切片。
- `run-initiative`：运行 Coder、双 Reviewer、修复、集成、恢复与最终验收。
- `triage`：分流外部 Issue、PR 或 MR。
- `handoff`：把续接必需的临时上下文写入 OS 临时目录。

模型可调用的 Workflow 与 Primitive：

- `review-change`、`diagnosing-bugs`
- `grilling`、`domain-modeling`、`primary-source-research`、`prototype`
- `tdd`、`codebase-design`、`resolving-merge-conflicts`

## 配置与主路径

首次使用先显式调用：

```text
使用 $setup-forgeloop 为当前仓库配置 Tracker、集成策略和领域文档。
```

从已充分讨论的需求交付：

```text
使用 $to-spec 将当前上下文发布为正式 Spec。
使用 $to-tickets 将该 Spec 拆成可独立验证且带 Blocking 的 Tickets。
使用 $run-initiative 从该 Spec 运行完整交付闭环。
```

大型模糊目标先用 `$wayfinder`；单会话可澄清的设计使用 `$grill-with-docs`。不确定入口时显式调用 `$ask-forgeloop`。

## Tracker

- GitHub 使用全局配置的 `gh` CLI。
- GitLab 使用 `glab` CLI。
- Local Markdown 使用 `.scratch/<feature>/`，并通过原子 Claim Lock 与 Git 事实完成恢复和集成。

认证、权限、保护分支、Required Checks、坏引用或状态冲突都会明确停止；远端失败不会静默回退为 Local。

## 安装

插件源码位于：

```text
plugins/forgeloop/
```

Manifest：

```text
plugins/forgeloop/.codex-plugin/plugin.json
```

安装或更新本地 Marketplace 后，请在新 Codex 任务中验证 Skill 发现与 Invocation Policy。

## 迁移

`2.5.0` 到 `3.0.0` 是破坏性升级。历史完成/归档产物保持只读；活动工作可以固定旧版本完成，或在预览与确认后重新生成为 Tracker Specs/Tickets。详见 [迁移指南](docs/migrations/2.5.0-to-3.0.0.md)。

## 验证

```bash
python3 plugins/forgeloop/scripts/validate_suite.py --mode release
python3 plugins/forgeloop/scripts/sync_upstream.py --check
python3 plugins/forgeloop/scripts/refresh_skill_metadata.py --check
python3 plugins/forgeloop/scripts/validate_runtime_contract.py
python3 plugins/forgeloop/scripts/validate_fixtures.py \
  plugins/forgeloop/fixtures/m1-tracker-paths.json \
  plugins/forgeloop/fixtures/m2-runtime-matrix.json
```

## 许可证

[MIT](LICENSE)
