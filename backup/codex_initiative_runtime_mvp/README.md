# Codex Initiative Runtime MVP

这是一个 **Codex 原生 Initiative 自动编码—审查执行体系** 的小型可运行 MVP。

它实现了四件核心能力：

1. 从 **单篇总任务文档** 解析 Initiative / Milestone / Workstream / Task。
2. 做 **Planning Preflight**，阻断未裁决或字段不完整的规划输入。
3. 在运行时重建 **Initiative / Milestone / Task** 派生状态。
4. 提供 **Initiative 主循环**、**Task 内部状态机**、**G1/G2/G3** 与 **R1/R2/R3** 的最小落地代码与 Codex skills / agents 目录。

## 目录法位

- `docs/initiatives/*.md`：总任务文档真理源
- `docs/design/*.md`：方案设计文档
- `.codex/`：项目级 Codex 配置与 custom agents
- `.agents/skills/`：显式 workflow 技能
- `src/codex_initiative_runtime/`：确定性 Python 内核
- `.initiative-runtime/`：可重建的运行时 cache，不是真理源

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cir planning-preflight --initiative-doc docs/initiatives/INIT-001.md
cir rebuild-state --initiative-doc docs/initiatives/INIT-001.md
cir run-initiative --initiative-doc docs/initiatives/INIT-001.md
python -m unittest -q
```

## 在 Codex 中的主入口

```text
$run-initiative INIT-001
```

## 重要说明

- **用户主入口是 Initiative**，不是 Task。
- **Task 仍然是内部最小执行原子**，用于 anchor commit、G1/R1、局部回滚与差异归因。
- `.initiative-runtime/` 里的内容可以删除；系统应能从总任务文档、Git 锚点与正式报告重建状态。
- 本项目不引入 MCP；核心编排面为 **skills**。

## 机器可读总任务文档格式

`docs/initiatives/*.md` 使用单篇 Markdown，并在文中内嵌一个 `initiative-plan` fenced block：

```initiative-plan
{
  "initiative": { "...": "..." },
  "milestones": [],
  "workstreams": [],
  "tasks": [],
  "pr_plan": []
}
```

人类主要编辑 Markdown 正文；运行时从该 fenced block 提取结构化数据。

## 运行时状态重建原则

- **规划真理源**：方案设计文档、差距分析文档、总任务文档
- **工程真理源**：Git anchor/fixup/revert commit、branch、PR
- **质量真理源**：G1/G2/G3 结果、R1/R2/R3 报告、真实环境验证记录

`.initiative-runtime/` 仅做派生缓存。
