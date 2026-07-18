# Forgeloop

Forgeloop 是一套面向 Codex 的 Tracker 驱动交付插件。它把模糊需求收敛为 Spec 和 Ticket，再由一个轻量 Scheduler 严格串行地组织实现、双重评审、验收与集成。

> 当前版本：`3.6.0` · 20 个正式 Skill · 11 个用户入口 · 9 个模型可调用能力

[完整中文手册](README.zh-CN.md) · [3.6.0 发布说明](docs/releases/3.6.0-release-notes.md) · [3.3.0 → 3.3.1 迁移指南](docs/migrations/3.3.0-to-3.3.1.md)

## 它解决什么问题

```text
已澄清的需求
    ↓
to-spec → to-tickets → run-initiative
                           ↓
              Coder → Standards Reviewer
                    → Spec Reviewer
                           ↓
                 验收 → PR/合并 → 完成
```

- Tracker 是 Spec、Ticket、依赖、认领和运行状态的唯一事实来源。
- Git 是分支、提交、PR 和合并状态的唯一事实来源。
- `to-spec` 在发布前审计候选方案的必要性，删除无证据复杂度；`to-tickets` 只把已批准方案拆成最小、可观察的 Ticket 图。
- Scheduler 每次只推进一个 Ticket；跨 Ticket 不复用子任务上下文。
- 每个修复周期由一个 Coder 实现，再接受相互独立的规范评审和需求评审。
- 每组三轮修复是一次强制诊断边界，不是 Ticket 的永久终点。
- 周期耗尽后先确认暂停，再由 fresh Coder 语义判断是否在同一 Ticket、Run 和 Branch 上自动续配；字段组织证据，不替代 Agent 判断。
- `CONTRACT_BLOCKER` 先形成完整调和包并完成内部语义 Review；用户一次决定即可授权 Spec/ADR/Ticket 调和与原 Run 恢复，不必分别调用工作流。

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
