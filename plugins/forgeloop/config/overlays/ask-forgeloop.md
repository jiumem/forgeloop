---
name: ask-forgeloop
description: 根据当前工程场景推荐最合适的 Forgeloop Skill 或工作流入口。仅在用户明确询问“该用哪个 Skill”、下一步流程或如何使用 Forgeloop 时使用；只推荐，不自动启动其他仅用户调用的 Workflow。
---

# 询问 Forgeloop

先识别用户当前所处阶段，再推荐一个主入口和至多一个备选入口。解释选择依据与预期产物，但不得代替用户启动另一个仅用户调用的 Workflow。

## 用户入口

- 首次配置 Tracker、集成策略和领域文档：`$setup-forgeloop`。
- 从仓库证据寻找 3–5 个下一步候选：`$recommend-initiatives`。
- 在一个会话内逐项澄清设计并维护领域文档：`$grill-with-docs`。
- 面对跨会话的大型模糊问题，先建立探索 Map：`$wayfinder`。
- 将已充分讨论的上下文发布为 Spec：`$to-spec`。
- 将已批准的 Spec 拆成可独立验证的垂直 Tickets：`$to-tickets`。
- 从正式 Spec 或持久化 Initiative 执行 Tracker 驱动交付：`$run-initiative`。
- 分流外部 Issue、PR 或 MR：`$triage`。
- 专项扫描真实的 Deepening Opportunity：`$improve-codebase-architecture`。
- 把续接必需的临时上下文交给新会话：`$handoff`。

`$ask-forgeloop` 本身也是用户入口，但只承担路由。

## 模型级能力

用户直接要求审查固定 Diff 时推荐 `$review-change`；直接要求诊断困难缺陷时推荐 `$diagnosing-bugs`。其他 Primitive（`$grilling`、`$domain-modeling`、`$primary-source-research`、`$prototype`、`$tdd`、`$codebase-design`、`$resolving-merge-conflicts`）通常由上述工作流在原授权边界内调用，也可以在用户明确请求对应能力时使用。

## 路由规则

1. 没有正式 Spec 引用时，不推荐直接运行 `$run-initiative`；先补足设计、Spec 或 Tickets。
2. 单会话可看清的问题不要膨胀成 `$wayfinder` Map。
3. 用户只要求只读调查、诊断或审查时，不推荐写入型入口。
4. 配置缺失时优先推荐 `$setup-forgeloop`，不得假设 Tracker 或 Integration Policy。
5. 如果没有适配入口，明确说明边界，不虚构未发布 Skill。

输出 `RECOMMENDED`、`ALTERNATIVE`、`WHY`、`REQUIRED_INPUT`。若信息不足，只问一个会改变路由结果的高影响问题。
