# INIT-001 · Bootstrap Codex Initiative Runtime MVP

## 1. 前置输入与决策基线
### 1.1 Requirement Summary
- 问题摘要：需要一个面向 Codex 原生能力的 Initiative-first 自动编码—审查执行体系。
- 目标摘要：给出可运行 MVP，验证总任务文档、Initiative 调度、Task 控制、Gate/Review 包装与 skills/agents 目录。

### 1.2 Design Refs
- `docs/design/INIT-001-design.md`

### 1.3 Gap Analysis Refs
- N/A

### 1.4 Sealed Decisions
- Initiative 是唯一用户主入口。
- Milestone 是阶段收敛边界。
- Task 是内部最小执行原子。
- Skill 是核心编排面。
- Repo 内 Python 是确定性执行核。

### 1.5 Execution Boundary
- 本文档覆盖运行时 MVP。
- 不覆盖真实 GitHub 生命周期自动化。
- 不覆盖外部发布系统。

### 1.6 Initiative Reference Assignment
- 法定参考入口：`docs/initiatives/INIT-001.md`

## 2. Initiative
### 2.1 Background
- 需要把上位执行法、规划法与 Codex 原生能力压到一个可运行仓库中。

### 2.2 Scope
- 规划 preflight
- Initiative 状态重建
- Task 状态机
- Gate/Review 包装
- Skills / Agents / AGENTS / config 布局

### 2.3 Non-Goals
- 外部 MCP
- 生产级 GitHub 集成
- 真实部署系统

### 2.4 Success Criteria
- 可从单篇总任务文档运行 Initiative。
- 可生成 Gate 与 Review 工件。
- 可通过显式 skills 驱动流程。

## 3. Milestone Master Table
### 3.1 Milestone List
- M1：规划输入与状态重建成立
- M2：Task 控制与 Gate/Review 包装成立
- M3：Codex 原生控制面成立

### 3.2 Milestone Dependencies
- M2 依赖 M1
- M3 依赖 M2

### 3.3 Milestone Acceptance
- 见 machine-readable plan

### 3.4 Milestone Reference Assignment
- 全部里程碑的法定参考入口：`docs/initiatives/INIT-001.md`

## 4. Workstream & Agent Allocation
- WS-CORE：Agent-A
- WS-REVIEW：Agent-B
- WS-CODEX：Agent-C

## 5. Task Ledger
- T001 ~ T005 见 machine-readable plan

## 6. Branch & PR Integration Path
- 默认一个 Milestone 一个 PR
- PR-01 / PR-02 / PR-03 对应 M1 / M2 / M3

## 7. Acceptance Matrix
- Task：G1 / R1
- Milestone：G2 / R2
- Initiative：G3 / R3

## 8. Global Residual Risks & Follow-Ups
- 见 machine-readable plan

```initiative-plan
{
  "initiative": {
    "key": "INIT-001",
    "title": "Bootstrap Codex Initiative Runtime MVP",
    "requirement_summary": {
      "problem": "A Codex-native initiative runtime is needed to drive large tasks from a single initiative entry while keeping Task-level evidence and formal gates.",
      "goal": "Create a small but complete repo that demonstrates initiative-first orchestration, task-atomic control, and Codex-native skills/agents layout."
    },
    "design_refs": [
      "docs/design/INIT-001-design.md"
    ],
    "gap_refs": [],
    "sealed_decisions": [
      "Use initiative as the only primary user entry.",
      "Keep task as the internal atomic execution unit.",
      "Use skills as the orchestration surface and repo-local Python as the deterministic kernel."
    ],
    "execution_boundary": "This initiative covers the runtime MVP itself; it does not automate real deployment or external release systems.",
    "initiative_reference_assignment": "docs/initiatives/INIT-001.md",
    "background": "The project must align Codex-native skills, agents, and runtime scripts with an initiative-first execution model.",
    "scope": [
      "Planning preflight",
      "Initiative state rebuild",
      "Task controller",
      "Formal gate/review wrappers",
      "Codex skills and custom agents layout"
    ],
    "non_goals": [
      "External MCP server integration",
      "Production-grade GitHub automation",
      "Full autonomous code generation without Codex"
    ],
    "success_criteria": [
      "The repo can parse a total-task document.",
      "The repo can rebuild initiative/task state from plan plus Git anchors.",
      "The repo exposes explicit skills for initiative/task/gate/review workflows."
    ]
  },
  "milestones": [
    {
      "key": "M1",
      "goal": "Planning input and initiative state rebuild are available.",
      "depends_on": [],
      "planned_pr_model": "Single PR",
      "acceptance": [
        "initiative-plan block parses",
        "planning preflight blocks malformed inputs",
        "state rebuild derives ready tasks"
      ],
      "reference_assignment": "docs/initiatives/INIT-001.md"
    },
    {
      "key": "M2",
      "goal": "Task-atomic controller and formal gate/review wrappers are available.",
      "depends_on": [
        "M1"
      ],
      "planned_pr_model": "Single PR",
      "acceptance": [
        "task-loop can advance toward READY_FOR_ANCHOR",
        "G1/G2/G3 commands can run",
        "R1/R2/R3 bundles and finalized reports exist"
      ],
      "reference_assignment": "docs/initiatives/INIT-001.md"
    },
    {
      "key": "M3",
      "goal": "Codex-native skills and agents are integrated as the repository control surface.",
      "depends_on": [
        "M2"
      ],
      "planned_pr_model": "Single PR",
      "acceptance": [
        "skills directories exist",
        "custom agents exist",
        "initiative-first entry path is documented"
      ],
      "reference_assignment": "docs/initiatives/INIT-001.md"
    }
  ],
  "workstreams": [
    {
      "key": "WS-CORE",
      "responsibility": "Planning parser, state rebuild, and initiative runtime orchestration.",
      "parallelizable": true,
      "depends_on": [],
      "recommended_executor": "Agent-A"
    },
    {
      "key": "WS-REVIEW",
      "responsibility": "Task controller, gate wrappers, and review report generation.",
      "parallelizable": true,
      "depends_on": [
        "WS-CORE"
      ],
      "recommended_executor": "Agent-B"
    },
    {
      "key": "WS-CODEX",
      "responsibility": "Codex skills, custom agents, and initiative-first operating surface.",
      "parallelizable": true,
      "depends_on": [
        "WS-REVIEW"
      ],
      "recommended_executor": "Agent-C"
    }
  ],
  "tasks": [
    {
      "key": "T001",
      "milestone": "M1",
      "workstream": "WS-CORE",
      "summary": "Implement initiative-plan parsing and planning preflight.",
      "design_refs": [
        "docs/design/INIT-001-design.md"
      ],
      "gap_refs": [],
      "spec_refs": [
        "README.md#机器可读总任务文档格式"
      ],
      "input": "Single initiative markdown document with embedded initiative-plan JSON.",
      "action": "Add parser and validator for the single initiative document.",
      "output": "Planning parser and preflight command.",
      "non_goals": [
        "No task controller yet",
        "No review generation yet"
      ],
      "dependencies": [],
      "acceptance": [
        "`cir planning-preflight` passes on INIT-001"
      ],
      "local_risks": [
        "Machine block format is JSON-first in this MVP."
      ],
      "recommended_executor": "Agent-A",
      "execution_mode": "write",
      "g1_commands": [
        "python -m unittest tests.test_planning -q"
      ]
    },
    {
      "key": "T002",
      "milestone": "M1",
      "workstream": "WS-CORE",
      "summary": "Implement initiative state rebuild and frontier selection.",
      "design_refs": [
        "docs/design/INIT-001-design.md"
      ],
      "gap_refs": [],
      "spec_refs": [
        "docs/initiatives/INIT-001.md#3-milestone-master-table"
      ],
      "input": "Valid initiative plan and Git anchor scan.",
      "action": "Create runtime state and frontier selection from plan plus tracked sources.",
      "output": "State rebuild, frontier, ready-task selection.",
      "non_goals": [
        "No formal gate execution yet"
      ],
      "dependencies": [
        "T001"
      ],
      "acceptance": [
        "`cir rebuild-state` returns ready tasks for the current frontier"
      ],
      "local_risks": [],
      "recommended_executor": "Agent-A",
      "execution_mode": "write",
      "g1_commands": [
        "python -m unittest tests.test_state -q"
      ]
    },
    {
      "key": "T003",
      "milestone": "M2",
      "workstream": "WS-REVIEW",
      "summary": "Implement Task controller transition rules.",
      "design_refs": [
        "docs/design/INIT-001-design.md"
      ],
      "gap_refs": [],
      "spec_refs": [
        "README.md#重要说明"
      ],
      "input": "Task packet and sensor observation.",
      "action": "Implement deterministic transition logic for local task convergence.",
      "output": "Transition decision with READY_FOR_ANCHOR / patch / proof / escalate actions.",
      "non_goals": [
        "No real Codex agent orchestration inside Python"
      ],
      "dependencies": [
        "T002"
      ],
      "acceptance": [
        "Task controller classifies clean observations as READY_FOR_ANCHOR"
      ],
      "local_risks": [],
      "recommended_executor": "Agent-B",
      "execution_mode": "write",
      "g1_commands": [
        "python -m unittest tests.test_controller -q"
      ]
    },
    {
      "key": "T004",
      "milestone": "M2",
      "workstream": "WS-REVIEW",
      "summary": "Implement G1/G2/G3 and R1/R2/R3 wrappers.",
      "design_refs": [
        "docs/design/INIT-001-design.md"
      ],
      "gap_refs": [],
      "spec_refs": [
        "docs/initiatives/INIT-001.md#7-acceptance-matrix"
      ],
      "input": "Task and milestone runtime state.",
      "action": "Add gate command runner and review bundle/finalization logic.",
      "output": "Formal gate JSON and review bundle/report files.",
      "non_goals": [
        "No external CI or GitHub API integration"
      ],
      "dependencies": [
        "T003"
      ],
      "acceptance": [
        "Gate and review artifacts are generated under .initiative-runtime"
      ],
      "local_risks": [
        "Formal review content still depends on Codex reviewer agents."
      ],
      "recommended_executor": "Agent-B",
      "execution_mode": "write",
      "g1_commands": [
        "python -m unittest tests.test_gate_review -q"
      ]
    },
    {
      "key": "T005",
      "milestone": "M3",
      "workstream": "WS-CODEX",
      "summary": "Integrate Codex skills, custom agents, and the initiative-first operating surface.",
      "design_refs": [
        "docs/design/INIT-001-design.md"
      ],
      "gap_refs": [],
      "spec_refs": [
        "AGENTS.md"
      ],
      "input": "Working runtime package and validated plan document.",
      "action": "Create skills and custom agents that expose the initiative-first workflow to Codex.",
      "output": "Skills directories, agent TOML files, and repository operating law.",
      "non_goals": [
        "No MCP server",
        "No production background automation"
      ],
      "dependencies": [
        "T004"
      ],
      "acceptance": [
        "The repo layout matches the intended Codex-native control surface"
      ],
      "local_risks": [],
      "recommended_executor": "Agent-C",
      "execution_mode": "write",
      "g1_commands": [
        "python -m unittest -q"
      ]
    }
  ],
  "pr_plan": [
    {
      "key": "PR-01",
      "milestone": "M1",
      "covers": [
        "T001",
        "T002"
      ],
      "goal": "Land planning input and initiative state rebuild.",
      "depends_on": [],
      "acceptance_checklist": [
        "Preflight passes",
        "Rebuild-state works",
        "Ready tasks are selected"
      ]
    },
    {
      "key": "PR-02",
      "milestone": "M2",
      "covers": [
        "T003",
        "T004"
      ],
      "goal": "Land task controller and formal quality wrappers.",
      "depends_on": [
        "PR-01"
      ],
      "acceptance_checklist": [
        "Task controller returns valid decisions",
        "Gate reports are generated",
        "Review bundles and reports are generated"
      ]
    },
    {
      "key": "PR-03",
      "milestone": "M3",
      "covers": [
        "T005"
      ],
      "goal": "Land Codex skills and custom agents surface.",
      "depends_on": [
        "PR-02"
      ],
      "acceptance_checklist": [
        "Skills are explicit-entry workflows",
        "Agents are repository-scoped",
        "Initiative-first entry is documented"
      ]
    }
  ],
  "global_residual_risks": [
    "Review content depends on Codex agents; deterministic scripts only validate structure and persist artifacts.",
    "GitHub and release integrations are intentionally stubbed in the MVP."
  ],
  "follow_ups": [
    "Add real GitHub PR lifecycle integration.",
    "Add more rigorous state reconstruction from CI and PR metadata.",
    "Add dedicated background automations for Shadow Check and Shadow Review."
  ],
  "g3_commands": [
    "python -m unittest -q"
  ]
}
```
