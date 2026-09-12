# Forgeloop

Forgeloop 是一套面向 Codex 的 Tracker 驱动交付插件。它把模糊需求收敛为 Spec 和 Ticket，再由一个负责到底的 Delivery Worker 完成实现、一次性双轴审查、最终 Gate 与集成。

> 当前版本：`4.3.0` · 20 个正式 Skill · 11 个用户入口 · 9 个模型可调用能力

[完整中文手册](README.zh-CN.md) · [4.3.0 发布说明](docs/releases/4.3.0-release-notes.md) · [4.2.1 → 4.3.0 迁移指南](docs/migrations/4.2.1-to-4.3.0.md)

## 它解决什么问题

```text
已澄清的需求
    ↓
to-spec → to-tickets → run-initiative
                           ↓
                  Delivery Worker
                       ↓
              Standards Reviewer ─┐
                                  ├→ Findings
              Spec Reviewer ──────┘
                           ↓
                 Worker 处置 → Gate → PR/合并
```

- Tracker 是 Spec、Ticket、依赖和交付证据的唯一事实来源。
- Git 是分支、提交、PR 和合并状态的唯一事实来源。
- `to-spec` 在发布前审计候选方案的必要性并原位维护 Planning Revision；`to-tickets` 只把已批准方案拆成最小、可观察的 Ticket 图。
- 跨 Ticket 共享的系统设计进入正式 Design Document；`grill-with-docs` 负责判断和维护，ADR 只承载长期架构决策。
- `run-initiative` 支持一个明确的大 Ticket、一个正式 Spec，或一个有界的多 Spec Initiative；不推荐用于小 Ticket，也不组合多个 Initiatives。
- 大 Ticket 使用一个分支，每个 Worker Slice 对应一个逻辑 Commit；Spec 同样使用一个分支，每个 Ticket 直接成为一个实现 Slice。
- Slice 期间只做必要的窄验证，不运行双轴 Review、完整 Gate、CI 或 PR 检查；全部实现完成后再统一收敛。
- 整条交付分支只进行一次双轴 Review。Reviewer 全面检查，但只报告会改变当前交付判断的问题，过滤低价值技术洁癖和范围外未来设想。
- Review 只提供 Findings，不产生合并 Verdict。Delivery Worker 对每个 Finding 记录 `FIXED`、`REJECTED` 或 `CONTRACT_BLOCKER`，且不启动重新审查循环。
- Findings 处理完后才运行完整 Gate、创建一个 PR 并按仓库策略集成。契约内的大规模重规划返回 `REPLAN_REQUIRED`，契约变化返回 `CONTRACT_BLOCKER`。
- 有界 Initiative 为每个 Spec 使用一个分支和一个 PR，并在 Specs 间复用同一对隔离 Reviewer，避免重复创建上下文。

## 60 秒开始

### 1. 安装插件

克隆本仓库并在 Codex 中打开仓库根目录。仓库已经通过 [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) 声明本地 Marketplace：

1. 在 Codex 中打开 `/plugins`。
2. 在 `forgeloop-local` Marketplace 中选择 `forgeloop` 并安装。
3. 新建一个 Codex 任务，使插件在新任务中生效。

详见 [Codex 插件安装说明](https://developers.openai.com/learn/developers-codex-plugin)。

### 2. 初始化项目

在目标代码仓库中显式调用：

```text
$setup-forgeloop
```

它会确认 Tracker 运行方式、集成策略和领域文档约定。支持 GitHub、GitLab 与 Local 三种 Tracker。

### 3. 交付第一个需求

```text
$to-spec 把已经澄清的需求写成可验收的 Spec
$to-tickets 把这份 Spec 拆成依赖明确的 Ticket
$run-initiative 执行并交付这个 Spec
```

如果目标还不清楚，先使用 `$wayfinder`、`$grill-with-docs` 或 `$recommend-initiatives`，不要把探索过程直接塞进执行阶段。

## 20 个正式 Skill

11 个 Workflow 只由用户显式调用：

```text
setup-forgeloop          ask-forgeloop             recommend-initiatives
improve-codebase-architecture                       grill-with-docs
wayfinder                to-spec                    to-tickets
run-initiative           triage                     handoff
```

9 个能力可以由任务匹配或其他 Workflow 调用：

```text
spec-standards-review    diagnosing-bugs            grilling
domain-modeling          primary-source-research     prototype
tdd                      codebase-design             resolving-merge-conflicts
```

“模型可调用”只表示 Codex 可以按任务语义加载该 Skill；Forgeloop 不指定子任务类型、模型或推理强度。当前任务选择的模型由用户在 Codex 主任务中控制。

## 从源码验证

在仓库根目录运行：

`plugins/forgeloop/` 是 Codex 实际安装的运行包，只包含插件清单与 Skills。生成配置、Fixture、维护脚本和测试统一位于 `tooling/forgeloop/`，不会进入插件缓存。

```bash
python3 tooling/forgeloop/scripts/validate_suite.py \
  --mode release \
  --plugin-root plugins/forgeloop
python3 -m unittest discover \
  -s tooling/forgeloop/tests \
  -p 'test_*.py'
```

维护者的完整验证矩阵、已安装缓存复验和上游同步说明见[完整中文手册](README.zh-CN.md#维护与验证)。

## 许可证

[MIT](LICENSE)
