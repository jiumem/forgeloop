# 双 Reviewer 协议

## 独立评审轴

**Spec Reviewer** 检查产品目标、Actor、Acceptance Criteria、用户路径、错误/权限/空状态、范围遗漏和 Scope Creep。

**Standards Reviewer** 检查测试质量、公共 Seam、架构边界、ADR、项目规范和真实 Code Smell。Fowler Smell 默认 Advisory；只有违反明确标准、ADR、测试要求或造成实际风险时才 Blocking。

两轴不得共享上下文、读取对方结论、合并 Findings 或跨轴排序。

## 输入绑定

每轴读取同一固定 Base、Head、累计 Diff、Commit 列表、Ticket、Spec Revision 和 Coder 证据。输入不可读时返回 `REVIEW_BLOCKED`，不得虚假 PASS。空 Diff 或坏固定点在创建 Reviewer 前由 Scheduler 拒绝。

## Verdict

```yaml
axis: SPEC | STANDARDS
verdict: PASS | REPAIR_REQUIRED
base_commit: <sha>
head_commit: <sha>
spec_revision: <revision>
findings:
  - finding_id: <stable-id>
    disposition: BLOCKING | ADVISORY
    evidence: <file/hunk/command>
    violated_contract: <source>
    observed: <actual>
    expected: <required>
    repair_check: <observable check>
```

任一 Blocking Finding 必须 `REPAIR_REQUIRED`；无 Blocking 时 `PASS`，可以保留 Advisory。修复轮次沿用稳定 `finding_id`，检查完整累计 Diff、修复 Diff 与最新证据。

## 模型路由

Spec 默认强通用推理、`medium`；涉及权限、资金、隐私、安全、多角色、跨 Spec 或解释空间时升级。Standards 默认强代码推理、`medium`；涉及 Schema/迁移、公共接口、并发、基础设施、Wide Refactor、共享分支或弱 Seam 时升级。

首次失败提升相关轴推理强度；同一问题重复失败升至最高等级。不支持显式路由时用最强可用模型创建两个独立 Reviewer，并在 Event 记录降级。
