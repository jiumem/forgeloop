# Forgeloop Skill 套件重构验收证据

本文记录 `docs/plans/forgeloop-skill-suite-rebuild.md` 的可复查执行证据。所有命令均从仓库根目录运行；发布、推送、PR、Tag 与 Release 不在本次授权范围内。

## 实施基线

- `2.5.0` 源码 Commit：`a32f7a5d1eceace7215321dd7168dc7d07dac249`（Tag `v2.5.0`）。
- 上游 Matt Pocock Skills Commit：`391a2701dd948f94f56a39f7533f8eea9a859c87`。
- 实施分支：`codex/forgeloop-skill-suite-rebuild`。
- 活动源码目录：`plugins/forgeloop/skills/`；不创建目录级版本副本。

## 任务证据

### T0.1 建立实施基线与套件静态校验器

Task: T0.1
Entry: `python3 plugins/forgeloop/scripts/validate_suite.py --mode <baseline|development|release>`
Changed: 版本清单、只读套件校验器、正反单元 Fixture、Manifest 预发布版本。
Commands: 基线归档恢复校验；开发中间态校验；`python3 -m unittest plugins/forgeloop/tests/test_suite_validator.py`。
Fixtures: `2.5.0` 五 Skill 正例；开发态缺失清单；缺失 `SKILL.md`、名称不一致、Invocation Policy 错误、重复名称反例。
Result: PASS
Errors: 首轮发现基线完整 SHA 错误及动态导入未注册模块，均已修复并回归。
Out of scope: 未安装、未发布预发布版本。

### T0.2 建立固定上游导入映射与漂移校验

Task: T0.2
Entry: `python3 plugins/forgeloop/scripts/sync_upstream.py --dry-run|--check`
Changed: 18 项声明式映射、固定 Commit、机械替换清单、冲突安全 Overlay、幂等同步器。
Commands: dry-run、同步器单元测试、导入后 `--check`。
Fixtures: 正确 Commit、错误 Commit、正文篡改、重复写入。
Result: PASS
Errors: 错误 Commit 在任何写入前退出；篡改文件返回具体路径。
Out of scope: `recommend-initiatives` 与 `run-initiative` 不受导入器管理。

### M1 上游能力与用户入口

Task: T1.1
Entry: `$setup-forgeloop`。
Changed: GitHub/GitLab/Local 模板、Integration Policy、认证/权限停止、旧历史只读检测。
Commands: 上游漂移校验、三个 Setup Fixture、`quick_validate.py`。
Fixtures: `setup-github`、`setup-gitlab`、`setup-local`。
Result: PASS
Errors: 认证或权限失败禁止回退与部分配置；缺少指令文件请求用户选择。
Out of scope: 不自动迁移 `docs/initiatives/**`。

Task: T1.2
Entry: `$grilling`、`$domain-modeling`、`$grill-with-docs`。
Changed: 继承逐问、事实调查与领域文档契约，补充不创建 Spec/Ticket/代码门禁。
Commands: 三 Skill `quick_validate.py`、上游漂移校验。
Fixtures: 高影响单问正例；未决问题与无术语变化边界。
Result: PASS
Errors: 未决问题保持未完成；无长期变化不写领域文档。
Out of scope: 不执行设计。

Task: T1.3
Entry: `$primary-source-research`、`$prototype`、`$wayfinder`。
Changed: 继承一手来源、可抛弃原型与 Map/Frontier 契约。
Commands: 三 Skill `quick_validate.py`、三 Tracker Wayfinder Fixture。
Fixtures: `wayfinder-github`、`wayfinder-gitlab`、`wayfinder-local`。
Result: PASS
Errors: 坏依赖或能力缺失明确回退/停止；一次只 Claim 一张。
Out of scope: 不把单会话问题膨胀为 Map。

Task: T1.4
Entry: `$to-spec`、`$to-tickets`。
Changed: 继承 Spec 模板、垂直切片、Wide Refactor 与批准门禁；映射执行入口。
Commands: 两 Skill `quick_validate.py`、三 Tracker Publish Fixture。
Fixtures: `publish-github`、`publish-gitlab`、`publish-local`。
Result: PASS
Errors: `CONTEXT_INSUFFICIENT` 与发布权限失败均保持未发布。
Out of scope: 不创建 `PLAN.md` 或 `LEDGER.md`。

Task: T1.5
Entry: `$triage`。
Changed: 继承发现桶、推荐后等待、状态机与 Out-of-Scope 区分。
Commands: `quick_validate.py`、引用校验。
Fixtures: 未分类/等待信息新回复正例；状态冲突与权限失败边界。
Result: PASS
Errors: 状态冲突先请求方向；写入前确认避免静默部分成功。
Out of scope: 不自动应用推荐。

Task: T1.6
Entry: `$tdd`、`$codebase-design`。
Changed: 原样继承 Red-Green、公共 Seam、Deep Module 统一词汇。
Commands: 两 Skill `quick_validate.py`、上游漂移校验。
Fixtures: 公共行为测试正例；实现细节耦合与 Scope 扩大反例。
Result: PASS
Errors: 未确认 Seam 时停止写测试。
Out of scope: Primitive 不自行扩大 Ticket。

Task: T1.7
Entry: `$diagnosing-bugs`、`$resolving-merge-conflicts`。
Changed: 继承诊断反馈环并增加只诊断授权；冲突 Skill 使用封板安全 Overlay。
Commands: 两 Skill `quick_validate.py`、Overlay 漂移校验。
Fixtures: 可复现诊断正例；意图不兼容 `CONTRACT_BLOCKER`。
Result: PASS
Errors: 无反馈环、破坏性操作或结构冲突均明确停止。
Out of scope: 只诊断请求不修复代码。

Task: T1.8
Entry: `$review-change <fixed-point>`。
Changed: 继承独立 Spec/Standards 双轴并补充固定点、空 Diff 与只读门禁。
Commands: `quick_validate.py`、上游漂移校验。
Fixtures: 双轴报告正例；坏引用、空 Diff、无 Spec 边界。
Result: PASS
Errors: 无 Spec 返回 `SPEC: NOT_AVAILABLE`，不伪造 Verdict。
Out of scope: 不修改代码或 Tracker。

Task: T1.9
Entry: `$recommend-initiatives`、`$improve-codebase-architecture`。
Changed: 使用 `init_skill.py` 重建只读推荐器；架构扫描增加证据与临时目录边界。
Commands: 两 Skill `quick_validate.py`、空结果/部分来源门禁检查。
Fixtures: 3–5 个跨类别候选；缺少目标、无 Deepening Opportunity、Tracker 不可访问边界。
Result: PASS
Errors: 空结果与部分来源显式输出，不虚构路线图。
Out of scope: 不写 Recommendations、Spec、Ticket 或生产代码。

Task: T1.10
Entry: `$handoff`。
Changed: 原样继承 OS 临时目录、正式产物引用与敏感信息清理。
Commands: `quick_validate.py`、上游漂移校验。
Fixtures: 新会话续接正例；凭据与重复 Tracker 状态反例。
Result: PASS
Errors: 必需上下文不足时明确列出缺口。
Out of scope: 不建立第二真理源。

Task: T1.11
Entry: `$ask-forgeloop` 与 20 份 `agents/openai.yaml`。
Changed: Router 仅覆盖正式入口；元数据由 Skill Creator 生成器和声明式清单刷新。
Commands: `refresh_skill_metadata.py --check`、19 次 `quick_validate.py`、套件开发态校验。
Fixtures: 11 个显式调用 Policy、9 个模型调用 Policy、20 个包含 `$skill-name` 的 Prompt。
Result: PASS
Errors: 未发布入口与旧 Skill 引用被移除。
Out of scope: M1 不替换旧 `run-initiative`，只保留到 M2 闭环通过。

### M2 `run-initiative` 执行内核

Task: T2.1
Entry: `$run-initiative <local-spec-ref>`。
Changed: 使用 `init_skill.py` 重建入口与八份一层协议，完成 Local 单 Ticket 主循环。
Commands: `quick_validate.py`、运行协议校验、Fixture 校验。
Fixtures: `happy-local`、空 Frontier、坏引用、脏工作区、Reviewer 不可用。
Result: PASS
Errors: 所有预检失败均在 Claim/Coder 前停止。
Out of scope: 不写 `PLAN.md`、`LEDGER.md` 或执行状态标签。

Task: T2.2
Entry: `$run-initiative <github-spec-ref>`。
Changed: `gh` Frontier、Claim Comment、Events、PR/Commit、关闭与两种集成策略。
Commands: Runtime 契约校验、`happy-github` Fixture。
Fixtures: Happy Path、权限/认证、Branch Protection、Required Checks、human-merge。
Result: PASS
Errors: 远端失败保持 Open，禁止回退 Local。
Out of scope: 不额外触发完整 CI。

Task: T2.3
Entry: `$run-initiative <gitlab-spec-ref>`。
Changed: `glab` Frontier、Claim Note、Events、MR/Commit、Free/Premium Blocking 与关闭。
Commands: Runtime 契约校验、`happy-gitlab` Fixture。
Fixtures: Happy Path、认证/权限、Protected Branch、能力回退。
Result: PASS
Errors: 平台失败可定位且不回退 Tracker。
Out of scope: 不承诺 Other Tracker。

Task: T2.4
Entry: 任一 Reviewer `REPAIR_REQUIRED`。
Changed: 原 Coder/Reviewer 复用、双轴独立重审、稳定 Finding、模型升级与修复预算。
Commands: 运行协议校验；Spec、Standards、双轴、预算、合约 Fixture。
Fixtures: `spec-repair`、`standards-repair`、`dual-repair`、`repair-exhausted`、`contract-blocker`。
Result: PASS
Errors: 同 Finding 两次或 Ticket 三次失败暂停；合约路径不耗普通预算。
Out of scope: 用户不能覆盖 Reviewer PASS 门禁。

Task: T2.5
Entry: 双 PASS 后按 Integration Policy 集成。
Changed: 独立/共享 Branch、integrate-and-verify、human-merge 恢复、冲突重审。
Commands: `human-merge`、`shared-integration` Fixture。
Fixtures: 人工合并暂停/恢复、共享分支、PR/MR 关闭未合并、Base/Head 变化。
Result: PASS
Errors: 冲突改变代码或 Base/Head 变化使 Verdict 失效。
Out of scope: 自动集成不含部署、发布或迁移执行。

Task: T2.6
Entry: 当前 Spec 所有 Tickets 通过。
Changed: 简单单 Ticket Reviewer 复用与全新 Spec Acceptance 分流。
Commands: Acceptance 协议校验、Spec 失败 Fixture。
Fixtures: `happy-local`、`spec-acceptance-fail`。
Result: PASS
Errors: 验收失败保持 Spec Open 并创建正式修复工作。
Out of scope: 不改写已关闭 Ticket 的历史 Verdict。

Task: T2.7
Entry: `$run-initiative <spec-ref...>` 或父 Initiative 引用。
Changed: 多 Spec 预览、持久化父 Item、成员变更确认与全新跨 Spec Acceptance。
Commands: `multi-spec`、Initiative 失败 Fixture。
Fixtures: `multi-spec`、`initiative-acceptance-fail`。
Result: PASS
Errors: 跨 Spec 失败保持父 Item Open 并创建修复工作。
Out of scope: 单 Spec 不创建多余父对象。

Task: T2.8
Entry: 新运行、并发 Claim 或沿原 Run ID 恢复。
Changed: 严格串行、重新查询 Frontier、Event Schema、幂等、Supersede 与恢复冲突。
Commands: Event 协议校验、并发与崩溃恢复 Fixture。
Fixtures: `blocking-graph`、`concurrent-claim`、`crash-recovery`、`empty-frontier`。
Result: PASS
Errors: 原生事实冲突返回 `RECOVERY_CONFLICT`；不用短 TTL。
Out of scope: Initiative 内不主动并行 Frontier。
