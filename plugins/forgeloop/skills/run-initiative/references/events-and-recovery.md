# Event 与恢复协议

## 事件集合

`RUN_CLAIMED`、`CODER_RESULT`、`REVIEW_RESULT`、`INTEGRATION_RESULT`、`RUN_PAUSED`、`RUN_CANCELLED`、`RUN_RESUMED`、`EVENT_SUPERSEDED`。

Reviewer 不可用使用 `RUN_PAUSED` 的 reason=`REVIEW_BLOCKED`；人工合并等待使用 reason=`READY_FOR_HUMAN_MERGE`。不创建互斥状态标签。

## 最小 Schema

```yaml
schema_version: "1"
run_id: <stable-id>
sequence: <monotonic-integer>
idempotency_key: <run-id:event:subject:revision>
event: <type>
previous_event: <id|null>
initiative_ref: <ref>
spec_ref: <ref>
ticket_ref: <ref|null>
base_commit: <sha|null>
head_commit: <sha|null>
target: <branch>
spec_revision: <revision>
repair_round: <integer>
model_capability: <level|null>
escalation_reason: <text|null>
evidence: <refs>
verdicts: <independent-axis-payloads>
timestamp: <tracker-server-time>
```

Event 发布后不编辑。相同幂等键已存在时读取并复用，不重复创建；错误通过指向原 Event 的 `EVENT_SUPERSEDED` 纠正，不改历史。

## 恢复

1. 读取 Tracker 原生状态、全部有效 Events、Branch/PR/MR/Commit 和 Merge 事实。
2. 按 Schema Version、Run ID、序号、previous link 与幂等键重建状态；忽略已被 Supersede 的解释，但保留历史。
3. 验证活动 Claim、Base/Head、Spec Revision、目标分支和两个 Verdict 仍有效。
4. 沿原 Run ID 追加 `RUN_RESUMED`，从最后一个已完成门禁继续，不重放已确认写入。

原生事实与 Events 冲突、序号分叉、重复有效 Claim、未知 Schema、Head/Base 变化或 Spec 实质修订时停止并报告 `RECOVERY_CONFLICT`。不得用短 TTL 推断长任务死亡；接管必须由确定性平台规则或用户裁决。
