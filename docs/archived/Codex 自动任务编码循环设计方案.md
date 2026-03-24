# **Codex 自动任务编码循环设计方案**

## 封面信息卡

| 字段       | 内容                                                                          |
| -------- | --------------------------------------------------------------------------- |
| **文档名称** | **Codex 自动任务编码循环设计方案**                                                      |
| **版本状态** | **v1.0 / Design Baseline**                                                  |
| **文档定位** | 面向产品负责人、技术负责人、自动化平台开发者的系统设计文档                                               |
| **核心目标** | 定义一套通用、可扩展、可审计的 Codex 自动编码—审查—回环系统                                          |
| **适用对象** | 已具备项目级规则与任务拆分能力的中长期开发项目                                                     |
| **上位关系** | 本文以下位实现视角承接《Codex 自动任务编码循环采用说明》                                             |
| **实现基础** | 基于 Codex CLI 非交互执行能力、项目级 `AGENTS.md` 指令机制、结构化结果输出与脚本编排能力构建 ([OpenAI开发者][1]) |

---

## 0. 文档定位

本文不是产品导读，也不是单纯的 CLI 参数笔记。

本文回答的是一个更硬的问题：

> **如何把 Codex 从“单次对话式编码助手”，收敛成一套可持续运行的自动任务执行系统。**

因此，本文的设计对象不是一次性的 prompt，而是一个**长期可演化的自动编码循环框架**。这个框架至少要满足四个条件：

第一，它必须能处理连续任务，而不是只处理离散请求。
第二，它必须有显式状态，而不是把流程记忆托付给人脑与聊天历史。
第三，它必须把“执行、审查、编排”三种权力解耦。
第四，它必须把自然语言输出降级为解释层，把结构化结果升级为执法层。

在 Codex 当前能力边界下，这样的设计是成立的。Codex CLI 本身可以在本地目录中读、改、运行代码；支持非交互 `codex exec` 用于脚本和 CI；支持 JSONL 事件流；支持把最终输出约束成指定 schema；支持 `AGENTS.md` 项目指令；也支持为不同任务定义不同模型和指令的 custom agents / subagents。换句话说，底层能力已经足以承载一套外部编排系统，真正需要设计的是**系统合同**而非“功能想象”。([OpenAI开发者][2])

---

## 1. 系统目标与非目标

### 1.1 系统目标

这套系统的目标，不是让 Codex“更会写代码”，而是让项目在连续任务开发中具备稳定吞吐。

从第一性原理看，连续编码任务的瓶颈通常不在模型 token，而在三类人为摩擦：**任务转述、结果搬运、状态记忆**。只要这些摩擦还靠人承担，哪怕底层模型再强，系统整体也会被人类同步成本卡住。因此，本系统的首要目标是把如下链路机械化：

> 任务装配 → 编码执行 → 结构化总结 → 审查裁决 → 自动回环 → 人类签字

围绕这个总目标，本文定义四个子目标：

| 子目标        | 解释                     |
| ---------- | ---------------------- |
| **吞吐提升**   | 减少人类在回环中的搬运与转述劳动       |
| **边界稳定**   | 让任务边界、完成定义、阻断条件保持结构化稳定 |
| **审计可追溯**  | 让每一轮执行、审查、状态跃迁都有对象化留痕  |
| **人机分工清晰** | 机器负责执行闭环，人类负责边界裁决与最终合入 |

---

### 1.2 系统非目标

任何自动化系统若不先定义非目标，最终都会因边界扩张而腐化。本文明确以下内容**不属于本系统目标**：

**它不是需求发现系统。**
若项目仍处于“到底做什么”的开放探索阶段，本系统不应介入。系统默认输入是**已被方案化、拆分化的任务**，而不是模糊需求。

**它不是第二套项目治理法。**
项目规则应由仓库级指令文件、团队约定、设计文档决定；本系统只消费这些规则，不重写这些规则。Codex 的 `AGENTS.md` 机制本身也是“读取与继承项目指令”，而不是代替项目治理。([OpenAI开发者][3])

**它不是无人值守的自动交付系统。**
系统会把人类从搬运劳动中抽离出来，但不会取消人类在法理冲突、架构品味、合入签字上的职责。

**它不是日志驱动系统。**
JSONL 事件流、自然语言总结、stdout/stderr 日志都只是观察材料；状态推进与自动裁决只依赖结构化模型。Codex 官方把 `--json` 描述为脚本消费事件流的方式，但并没有把事件流定义为高层业务真值；相反，`--output-schema` 才是最适合做稳定下游消费的出口。([OpenAI开发者][1])

---

## 2. 关键设计决策

本章给出系统封板级裁决。后文所有设计都从这些裁决推导。

### 2.1 真值源裁决：结构化对象高于自然语言

> **任务真值、执行真值、审查真值、编排真值，分别由四个结构化模型承担；自然语言与 JSONL 事件流只承担解释与观测职责。**

原因很简单。自然语言适合说明，但不适合执法。凡是把“任务是否完成”交给自由文本解释的系统，最终都会失去复现性与自动裁决能力。

---

### 2.2 编排裁决：Controller 默认 deterministic

> **Controller 的决策内核必须是规则驱动的状态机；LLM 仅用于结案总结、通知生成、以及少数歧义场景的辅助解释。**

这样设计不是为了“保守”，而是为了避免 controller 演化成第四个 reviewer。只要 controller 开始自由重判 findings、重写任务边界或自行发明下一任务，它就不再是调度器，而变成了新的不受约束的治理中心。

---

### 2.3 权力裁决：执行、审查、编排三权分立

> **Coder 只实现，Reviewer 只审查，Controller 只推进状态。**

这条看似简单，实际上是整套系统的根法。任何角色混权，都会直接导致上下文污染：

* coder 一旦拥有通过判定权，就会自然倾向于自证完成；
* reviewer 一旦拥有正式排产权，就会把局部问题放大成全局任务；
* controller 一旦拥有代码裁判权，就会重走第二套人工 review。

Codex 的 subagents / custom agents 能支持多角色并行与差异化配置，但角色能力的存在不等于角色边界天然正确，边界仍需由系统显式定义。([OpenAI开发者][4])

---

### 2.4 排产裁决：Reviewer 可建议，不可决定

> **Reviewer 可以同时给出“当前任务是否可晋级”与“下一任务候选建议”；正式排产必须由 Controller 结合任务依赖与阶段顺序二次确认。**

这是效率与稳定性的平衡点。这样既能提高吞吐，又不会把 reviewer 升格成项目经理。

---

### 2.5 停止条件裁决：自动回环必须有硬上限

> **自动回环受最大轮次、重复 findings、scope 冲突、法律冲突、依赖缺失五类条件约束。**

没有上限的回环不是自动化，而是语言表演。系统必须在“继续修复”与“升级人工”之间有清晰边界。

---

### 2.6 任务粒度裁决：默认单位是闭环，不是 patch

> **系统默认面向“单一现实接缝 / 单一验收闭环 / 单一任务边界”运行，而不是面向任意大小的代码片段。**

这意味着它适合 milestone 内的任务单元，不适合纯粹零碎的临时 patch。此裁决与前置采用文档保持一致。

---

### 2.7 Prompt 分层裁决：共享法则、角色职责、任务上下文分层注入

> **共享项目规则放在 `AGENTS.md`；角色差异放在角色级 developer instructions；每轮具体工作内容由 task packet 与 round context 注入。**

Codex 会在启动时构建指令链，按全局、项目、目录层级读取 `AGENTS.md`，并从根到当前目录合并。这个机制天然适合作为共享法则层，而不适合作为一次性任务上下文层。([OpenAI开发者][3])

---

### 2.8 默认安全裁决：最小权限优先

> **Coder 仅获得完成任务所需的最小写权限；Reviewer 默认只读；Controller 默认不写代码；高危绕过参数永不作为默认配置。**

Codex 官方明确说明 `codex exec` 默认在只读 sandbox 中运行，`--full-auto` 会切到 `workspace-write + on-request`，而 `danger-full-access` 与绕过 approvals/sandbox 只应在受控环境下使用。系统默认值必须沿着这个安全阶梯设计，而不能反其道而行。([OpenAI开发者][1])

---

## 3. 总体架构

### 3.1 架构总览

系统总图可以收敛为一句话：

> **任务由 `task_packet` 定义，执行由 `coder_result` 记录，审查由 `review_result` 裁定，推进由 `task_state` 统领。**

更具体地，链路如下：

```text
task_packet
  -> Controller 装配任务上下文
  -> Coder 执行并产出 coder_result
  -> Reviewer 审查并产出 review_result
  -> Controller 依据规则推进 task_state
  -> 必要时回环 / 升级人工 / 进入下一任务
```

从系统工程角度看，这是一个典型的**以状态机为中轴、以结构化对象为合同、以外部 agent runtime 为执行器**的架构。Codex CLI 处在执行器层，而不是控制器层。

---

### 3.2 角色协作图

| 角色             | 系统位置 | 读什么                                                     | 写什么                                 | 不得做什么   |
| -------------- | ---- | ------------------------------------------------------- | ----------------------------------- | ------- |
| **Controller** | 编排层  | task_packet / coder_result / review_result / task_state | task_state / summary / notification | 不直接裁判代码 |
| **Coder**      | 执行层  | task_packet / 项目代码 / 上轮 findings                        | coder_result / 代码变更                 | 不宣布任务通过 |
| **Reviewer**   | 审查层  | task_packet / coder_result / diff / 必要法源                | review_result                       | 不接管排产   |

这一表格不是排版装饰，而是接口设计的直接前提。后文的数据模型、提示词与状态跃迁，全部围绕这三列权责展开。

---

## 4. 角色分工与状态机

### 4.1 Controller

Controller 的本质不是“更聪明的 agent”，而是**系统操作员**。

它承担四类职责：任务装配、状态推进、下一任务选择、对人类可读的结案与通知。它不应深读全部代码，也不应直接形成新的 code review 结论。它真正依赖的是结构化对象，而不是自由文本。

因此，Controller 最佳形态通常不是“强推理大模型 + 自由 prompt”，而是**Python 状态机 + 轻量模型叙述层**。

---

### 4.2 Coder

Coder 的职责极其单纯：

> 在当前任务包边界内实现、清理、验证，并如实产出结果对象。

Coder 必须同时做两类事：**落位**与**清理**。这是从复杂项目中抽出的共性法则。任何只新增结构、不清理旧残影的自动化 patch，都会把技术债延后，而不是消除。

---

### 4.3 Reviewer

Reviewer 的价值不在“再写一遍总结”，而在**找出阻断性问题并把它们结构化**。

它必须优先回答三件事：

1. 当前任务是否还有 in-scope 的实质性 findings
2. 当前任务是否满足晋级条件
3. 若满足，最相邻的下一任务候选是什么

为了保持系统可执法，reviewer 的每个 finding 都必须显式给出：

* 严重级别
* 为什么重要
* 是否在当前 scope 内
* 依据的是哪条任务边界
* 是否阻断晋级

如果 reviewer 不承担这些结构化义务，它就只是另一份更长的自然语言评论。

---

### 4.4 状态机

系统状态机定义如下：

```text
NEW
-> CODING
-> REVIEWING
-> NEEDS_FIX
-> REVIEWING
-> REVIEW_CLEAN
-> HUMAN_REVIEW
-> DONE
```

异常出口为：

```text
ANY -> NEEDS_HUMAN_RULING
ANY -> BLOCKED
```

### 4.5 状态跃迁法则

| 当前状态         | 触发条件                                           | 下一状态               |
| ------------ | ---------------------------------------------- | ------------------ |
| NEW          | controller 首次调度                                | CODING             |
| CODING       | coder_result 产出                                | REVIEWING          |
| REVIEWING    | 有 blocking findings / checks 不通过 / must_do 未完成 | NEEDS_FIX          |
| NEEDS_FIX    | controller 回 coder                             | CODING             |
| REVIEWING    | 无阻断 findings 且晋级条件满足                           | REVIEW_CLEAN       |
| REVIEW_CLEAN | 需要人工最终审查                                       | HUMAN_REVIEW       |
| HUMAN_REVIEW | 人工批准                                           | DONE               |
| 任意状态         | 法律冲突 / loop 超限 / reviewer 无法可靠裁决               | NEEDS_HUMAN_RULING |

这张表的意义在于：系统推进依赖**显式条件**，而不是依赖对话气氛。

---

## 5. 四个核心数据模型

### 5.1 `task_packet`：任务真值模型

`task_packet` 是整个系统的源头。它定义当前任务是谁、依据什么、必须做什么、明确不做什么、需要哪些检查、何时算完成。

它的设计原则是：

> **尽量少，但必须足够执法。**

因此，它不记录执行日志，不承载审查结论，也不保存运行态状态。它只保留机器推进所需的最小边界信息。

#### 核心字段分层

| 层   | 典型字段                                  |
| --- | ------------------------------------- |
| 身份层 | task_id / title / phase / chain       |
| 法源层 | entry_docs                            |
| 范围层 | must_do / must_not_do / done_criteria |
| 依赖层 | depends_on / related_tasks            |
| 验证层 | required_checks                       |
| 推进层 | promotion_policy                      |

#### 关键裁决

* `task_packet` 是任务边界的唯一真值
* coder 与 reviewer 只能映射或反馈，不能重写它
* controller 的一切自动推进都必须回到它上面计算

---

### 5.2 `coder_result`：执行结果模型

`coder_result` 不是“任务是否通过”的证明，而是**当前这一轮执行客观做了什么**的记录。

它至少要覆盖五个面：

| 面   | 内容                        |
| --- | ------------------------- |
| 代码面 | 改了哪些文件                    |
| 法位面 | 收正了哪些接口 / seam / contract |
| 清理面 | 删了哪些兼容壳 / 旧命名 / 旧路径       |
| 验证面 | 跑了哪些检查、哪些跳过               |
| 边界面 | 哪些相邻内容刻意未做                |

这一“边界面”尤其关键。因为复杂项目里最大的腐化源头之一，就是 coder 总爱以“顺手优化”为名扩大任务边界。

#### 关键裁决

* `coder_result` 可以声明“我完成了什么”，不能宣布“任务已通过”
* 未执行的检查必须显式写明原因
* 相邻内容未做不是缺陷，而是合同的一部分

---

### 5.3 `review_result`：审查结果模型

`review_result` 是自动回环成立的核心。
它必须能支撑 controller 做三类动作：继续修、允许晋级、升级人工。

因此，它至少要包含四个区块：

| 区块                          | 作用         |
| --------------------------- | ---------- |
| `findings`                  | 记录结构化问题    |
| `current_task_verdict`      | 说明当前任务总体结论 |
| `promotion_readiness`       | 说明是否具备晋级条件 |
| `next_task_recommendations` | 提供候选而非命令   |

#### finding 的法定字段

一个合格 finding 至少应当同时包含：

* `finding_key`
* `severity`
* `summary`
* `why_it_matters`
* `in_scope`
* `scope_basis`
* `blocks_promotion`

少任何一项，controller 的自动裁决都会变弱。

#### 关键裁决

* Reviewer 关注的是**实质性问题**，不是风格偏好
* Reviewer 可以建议下一任务，但不能直接决定调度
* “看不清”必须诚实地输出 `needs_human_ruling`，而不是用模糊措辞掩盖不确定性

---

### 5.4 `task_state`：编排运行态模型

`task_state` 是 controller 的工作台对象。
它不定义法律，不记录代码细节，而是记录：

* 任务现在在哪个状态
* 已经回环多少轮
* 当前绑定了哪一轮 coder/reviewer 结果
* controller 下一步准备做什么
* 是否要通知人类
* 当前 closure summary 是什么

#### 关键意义

没有 `task_state`，系统就只有一堆静态对象；
有了 `task_state`，系统才真正变成**状态机**。

它的本质作用，是把“项目正在发生什么”从人脑中剥离出来，落成机器可读的现实。

---

## 6. 两层接口设计

### 6.1 外部接口：自动化脚本对外接口

这一层是你自己的系统接口，不是 Codex 的接口。
它决定系统如何被任务调度器、命令行工具、CI 或人类用户调用。

建议最小接口集如下：

| 接口                                | 作用                 |
| --------------------------------- | ------------------ |
| `create_task(task_packet)`        | 初始化任务与 task_state  |
| `run_coder(task_id, round_no)`    | 触发 coder 执行        |
| `run_reviewer(task_id, round_no)` | 触发 reviewer 审查     |
| `advance_state(task_id)`          | 应用 controller 规则推进 |
| `approve_human_review(task_id)`   | 人工签字并结案            |
| `send_notification(task_id)`      | 发送关键事件通知           |

这些接口都应满足两个约束：**幂等可设计**、**返回结构化对象**。
自动化系统最大的敌人之一，是“函数调用成功了，但没有稳定结果对象”。

---

### 6.2 内部接口：Codex CLI 适配接口

Codex CLI 处在执行器层。对系统来说，它最关键的能力是：

* 可以用 `codex exec` 进行脚本化非交互执行；
* 可以用 `codex exec resume` 续跑会话；
* 默认只读 sandbox，可显式提升权限；
* 可以输出 JSONL 事件流；
* 可以通过 `--output-schema` 约束最终输出；
* CLI flag 与 `-c key=value` 覆盖会优先于配置文件默认值。([OpenAI开发者][1])

#### 适配器抽象

业务层不应直接散落 `subprocess.run()`。
应该封装为一个稳定抽象，例如：

| 方法                       | 说明                 |
| ------------------------ | ------------------ |
| `exec(...)`              | 新开一次非交互运行          |
| `resume(...)`            | 续跑已有线程             |
| `parse_events(...)`      | 解析 JSONL 仅供日志与调试   |
| `read_final_output(...)` | 读取 schema 约束后的最终结果 |

#### 稳定依赖与刻意不依赖

> **稳定依赖：最终 schema 输出。**
> **弱依赖：JSONL 事件流。**

Codex 官方明确说明 `--json` 会把 stdout 变为 JSONL 事件流，包含 `thread.started`、`turn.started`、`turn.completed`、`turn.failed`、`item.*`、`error` 等事件。这个能力非常适合做可观察性与调试。
但高层业务裁决不应依赖这些内部事件细节，而应只依赖最终结构化输出。([OpenAI开发者][1])

---

## 7. 模型、提示词与默认安全配置

### 7.1 配置分层原则

整个系统的配置必须分层，否则 prompt 很快会漂。

| 层      | 承担什么                                                   |
| ------ | ------------------------------------------------------ |
| 共享规则层  | 项目级 `AGENTS.md`                                        |
| 角色职责层  | controller / coder / reviewer 的 developer instructions |
| 任务上下文层 | task_packet + round context                            |
| 运行参数层  | model / reasoning / sandbox / approval                 |

Codex 会按目录层级发现并合并 `AGENTS.md`，这非常适合承担共享规则层；同时 Codex 也支持 custom agents / subagents，为不同 agent 指定不同 instructions 与模型配置，这适合作为角色职责层。([OpenAI开发者][3])

---

### 7.2 模型默认配置

本文给出推荐默认值，而非唯一值。

| 角色         | 默认模型 | 默认推理强度       | 原因                |
| ---------- | ---- | ------------ | ----------------- |
| Controller | 轻量模型 | low / medium | 以状态推进与总结为主，不深读代码  |
| Coder      | 主力模型 | medium       | 负责多文件实现、清理与验证     |
| Reviewer   | 主力模型 | high         | 负责找边界问题、阻断问题与晋级判断 |

Codex 当前支持为 custom agents 指定不同模型与配置，也支持通过 CLI `--model` 与 `-c key=value` 覆盖配置。系统建议把关键配置显式放在调用层，而不是完全依赖全局默认文件。([OpenAI开发者][5])

---

### 7.3 提示词职责分离

三角色提示词应当是**职责合同**，而不是文学风格模板。

#### Controller 提示词应强调

* 你不判代码，只推进状态
* 有规则时优先规则
* reviewer 的下一任务建议不是命令
* 输出只允许是结构化结果或结案文字

#### Coder 提示词应强调

* 只处理当前 task_packet
* 必须同时完成落位与清理
* 必须如实填写未做项与检查执行情况
* 不得自称任务已通过

#### Reviewer 提示词应强调

* 只找实质性 findings
* findings 必须结构化
* 下一任务只能给建议
* 看不清就升级人工，不得用模糊措辞代替结论

---

### 7.4 默认安全配置

默认安全配置必须遵守最小权限原则。

| 角色         | 默认 sandbox      | 默认 approval               | 说明        |
| ---------- | --------------- | ------------------------- | --------- |
| Controller | read-only       | never                     | 通常无需代码写权限 |
| Coder      | workspace-write | on-request / 自动化受控环境下最小可写 | 仅写当前工作区   |
| Reviewer   | read-only       | never                     | 只读审查，禁止修改 |

Codex 官方对默认只读、安全提升路径、`--full-auto`、`danger-full-access` 和 `--yolo` 的风险提示都非常明确，因此系统默认配置必须沿官方安全阶梯设计，而不能把危险模式当常态。([OpenAI开发者][1])

---

## 8. 默认执行流程

### 8.1 任务启动

系统接收到 `task_packet` 后，controller 创建 `task_state`，状态置为 `NEW`。此时尚未发生代码动作，只发生合同装配。

### 8.2 首轮编码

controller 读取：

* 共享规则
* 角色 prompt
* task_packet
* 当前工作树上下文

然后调用 Codex CLI 执行 coder。由于 `codex exec` 正是为脚本与 CI 设计的非交互入口，这一步天然适合外部控制器驱动。([OpenAI开发者][1])

coder 完成后，产出 `coder_result` 并绑定到 `task_state`。

### 8.3 首轮审查

controller 再调用 reviewer，输入至少包括：

* task_packet
* coder_result
* 当前 diff
* 必要法源摘录

reviewer 输出 `review_result`。

### 8.4 自动回环

controller 应用 deterministic 规则：

* 若有 in-scope blocking findings → `NEEDS_FIX`
* 若 checks 未通过 → `NEEDS_FIX`
* 若 must_do 未完成 → `NEEDS_FIX`
* 若 reviewer 无法可靠裁决 → `NEEDS_HUMAN_RULING`
* 若 clean 且 ready → `REVIEW_CLEAN`

### 8.5 人工审查

系统进入 `REVIEW_CLEAN` 后，通知人类进入架构性审查。这里的人类不是来搬运 review，而是来做**自动化无法承担的最终判断**。

### 8.6 结案与下一任务

人工批准后，`task_state -> DONE`。
此时 controller 可读取 reviewer 的 `next_task_recommendations`，结合 DAG、依赖、阶段顺序与容量策略，决定是否选择下一任务。

---

## 9. Mock 与测试设计

### 9.1 为什么必须单列 Mock

这套系统并不是“写几个 prompt 然后跑一跑”就能稳定的。
它是一个状态机系统。状态机系统最大的工程风险，不在模型输出差一点，而在**状态推进不一致、回环条件判断错误、边界对象漂移**。

因此，mock 不是附属物，而是系统设计的一部分。

---

### 9.2 Mock 分层

建议 mock 分三层：

| 层    | 模拟什么                                      | 用途                 |
| ---- | ----------------------------------------- | ------------------ |
| 进程层  | CLI exit code / stdout / stderr / 输出文件存在性 | 测试调用器与错误处理         |
| 事件流层 | JSONL 事件                                  | 测试日志与观测链           |
| 结果层  | coder_result / review_result 最终 JSON      | 测试 controller 业务裁决 |

其中，真正的业务真值测试应集中在**结果层**。

---

### 9.3 最小测试场景集

至少覆盖以下场景：

* coder 成功，reviewer clean
* reviewer 存在 P1 且 in-scope blocking finding
* reviewer clean 但 blocking checks 未通过
* reviewer `needs_human_ruling`
* reviewer 推荐下一任务但依赖未满足
* review loop 轮次超限
* coder 声称完成但 must_do 与结果不一致

### 9.4 为什么不把 JSONL 事件当主测试对象

因为事件流适合观测过程，不适合作为业务裁决真值。
测试应尽量围绕最终 schema 产物设计，这样系统面对 Codex 运行时细节变化时仍能保持稳定。

---

## 10. 最佳默认配置

### 10.1 仓库布局建议

```text
repo/
  AGENTS.md
  .codex/
    prompts/
      controller.system.md
      coder.system.md
      reviewer.system.md
    config.toml
  automation/
    controller/
    adapters/
    state/
  schemas/
    task_packet.schema.json
    coder_result.schema.json
    review_result.schema.json
    task_state.schema.json
  runs/
  mock/
```

这个布局的意义不在于美观，而在于**规则、角色、接口、状态、观测、测试各自独立**。

---

### 10.2 配置默认值建议

| 项                | 默认值                                                                          |
| ---------------- | ---------------------------------------------------------------------------- |
| 任务真值             | 结构化模型                                                                        |
| controller 决策方式  | deterministic rules first                                                    |
| coder 输出         | `--output-schema` 约束后的 JSON                                                  |
| reviewer 输出      | `--output-schema` 约束后的 JSON                                                  |
| 观测方式             | JSONL 事件流 + 日志                                                               |
| 默认通知点            | `needs_human_ruling`、`review_clean_ready_for_human`、`task_done`、`phase_done` |
| review loop 默认上限 | 3                                                                            |
| 下一任务选择           | reviewer 建议 + controller 二次确认                                                |

### 10.3 CLI 默认调用原则

* 显式传 `-C`
* 显式传模型与关键 config
* 显式传 sandbox / approval
* 显式传 `--output-schema`
* 输出文件显式落盘

Codex CLI 本身支持这些覆盖方式，且命令行 `-c` 优先于配置文件默认值，因此自动化系统最稳的方式就是把关键参数显式化。([OpenAI开发者][5])

---

## 11. 风险、边界与后续演进

### 11.1 当前风险

**角色混权风险。**
一旦 controller 开始审代码，或 reviewer 开始排产，系统会迅速失去边界。

**schema 漂移风险。**
若 prompt、schema、controller 规则三边不同步，系统会出现“形式上成功、语义上失败”的伪稳定。

**无限回环风险。**
若没有重复 finding 检测与轮次上限，自动化只会扩大噪音。

**项目治理缺口风险。**
没有项目规则、没有 planning 文档、没有验证入口时，自动循环只会复制混乱。OpenAI Cookbook 也明确建议在复杂长任务中使用计划文档，并通过 `AGENTS.md` 指导何时使用计划。([OpenAI开发者][6])

---

### 11.2 当前边界

本文默认系统基于 **Codex CLI 外部编排**，而非直接构建在更深的 app-server 或 MCP 原语之上。
它也不要求一开始就使用 Codex subagents。虽然 Codex 已支持 subagents 和 custom agents，并可为不同 agent 配不同模型与指令，但这属于后续增强路径，不是首版系统成立的前提。([OpenAI开发者][4])

---

### 11.3 后续演进方向

未来可逐步演进到：

* 多任务并行调度
* reviewer 内部多子 agent 并行审查
* dashboard 与队列可视化
* GitHub Action / CI 更深整合
* MCP server 或更底层接口接入
* 更复杂的优先级与资源分配策略

但这些演进必须建立在首版状态机与四个核心模型稳定之后。否则系统会在“平台扩张”中失去核心合同。

---

## 12. 结语

本文真正想封住的，不是某个命令行参数，而是一种系统误区：

> **不要把自动编码系统理解成“更强的对话工具”；
> 应把它理解成“以状态机为中轴、以结构化对象为合同、以 agent runtime 为执行器的工程系统”。**

这一定义一旦成立，后续所有实现选择都会变得清晰：

* 为什么要有四个核心模型
* 为什么要有三角色分工
* 为什么要把 controller 做瘦
* 为什么 reviewer 只能建议不能排产
* 为什么 schema 高于散文
* 为什么默认最小权限
* 为什么这套系统适合连续任务而不适合一次性 patch

再收成一句话：

> **这套方案的本质，不是让 Codex 更忙，而是让项目中的机械回环被系统接管，让人类只保留真正值得保留的判断权。**

([OpenAI开发者][2])


[1]: https://developers.openai.com/codex/noninteractive/ "Non-interactive mode"
[2]: https://developers.openai.com/codex/cli/?utm_source=chatgpt.com "Codex CLI"
[3]: https://developers.openai.com/codex/guides/agents-md/ "Custom instructions with AGENTS.md"
[4]: https://developers.openai.com/codex/subagents/ "Subagents"
[5]: https://developers.openai.com/codex/cli/reference/ "Command line options"
[6]: https://developers.openai.com/cookbook/articles/codex_exec_plans/ "Using PLANS.md for multi-hour problem solving"
