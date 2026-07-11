# Forgeloop 编码 Skill 套件重构封板设计

状态：设计已封板，待实施规划
创建日期：2026-07-11
封板日期：2026-07-12
适用项目：`/Users/nuc8/project/forgeloop`
上游参考：Matt Pocock Skills Commit `391a2701dd948f94f56a39f7533f8eea9a859c87`

## 1. 文档目的

本文封板 Forgeloop 编码 Skill 套件的能力边界、信息模型、运行契约和迁移策略。目标是将 Matt Pocock Skills 已验证的交互设计、Tracker 工作图和工程纪律，与 Forgeloop 的 Scheduler、Coder、双 Reviewer、修复循环、恢复和长时间自治能力融合。

本文不是实施计划，不授权立即删除旧 Skills，也不包含批量重写步骤。进入编码前仍需基于本文单独编写可执行实施计划。

## 2. 封板原则

### 2.1 上游已有契约直接继承

Matt Pocock 上游已经定义的 Skill 行为、模板和流程直接从固定 Commit 继承，不重复设计。落地时只做 Forgeloop 品牌、Skill 名称、路径、跨 Skill 引用和 Codex 元数据等必要机械替换。上游的 Claude 专用 `disable-model-invocation` 不进入 `SKILL.md`；Codex 的调用策略统一写入 `agents/openai.yaml`。

典型继承对象包括：

- `setup-matt-pocock-skills` 的 Tracker 配置模式；
- `to-spec` 的正文模板和发布规则；
- `to-tickets` 的垂直切片、Wide Refactor 和依赖表达；
- `grill-with-docs`、`wayfinder`、`triage`、`diagnosing-bugs`、`prototype`、`tdd`、`domain-modeling` 与 `codebase-design` 的主体契约；
- `code-review` 的 Spec / Standards 双轴隔离思想；
- `handoff` 的临时上下文运输模式。

Forgeloop 只为上游没有覆盖的自动执行、结构化 Verdict、修复预算、状态恢复、完成门禁、模型路由和多 Spec 验收补充协议。

### 2.2 人负责高影响决策，Agent 负责调查与执行

代码库可以回答的事实由 Agent 调查；可逆、局部的实现选择由 Coder 在 Ticket 边界内处理；产品行为、范围、不可逆权衡、外部约束和合约变更由用户逐项裁决。

### 2.3 一个系统事实只有一个真理源

| 信息 | 真理源 |
|---|---|
| 领域术语 | `CONTEXT.md` |
| 长期架构决策 | `docs/adr/NNNN-*.md` |
| Spec、Ticket、阻塞、讨论和实时状态 | 配置的 Issue Tracker |
| 候选实现、评审与修复 | Branch、Commit、PR/MR、Tracker Comment |
| 可执行系统事实 | 代码与测试 |
| 临时跨会话上下文 | OS 临时目录中的 Handoff |

新工作流不再创建 `PLAN.md` 或 `LEDGER.md`，也不同时维护 Tracker 与本地运行账本。

### 2.4 Ticket 是最小实现与评审单元

Ticket 必须是窄而完整的垂直切片，能够在一个新鲜 Agent 上下文中完成，并通过公共 Seam 独立验证。每张 Ticket 拥有独立 Coder、Spec Reviewer 和 Standards Reviewer；同一 Ticket 的修复轮次复用这三个上下文，Ticket 完成后立即结束。

## 3. Tracker 支持范围

首版正式支持 Matt 上游已有的三套 Tracker：

- GitHub：使用 `gh` CLI；
- GitLab：使用 `glab` CLI；
- Local Markdown：使用 `.scratch/<feature>/`。

Linear、Jira 等保留 `Other` 自由描述入口，但首版不承诺完整兼容。

三套正式 Tracker 必须覆盖同一组语义：

- 创建、读取、评论和关闭 Spec/Ticket；
- Parent / Child 关系；
- Blocking Dependencies；
- Frontier 查询；
- Claim；
- Agent Run Events；
- Review Verdict；
- 完成与取消。

GitHub/GitLab 优先使用原生子 Issue 和依赖能力，平台不支持时沿用上游正文关系回退。Local Markdown 是正式活动 Tracker，不是 `LEDGER.md` 的替代镜像。

## 4. 领域模型

**Initiative**：用户一次授权执行的范围，可以包含一份 Spec 或一组 Specs。

**Spec**：一项完整产品或系统交付契约，默认表现为 Tracker 父 Item。

**Ticket**：Spec 下最小、可独立验证的垂直子 Item，拥有 Acceptance Criteria 和阻塞关系。

**Frontier**：选定 Initiative 范围内所有 Open、Unblocked、Unclaimed 的 Tickets。

**Agent Run**：围绕一张 Ticket 的 Coder、双 Reviewer、验证证据、候选 Commit 和修复历史。Agent Run 通过 Tracker 原生事实与追加式 Events 表达，不创建独立 Ledger。

**Review Verdict**：每个评审轴对明确 Base/Head Commit 独立返回的 `PASS` 或 `REPAIR_REQUIRED`。

## 5. Initiative 的持久化规则

### 5.1 单 Spec Initiative

- 不创建额外 Initiative 父对象；
- Spec 本身就是运行根；
- Spec 完成后 Initiative 逻辑完成。

### 5.2 多 Spec Initiative

- 必须创建持久化 Initiative Tracker Item；
- GitHub/GitLab 使用父 Issue，Local Markdown 使用 `initiative.md`；
- 只记录授权的 Spec 集合、跨 Spec 约束、运行状态和集成验收；
- 不复制各 Spec 正文；
- 增删 Spec 属于授权范围变化，必须由用户明确确认并留下事件。

## 6. 正式 Skill 清单

### 6.1 仅用户调用的 Workflow

以下 Skills 在 `agents/openai.yaml` 中设置 `policy.allow_implicit_invocation: false`：

1. `setup-forgeloop`
2. `ask-forgeloop`
3. `recommend-initiatives`
4. `improve-codebase-architecture`
5. `grill-with-docs`
6. `wayfinder`
7. `to-spec`
8. `to-tickets`
9. `run-initiative`
10. `triage`
11. `handoff`

### 6.2 模型可调用的完整 Workflow

12. `review-change`
13. `diagnosing-bugs`

### 6.3 模型可调用的 Primitive

14. `grilling`
15. `domain-modeling`
16. `primary-source-research`
17. `prototype`
18. `tdd`
19. `codebase-design`
20. `resolving-merge-conflicts`

### 6.4 Invocation 约束

- 仅用户调用的 Workflow 可以调用模型级 Workflow 或 Primitive，但不能自动启动另一个仅用户调用的 Workflow；
- `ask-forgeloop` 只推荐入口，不代替用户启动入口；
- `run-initiative` 必须始终由用户明确授权；
- 模型调用 Skill 不扩大用户原始授权；
- `diagnosing-bugs` 在用户只授权诊断时不得修改代码；
- `review-change` 默认只读；
- `prototype` 的产物始终可抛弃，不能直接并入生产代码。

### 6.5 融合与移除

- `grill-initiative` 由 `grill-with-docs` 替代；
- `plan-initiative` 由 `to-spec` 与 `to-tickets` 替代；
- `run-initiative-sequences` 由新 `run-initiative` 的多 Spec 能力替代；
- 上游 `implement` 进入 `run-initiative` 的 Ticket Coder；
- 上游 `code-review` 进入 `review-change` 与 Ticket 双 Reviewer 协议；
- 上游 `research` 更名为 `primary-source-research`；
- Harness 教学相关能力继续留在独立的 `forge-harness-builder`；
- 不发布 `legacy-*` 活动 Skill 或同义别名。

## 7. 关键 Workflow 边界

### 7.1 `recommend-initiatives`

- 保留为正式、只读、仅用户调用的 Workflow；
- 综合代码、测试、CI、Tracker、ADR 和用户已声明目标，给出 3–5 个跨类别候选；
- 默认只在对话中返回，不再写入 `docs/initiatives/recommendations/**`；
- 不创建 Spec、Ticket 或 Initiative；
- 用户选中后再进入 `grill-with-docs` 或 `wayfinder`。

### 7.2 `improve-codebase-architecture`

- 直接继承上游主体，作为专项架构扫描入口；
- 使用 `codebase-design` 的统一词汇；
- 报告写入 OS 临时目录，不写项目；
- 不直接创建 Spec、Tickets 或修改生产代码；
- 只有证明问题来自浅模块、错误 Seam、重复真理源或跨模块耦合时才提出架构候选。

### 7.3 `run-initiative`

接受以下入口：

- `run-initiative <spec-ref>`：单 Spec Initiative；
- `run-initiative <initiative-ref>`：恢复多 Spec Initiative；
- `run-initiative <spec-ref...>`：多 Spec 时先预览并创建持久化 Initiative Tracker Item。

未提供正式 Spec 引用时停止，不从模糊对话直接开始编码。收到旧 `PLAN.md` 时提示迁移或固定使用 `2.5.0`，不得按新语义静默解释。

## 8. Branch 与 Integration Policy

### 8.1 Branch 策略

- 默认每张 Ticket 使用独立 Branch；
- 只有 `to-tickets` 预先声明的不可独立落地场景才共享 Spec Integration Branch；
- 共享分支仅用于 Wide Refactor、不可独立绿色的迁移或必须原子交付的变更；
- 共享分支必须增加最终 `integrate-and-verify` Ticket；
- Coder 不得临时决定切换集成模式。

### 8.2 Integration Policy

`setup-forgeloop` 必须让用户为仓库选择：

- `auto-merge`：双 `PASS` 且 Head 未变化后自动集成；
- `human-merge`：进入 `READY_FOR_HUMAN_MERGE`，等待用户合并并刷新。

约束：

- 配置缺失时不得自动合并；
- 单次 Initiative 只有在用户明确确认并记录事件后才能覆盖仓库策略；
- 分支保护和平台权限始终优先；
- `auto-merge` 不包含部署、发布、迁移执行或其他不可逆外部操作；
- Local Markdown 同样遵守 Integration Policy。

## 9. 并发与 Claim

- 每个 Initiative 严格串行，一次只运行一张 Ticket；
- Scheduler 在当前 Ticket 完成、暂停或取消前不启动下一张；
- 每次推进后重新查询 Frontier，不复用旧快照；
- 一个 Initiative 同时只能存在一个有效 Scheduler Run；
- GitHub/GitLab 通过带 Run ID 的 Claim Event 竞争，以 Tracker 服务端最早事件为胜者；
- Local Markdown 使用 Tracker 目录内的原子 Claim Lock；
- Claim 失败者不得开始编码；
- 不使用会误判长任务死亡的短 TTL；
- 不同 Initiative 只有在用户分别显式启动时才允许并存，首版不主动并行编排。

## 10. Agent Run 状态与恢复

### 10.1 原生事实

- Open/Closed 表达是否仍需处理；
- Dependencies 表达是否被阻塞；
- Assignee 或 Local Claim 表达是否已被领取；
- Branch、PR/MR 和 Commit 表达候选实现与集成结果。

这些事实用于 Frontier 查询，不从自定义执行标签推断。

### 10.2 追加式 Events

GitHub/GitLab 将 Event 写为结构化 Comment；Local Markdown 追加到 Ticket 的 `## Agent Run Events`。

首版事件包括：

- `RUN_CLAIMED`
- `CODER_RESULT`
- `REVIEW_RESULT`
- `INTEGRATION_RESULT`
- `RUN_PAUSED`
- `RUN_CANCELLED`
- `RUN_RESUMED`
- `EVENT_SUPERSEDED`

每个事件至少包含 Schema Version、Run ID、事件序号、幂等键、Base/Head/Target、验证证据、双 Verdict、修复轮次、模型能力等级、升级原因和前一事件引用。

事件发布后不修改；错误通过 `EVENT_SUPERSEDED` 追加纠正。Tracker 原生状态与事件冲突时停止自动推进并报告恢复异常。

不增加 `CODING`、`REVIEW`、`REPAIR` 等互斥标签，也不创建 `LEDGER.md`。

## 11. Ticket Coder 契约

### 11.1 输入

Scheduler 向 Coder 提供：

- Ticket 正文与评论；
- Parent Spec 及当前 Revision；
- 已完成依赖的必要结论；
- 项目指令、`CONTEXT.md`、ADR 和工程规范；
- Base、Target 和已创建的 Ticket Branch；
- 验证入口、公共 Seam 和停止条件；
- 修复轮次中的两个评审轴 Findings。

### 11.2 权限

Coder 可以调查代码、调用模型级 Skills、修改 Scope 内代码/测试/明确要求的文档、运行验证并创建实现 Commit。

Coder 不得：

- 修改 Spec、Ticket 合约或 Acceptance Criteria；
- 写 Agent Run Events、Reviewer Verdict 或关闭 Tracker Item；
- 创建或合并 PR/MR、修改目标分支；
- 自行扩展 Scope 或发明产品行为；
- 把 `READY_FOR_REVIEW` 描述为 Ticket 已完成。

### 11.3 结果

Coder 返回以下状态之一：

- `READY_FOR_REVIEW`
- `NO_CHANGE_REQUIRED`
- `CONTRACT_BLOCKER`
- `IMPLEMENTATION_BLOCKED`

结果必须包含 Base/Head、可观察行为、Acceptance Criteria 证据、验证命令与结果、修改范围、Commit 列表、已知风险和未完成项。

`NO_CHANGE_REQUIRED` 仍需双 Reviewer 验证；`CONTRACT_BLOCKER` 不进入普通修复预算；`IMPLEMENTATION_BLOCKED` 不创建 Reviewer。

## 12. 验证职责

验证链保持精简：

```text
Coder 实现与验证
  -> Spec Reviewer
  -> Standards Reviewer
  -> 双 PASS
  -> 按 Integration Policy 集成
```

- Coder 在最终 Head 上运行与 Ticket 相关的验证并提交证据；
- Spec Reviewer 判断证据是否覆盖 Spec 行为，必要时只运行针对性的公共 Seam 验证；
- Standards Reviewer 判断测试质量、工程规范和回归保护，必要时只复现可疑检查；
- 证据不足时 Reviewer 返回 `REPAIR_REQUIRED`；
- Scheduler 只确认 Coder Result、Verdict 与 Branch 绑定同一 Head，不重复运行测试；
- CI 只按仓库已有策略自然运行，不额外触发完整 CI；
- 平台已有 Required Checks 时直接消费其结果；
- 合并冲突或 Base 更新实际改变代码时，重新进入 Coder 验证和双 Reviewer。

## 13. 双 Reviewer 与 Verdict

### 13.1 两个独立评审轴

**Spec Reviewer** 检查产品目标、Acceptance Criteria、用户路径、失败状态、范围遗漏和 Scope Creep。

**Standards Reviewer** 检查测试质量、公共 Seam、架构边界、ADR、项目规范和 Code Smells。

两个 Reviewer 使用独立上下文，不读取对方结论。Scheduler 不合并或重排两个轴的 Findings。

### 13.2 `review-change` 与运行门禁的区别

独立使用的 `review-change` 直接继承上游 `code-review` 的定性双轴报告。

只有 `run-initiative` 内部增加结构化 Verdict：

```text
axis: SPEC | STANDARDS
verdict: PASS | REPAIR_REQUIRED
base_commit: <sha>
head_commit: <sha>
spec_revision: <revision>
findings:
  - finding_id
    disposition: BLOCKING | ADVISORY
    evidence
    violated_contract
    observed
    expected
    repair_check
```

- 任一 `BLOCKING` Finding 必须导致 `REPAIR_REQUIRED`；
- 无 Blocking Finding 时返回 `PASS`，可以带 `ADVISORY`；
- Fowler Smell 默认是判断性建议，只有同时违反项目标准、ADR、测试要求或造成实际风险时才能成为 Blocking；
- Reviewer 无法读取必要输入时不返回虚假 Verdict，Scheduler 记录 `REVIEW_BLOCKED`；
- Verdict 绑定 Base/Head，代码变化后失效；
- 修复轮次沿用稳定 `finding_id`。

## 14. 模型路由

使用能力等级而非硬编码具体模型名称。

| Reviewer | 默认能力 | 默认推理强度 |
|---|---|---|
| Spec Reviewer | 强通用推理模型 | `medium` |
| Standards Reviewer | 强代码推理模型 | `medium` |

Spec Reviewer 在权限、资金、隐私、安全、多角色路径、跨 Spec 行为或 Acceptance Criteria 解释空间较大时升级。

Standards Reviewer 在 Schema/数据迁移、公共 API、并发、基础设施、Wide Refactor、共享 Integration Branch 或缺少可靠测试 Seam 时升级。

首次 `REPAIR_REQUIRED` 后提升失败评审轴的推理强度；同一问题重复失败时升至最高能力。运行环境不支持显式路由时使用最强可用模型创建两个独立 Reviewer，并记录能力降级。

## 15. 修复协议

- 同一 Ticket 的修复复用原 Coder 和两名原 Reviewer；
- 任一轴返回 `REPAIR_REQUIRED` 即进入修复；
- Coder 同时收到两个轴的 Findings；
- 两个 Reviewer 只收到本轴历史 Findings；
- 任何代码变化都会使两个旧 Verdict 失效；
- 修复后两个 Reviewer 都重新检查完整累计 Diff、修复 Diff 和最新证据；
- 同一 Finding 经两次修复仍存在时 `RUN_PAUSED`；
- 同一 Ticket 累计三次评审返回 `REPAIR_REQUIRED` 时 `RUN_PAUSED`；
- 两轴要求冲突、合约不可实现、Scope 不足或需要改变 Spec/ADR 时记录 `CONTRACT_BLOCKER`；
- 用户可以修改合约或记录正式例外，但不能把 `REPAIR_REQUIRED` 直接改写成 `PASS`。

## 16. 合并冲突协议

`resolving-merge-conflicts` 是模型可调用 Primitive，但不原样继承上游“永远解决”的规则：

- 先读取双方 Commit、Spec、Ticket、ADR 和评审记录；
- 只有两边意图兼容时才自动解决；
- 冲突代表产品、Schema 或架构决策不兼容时暂停并请求裁决；
- 不自动执行破坏性重置、丢弃提交或放弃操作；
- 冲突解决改变候选代码后，原 Verdict 失效并重新双评审。

## 17. 完成门禁

### 17.1 Ticket

Ticket 完成必须同时满足：

1. Acceptance Criteria 有实现与验证证据；
2. Coder 验证完成；
3. Spec Reviewer 对最终累计 Diff 返回 `PASS`；
4. Standards Reviewer 对同一最终累计 Diff 返回 `PASS`；
5. 两个 Verdict 绑定同一 Base/Head；
6. 候选代码按 Integration Policy 进入声明的目标分支；
7. 仓库已有 Required Checks 满足既有策略；
8. Tracker 记录 Branch/PR/MR、Commit、证据、双 Verdict 和集成结果；
9. 最后关闭 Ticket 或将 Local Ticket 标记为 `resolved`。

双 `PASS` 但尚未合并时只是 `READY_FOR_MERGE`。PR/MR 被关闭但未合并不算完成。共享 Integration Branch 下，Ticket 进入 Integration Branch 后可以完成，最终目标分支由 `integrate-and-verify` Ticket 负责。

### 17.2 Spec

Spec 完成必须同时满足：

1. 当前 Scope 内所有子 Tickets 已按 Ticket 门禁完成；
2. 不存在 Open、Blocked、`REPAIR` 或等待人工合并的 Ticket；
3. Scope 变化有用户确认记录；
4. 所有交付代码进入 Spec 的最终目标分支；
5. 取得 Spec 最终验收 Verdict；
6. Verdict 绑定 Spec Revision 和最终目标 Commit；
7. Tracker 记录交付摘要、验证入口、证据、已知限制和最终 Commit/PR/MR；
8. 最后关闭 Spec。

简单单 Ticket、常规风险、无修复且已有完整公共 Seam 证据时，Ticket Spec Reviewer 可以同时输出 `TICKET_VERDICT: PASS` 与 `SPEC_ACCEPTANCE: PASS`。

多 Ticket、共享 Integration Branch、高风险、发生过修复、跨模块/多步骤路径或证据不完整时，必须创建全新 Spec Acceptance Reviewer。失败时 Spec 保持打开并创建正式修复工作。

### 17.3 Initiative

单 Spec Initiative 随 Spec 完成而逻辑完成。

多 Spec Initiative 完成必须同时满足：

1. 成员 Spec 集合确定且范围变化有用户确认；
2. 所有成员 Specs 完成；
3. 不存在未完成、阻塞、修复或等待人工合并的工作；
4. 跨 Spec Dependencies 已解决；
5. 所有交付代码进入最终目标分支；
6. 全新的 Initiative Acceptance Reviewer 返回 `INITIATIVE_ACCEPTANCE: PASS`；
7. Verdict 绑定 Initiative Revision 和最终目标 Commit；
8. Tracker 记录成员 Specs、跨 Spec 证据、最终 Commit/PR/MR、已知限制和 Verdict；
9. 最后关闭 Initiative Tracker Item。

`CANCELLED` 与 `COMPLETED` 是不同终态；`PAUSED` 保持打开。关闭父 Item 但没有正式 Acceptance `PASS` 不算完成。

## 18. Spec 修订

Spec 在执行开始后允许版本化演进：

- 首次运行记录 `spec_revision`；
- 拼写、排版、链接和不改变行为的澄清可以记为非实质性修改；
- Problem、Actor、目标、Acceptance Criteria、失败状态、权限、Scope、公共接口、Schema、迁移、测试 Seam 或交付目标变化属于实质性修改；
- 实质性修改必须由用户确认，Initiative 进入 `PAUSED_FOR_SPEC_CHANGE`；
- `to-tickets` 重新对账 Open Tickets，已完成 Tickets 保留历史；
- 受影响 Verdict 和最终验收资格失效；
- 核心 Problem、Actor 或交付目标被替换时创建新 Spec，并将旧 Spec 标记为 `SUPERSEDED`；
- Coder 和 Reviewer 只能返回 `CONTRACT_BLOCKER`，不得直接修改 Spec。

## 19. 迁移策略

新套件以破坏性大版本原子切换，建议版本为 `3.0.0`。

### 19.1 旧 Skills

- 新套件通过 Fixture 验收后，从活动 `plugins/forgeloop/skills/` 删除五个旧实现；
- 不发布 `legacy-*` Skills；
- 使用 Git Tag/Release 保留 `2.5.0` 源码；
- 原子更新 README、Manifest、默认 Prompt 和能力说明。

### 19.2 下游历史文档

新版 `setup-forgeloop` 检测 `docs/initiatives/**` 时只报告，不自动迁移：

- `completed/`、`archived/`、`handoff/`、`recommendations/` 原地只读保留；
- 未执行 `DESIGN.md` 可在用户确认后转换为 Spec；
- 未执行 `PLAN.md` 在确认 Spec 后重新拆 Tickets，不机械复制 Milestones；
- 已有 `LEDGER.md` 不自动迁移；
- 用户可以固定 `2.5.0` 完成旧 Initiative，或显式授权把未完成范围重新生成 Specs/Tickets；
- 已完成 Milestone 只作为历史证据，不创建伪完成 Tickets；
- 原文件不删除、不移动；
- 迁移必须预览、逐 Initiative 确认并保持幂等。

## 20. 非目标

- 本文不决定具体实施顺序和 Commit 划分；
- 本文不立即删除或改写现有五个 Skills；
- 本文不立即迁移任何下游 `docs/initiatives/**`；
- 首版不自动并行一个 Initiative 内的 Frontier；
- 首版不承诺 Linear、Jira 等 `Other` Tracker 的完整兼容；
- 不把 Harness 创作或长期教学放回 Forgeloop；
- 不把 GitHub/GitLab/Local Tracker 状态复制成 `PLAN.md` 或 `LEDGER.md`；
- 不让 Coder 自己批准、集成或关闭 Ticket；
- 不额外触发昂贵 CI 来重复 Coder 与 Reviewer 已完成的验证职责。

## 21. 实施规划前接受条件

本文已完成以下设计裁决，实施计划必须逐项保持：

- 正式 20 个 Skill 清单与 Invocation 边界；
- GitHub、GitLab、Local Markdown 三套 Tracker 契约；
- Initiative、Spec、Ticket、Frontier、Agent Run 和 Review Verdict 的唯一真理源；
- Ticket、Spec 和 Initiative 三层完成条件；
- Ticket Coder、双 Reviewer、修复预算、模型升级和最终验收协议；
- Branch、Integration Policy、并发、Claim 与恢复协议；
- 旧 Skills 和历史 Initiative 文档迁移策略；
- 上游已有契约直接继承、Forgeloop 只补新增运行能力的边界。

实施验收至少需要 Fixture 覆盖：

1. 单 Spec、单 Ticket 的简单闭环；
2. 单 Spec、多 Ticket 的依赖图与 Frontier；
3. 多 Spec Initiative 与跨 Spec 最终验收；
4. 双 Reviewer 一方失败后的修复循环；
5. 修复预算耗尽与 `CONTRACT_BLOCKER`；
6. `human-merge` 暂停和恢复；
7. 共享 Integration Branch 与 `integrate-and-verify`；
8. Spec 最终验收失败后创建修复工作；
9. Agent Run 崩溃恢复、幂等 Event 与状态冲突；
10. GitHub、GitLab、Local Markdown 三套 Tracker 的等价主路径。
