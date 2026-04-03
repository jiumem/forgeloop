# Anchor-Sliced Dispatch Optimization 设计文档（Design Doc）

<!-- forgeloop:anchor document-card -->
## 1. 文档卡片（Document Card）
### 1.1 状态与阶段（Status And Stage）
- 状态：`sealed`
- 阶段：`Design Doc`

### 1.2 Initiative 类型（Initiative Type）
- 类型：`governance convergence + workflow contract refactor`
- Gap Analysis Requirement: `required`

### 1.3 主要读者（Primary Readers）
- `design_reviewer`
- 下游 `gap_reviewer` 与 `total_task_doc_reviewer`
- 后续消费 sealed planning truth 的 `run-planning`、`run-initiative`、`planner`、`coder`、runtime reviewers

<!-- forgeloop:anchor requirement-baseline -->
## 2. 需求基线（Requirement Baseline）
### 2.1 问题陈述（Problem Statement）
当前 Forgeloop 的 planning / runtime 循环以正式文档为真理源，但热路径读取仍偏向整文重读或大包分发。结果是 token 成本高、恢复时容易因上下文过宽或 handoff 边界不稳而降低收敛性。现有 rolling docs 已有结构化 block 与 handoff 机制，但缺少跨 planning docs、runtime docs、review baselines 的稳定 machine-readable text anchors，也缺少以 anchor 为核心的最小分发默认面。

### 2.2 目标结果（Intended Outcome）
建立一个以稳定 text anchors 为地址层、以最小 anchor-based dispatch packet 为默认输入面、以正式文档为唯一权威源、以 derived effective views 为辅助投影的目标态，使正常执行只读当前需要的切片，而冷启动、runtime rebuild、anchor 合法性 / 冲突场景仍能安全退回整文读取。

### 2.3 成功标准（Success Criteria）
- planning 与 runtime 的正常热路径可以依赖 `doc_ref + anchor_ref + 最小必要切片` 工作，而不是默认整文重读。
- 任何 derived slice / current-effective view 都可从正式文档重建，且不成为平行真理源。
- rolling docs 的同 handoff 重复结果、supersede 规则、当前有效视图可被 machine-resolve，而不靠人工解释。
- 冷启动、runtime rebuild、anchor 冲突或 anchor 非法时，系统仍能通过整文读取恢复，不因切片化而丢失恢复能力。

### 2.4 硬约束（Hard Constraints）
- 单一真理源必须保留在现有正式 planning artifacts、`Planning State Doc` / `Global State Doc`、以及 rolling docs；不得再引入平行权威模型。
- 现有 stage contract、rolling-doc contract、runtime routing vocabulary 的法位不能被 packet 摘要或派生缓存替代。
- 新设计必须同时优化 token 效率与 recovery stability；只降 token、不提升恢复稳定性，不算达标。
- 下游不得依赖目录猜测、聊天记忆或非正式摘要来恢复当前 handoff / round / review target。

<!-- forgeloop:anchor design-verdict-summary -->
## 3. 设计裁决摘要（Design Verdict Summary）
### 3.1 主要矛盾（Primary Contradiction）
系统需要显著缩小下游 dispatch 输入面，才能降低 token 成本并减少恢复漂移；但当前唯一可信的上下文又主要存在于较长的正式文档与 append-only rolling docs 中，缺少稳定地址层时，安全做法往往只能重读整文。

### 3.2 胜出切法（Winning Cut）
胜出切法是：在不改变正式文档法位的前提下，为 planning docs、runtime docs、review baselines 建立稳定 machine-readable text anchors，把 dispatch packet 默认收缩为 `权威 doc refs + anchor selectors + 当前最小必要切片`，并允许从 rolling docs 派生 current-effective views 作为读取优化层；整文读取只保留给 cold start、runtime rebuild、anchor legality failure、anchor conflict。

### 3.3 下游绑定影响（Downstream Binding Effects）
- 下游 planning 与 runtime packet 从“整文上下文为默认”切换为“anchor-addressed minimal packet 为默认”。
- rolling docs 后续必须支持 attempt-aware slicing、handoff-scoped reviewer reads、same-handoff duplicate result supersede、以及 current-effective derived view。
- `Gap Analysis Doc` 需要显式覆盖现有 contracts / docs / skills 与目标 anchor topology 之间的结构缺口，而不能在 `Total Task Doc` 里边执行边补。

<!-- forgeloop:anchor scope-and-non-goals -->
## 4. 范围与非目标（Scope And Non-Goals）
### 4.1 范围内（In Scope）
- 规划侧正式文档、planning rolling docs、runtime control docs、runtime rolling docs、review baselines 的 anchor 化地址层。
- 默认 dispatch packet 的最小化规则、整文读取例外规则、anchor legality / conflict 处理边界。
- rolling docs 的 current-effective / handoff-scoped / attempt-aware 切片语义。
- 为下游 Gap / Plan 阶段锁定单一权威线：什么是正式源，什么只是派生投影。

### 4.2 范围外（Out Of Scope）
- 具体 Milestone / Task 拆分。
- rollout 时序、迁移执行账本、PR 路径、脚本实现教程。
- 与 anchor 切片无直接关系的 runtime 算法优化或 agent prompt 润色。
- 把现有 markdown 正式文档替换成数据库、服务端状态机或新的长期持久层。

### 4.3 明确非目标（Explicit Non-Goals）
- 不是为了让 dispatch packet 成为新的权威文档。
- 不是为了取消 cold start / rebuild 场景的整文读取能力。
- 不是为了重写 `G1 / G2 / G3`、`R1 / R2 / R3`、或 planning stage routing 的法位。
- 不是为了让 derived views、cache、sidecar index 获得比正式文档更高的恢复优先级。

<!-- forgeloop:anchor target-state-design -->
## 5. 目标态设计（Target-State Design）
### 5.1 核心拓扑（Core Topology）
目标态分四层：

1. 权威层：`Design Doc` / `Gap Analysis Doc` / `Total Task Doc`、`Planning State Doc`、`Global State Doc`、planning rolling docs、runtime rolling docs 继续作为唯一正式真理源。
2. 地址层：每个会被下游精确读取的正式表面都暴露稳定 machine-readable anchors，用于定位 section、contract block、round/handoff candidate、current-effective projection input。
3. 投影层：从权威层派生 current-effective / handoff-scoped / attempt-aware slices，用于热路径读取优化；该层永远可丢弃并从权威层重建。
4. 分发层：dispatch packet 只携带当前角色所需的最小 authoritative refs、anchor selectors、以及必要切片；不再默认携带整篇正文。

### 5.2 关键表面（Key Surfaces）
- Anchor identity surface：anchor 必须在所属正式文档内唯一、可机器解析、可稳定引用；同一逻辑对象不能同时存在多个等价主 anchor。
- Anchor resolution surface：给定 `doc_ref + anchor selector`，系统必须得到唯一目标、显式冲突、或显式缺失三种结果之一。
- Rolling-doc effective surface：同一 round / handoff 的“当前有效事实”由滚动文档的 freshness law 推导，不通过覆写历史获得。
- Reviewer handoff surface：reviewer 默认读取当前 handoff 对应的最小切片；只有 anchor 非法、冲突、或判定需要更大半径时才升级到整文。
- Dispatch contract surface：packet 必须显式携带权威 ref 与 anchor 定位，不允许依赖目录布局或记忆推断当前目标。

### 5.3 关键路径与转换（Critical Paths And Transitions）
- 正常热路径：绑定当前 active object 或 planning stage -> 解析当前权威 doc refs -> 解析当前 anchors 与 current-effective slice -> 发送最小 packet -> 追加新正式 block -> 刷新派生有效视图。
- reviewer 热路径：从当前 handoff 定位 review target 与必要 supporting anchors -> 只读该 handoff 的最小切片 -> 产出结果 -> freshness law 选出当前有效 verdict。
- 恢复路径：当进入 cold start、runtime rebuild、anchor legality failure、anchor conflict 时，先整文读取权威源，再重建 anchor legality 与 current-effective projections，然后恢复最小分发。
- supersede 路径：同一 handoff 下若出现重复结果，以 rolling doc 中最新追加且匹配 `round + handoff_id + review_target_ref` 的 block 为当前有效结果；旧结果保留为历史，不得删除。

### 5.4 边界划分与实现自由度（Boundary Allocation And Implementation Freedom）
以下内容在 Design 层已经固定：

- 正式 planning artifacts、state docs、rolling docs 仍是唯一权威源；anchor、slice、derived view 都只能建立在它们之上。
- planning docs 在正常热路径不再默认整文读取；整文读取只保留给 cold start、runtime rebuild、anchor legality failure、anchor conflict。
- 默认 dispatch packet 必须是 anchor-addressed 且最小化的；“为了稳妥先塞整文”不再是合法默认策略。
- rolling docs 必须演进到支持 attempt-aware slicing、handoff-scoped reviewer reads、same-handoff supersede、以及 derived current-effective views。
- anchor 缺失、冲突、歧义、过期或无法合法解析时，系统必须升级为整文恢复或显式停止；不得猜测性继续。
- `Gap Analysis Requirement` 固定为 `required`，因为当前 repo 已有多套 planning/runtime 合同与 rolling-doc 规则，需要先做结构缺口与迁移面分析。

以下内容保留实现自由度：

- anchor 的具体语法、命名细则、嵌入 markdown 的具体形式。
- anchor parser、projection builder、packet builder 放在何处实现，只要不改变权威边界。
- derived view 的物化方式可以是临时内存、临时文件、或明确标记为非权威的辅助产物；但它必须可重建、可失效、不可抢占正式源法位。
- 不同消费者的 packet 字段名与切片粒度可以调整，只要仍满足“显式权威 ref + anchor address + 最小必要上下文”的固定边界。

<!-- forgeloop:anchor key-decisions -->
## 6. 关键决策与被否定方案（Key Decisions And Rejected Alternatives）
### 6.1 已封板决策（Sealed Decisions）
- 采用“anchor 地址层 + 最小 dispatch packet + derived effective views”的组合切法，而不是单独做 packet 压缩。
- 不新增第二真理源；任何 index、cache、slice、projection 都从正式文档导出，并在冲突时让正式文档获胜。
- rolling docs 的 append-only / update-only 合同不因切片化而改变；当前有效视图通过推导获得，而不是通过回写历史块获得。
- 设计阶段只锁定目标拓扑与法位边界，不在此文档内展开迁移台账或执行拆分。

### 6.2 被否定方案（Rejected Alternatives）
- 继续以整文读取作为默认派发方式，仅在极少场景手动摘录。
- 建一个外部 index / 数据库 / sidecar schema 作为主查询面，再把 markdown 文档降为备份。
- 让每次 dispatch 依赖人工编写的 packet 摘要或聊天记忆，而不要求稳定 anchor。
- 仅依赖行号、文件偏移或临时字符串匹配做切片定位。

### 6.3 为什么胜出切法会赢（Why The Winning Cut Wins）
它同时解决两个主要压力：一方面通过稳定地址层把热路径输入压到最小必要范围，直接降低 token 与无关上下文噪声；另一方面保留正式文档的唯一权威地位和整文恢复通道，避免为了省 token 引入新的恢复脆弱点。相比把状态搬去外部索引，本切法对现有 contract 侵入更低、可逆性更好，也更符合 Forgeloop 当前“正式文档 + machine blocks + derived views”的演化方向。

<!-- forgeloop:anchor correctness-surface -->
## 7. 正确性表面（Correctness Surface）
### 7.1 不变量（Invariants）
- 任一被下游消费的 anchor 引用都必须解析到唯一正式目标，或明确进入冲突 / 缺失状态。
- 任何 current-effective / handoff-scoped 派生视图都必须是对应正式文档的可重建投影，不得引入额外事实。
- 当前有效 handoff / review result 的判定必须继续服从既有 rolling-doc freshness law，而不是由 packet 作者自由解释。
- control-plane docs 继续只承载最小控制状态；正文级语义仍留在正式 artifacts 与 rolling docs。

### 7.2 契约边界（Contract Boundaries）
- stage reference 仍定义 artifact shape；rolling-doc contract 仍定义 communication plane；anchor 层只负责地址化与切片读取，不重写这两类合同。
- sealed `Design Doc` 中的 `Gap Analysis Requirement` 继续是 planning 路由唯一真理源；anchor 体系不能绕过这一点。
- `Planning State Doc` / `Global State Doc` 不因为切片化而扩张成摘要仓库或索引仓库。
- reviewer、planner、coder、runtime supervisors 只能消费被明确绑定的 refs / anchors；隐式发现不是合法契约。

### 7.3 失败与安全红线（Failure And Safety Lines）
- anchor 非法、重复、漂移、冲突、或无法证明新旧映射合法时，必须停止最小分发并升级为整文恢复或显式阻塞。
- 若 derived view 与权威文档不一致，以权威文档为准并立即使派生结果失效。
- 任何 packet 若只提供切片文本而不提供对应权威 ref / anchor address，都视为非法输入。
- 不允许为了节省 token 跳过 freshness、handoff 匹配、或 current-effective 选择规则。

### 7.4 允许的实现变体（Allowed Implementation Variation）
- anchor 可以绑定 section、formal block、handoff candidate、或更细粒度对象，只要唯一性与稳定性可验证。
- legality check 可以在 parser、builder、dispatcher、或 reviewer admission 阶段触发，只要失败会回到权威恢复路径。
- derived views 可以按 planning / task / milestone / initiative 消费面分别定制，只要它们都从同一正式源推导。
- packet 可以为不同角色裁剪不同字段集合，只要不突破 `5.4` 中已固定的边界。

<!-- forgeloop:anchor residual-risks -->
## 8. 残余风险与后续事项（Residual Risks And Follow-Ups）
### 8.1 可接受残余风险（Accepted Residual Risks）
- 初期 anchor 化会提高文档结构复杂度，并需要额外解析 / 校验逻辑。
- 在混合新旧文档并存阶段，部分路径仍可能暂时回退到整文读取。
- first-pass anchor granularity 可能需要在真实 dispatch 数据后再调细，但这不改变当前设计切法。

### 8.2 后续事项（Follow-Ups）
- 在 `Gap Analysis Doc` 中逐一映射当前 planning / runtime docs、skills、review baselines 与目标 anchor topology 的缺口。
- 在 `Total Task Doc` 中定义 Milestone / Task 执行拆分、验证矩阵、迁移顺序、以及回滚 / 兼容处理。
- 建立 anchor legality、slice derivation、supersede resolution、以及 rebuild fallback 的测试与样例集。

### 8.3 升级触发器（Escalation Triggers）
- 如果发现某类正式文档无法在不破坏其权威边界的前提下承载稳定 anchors，需要回到设计层重切。
- 如果最小 packet 在 reviewer 或 coder 场景下反复无法提供足够正确上下文，且问题不是 anchor 粒度选择能解决的，需要回到设计层。
- 如果 derived views 只有在被升级成新的长期权威层时才能工作，当前设计失效，必须升级裁决。
- 如果 anchor 化要求打破 repo-root-relative refs、current contract snapshot law、或 rolling-doc freshness law，也必须回到设计层。
