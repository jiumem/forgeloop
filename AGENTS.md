# AGENTS.md

## Project Purpose

This repository builds a Codex auto-coding loop for continuous engineering tasks.

The system is centered on:

* 4 structured models as business truth:
  * `task_packet`
  * `coder_result`
  * `review_result`
  * `task_state`
* 2 interface layers:
  * external automation API
  * internal Codex CLI adapter

Natural language summaries are explanation only. They are not execution truth.

## Current Delivery Mode

This project is in early implementation.

The default delivery strategy is:

1. contract-first TDD
2. deterministic controller rules
3. mock-first validation
4. minimal real Codex smoke tests after core tests pass

Do not start from prompt tuning or CLI plumbing alone.

## Toolchain Baseline

Use Python with a `uv`-managed toolchain.

Default stack:

* `uv` for Python version, environment, dependency, and command entry management
* `pytest` for tests
* `ruff` for formatting and linting
* `pyright` for static type checking

Do not introduce parallel tools for the same responsibility unless the task explicitly requires it.

Default command style:

* `uv run pytest`
* `uv run ruff check .`
* `uv run ruff format --check .`
* `uv run pyright`

## Source Of Truth

Before changing code, align with these documents:

* [`docs/Codex 自动任务编码循环采用说明.md`](docs/Codex%20自动任务编码循环采用说明.md)
* [`docs/Codex 自动任务编码循环设计方案.md`](docs/Codex%20自动任务编码循环设计方案.md)
* [`docs/Codex 自动任务编码循环任务规划文档.md`](docs/Codex%20自动任务编码循环任务规划文档.md)

If implementation conflicts with docs:

* prefer the planning doc for scope and order of work
* prefer the design doc for system contracts and role boundaries
* do not silently invent a third interpretation

## Architecture Rules

Always preserve these boundaries:

* `Controller` advances state. It does not perform code review.
* `Coder` implements and reports what changed. It does not declare task passage.
* `Reviewer` finds substantive issues and promotion readiness. It does not own scheduling.

Keep these invariants:

* structured outputs rank above prose
* schema ranks above ad hoc fields
* controller decisions are rule-driven first
* review loop must have hard stop conditions

## Implementation Order

Unless a task explicitly says otherwise, implement in this order:

1. schemas for the 4 core models
2. state machine and controller transition rules
3. contracts for the 2 interface layers
4. mock scenarios and fixtures
5. tests for schema, state, and interfaces
6. implementation code
7. real Codex smoke tests

Avoid reversing this order.

## TDD Rules

For new behavior:

* add or update tests first when practical
* prefer contract tests over fragile log-based assertions
* test controller behavior with structured fixtures
* keep JSONL event parsing as observability support, not business truth

Minimum priority test areas:

* schema validation
* `advance_state()` transitions
* adapter input/output contracts
* loop stop conditions
* human approval path

## Scope Control

This repository is intentionally narrow for v1.

Default non-goals:

* multi-task parallel scheduling
* dashboard or visualization layer
* CI or GitHub Actions deep integration
* automatic task decomposition
* multi-agent reviewer orchestration
* distributed workers or queue services

Do not expand scope unless the task explicitly changes v1 boundaries.

## Repository Conventions

Expected top-level areas:

* `docs/` for rationale, design, planning
* `schemas/` for structured model schemas
* `automation/` for controller, adapters, and runtime logic
* `mock/` for fixtures and scripted scenarios
* `runs/` for local run artifacts when needed
* `.codex/prompts/` for role-specific prompts if introduced

When adding files, place them according to these responsibilities.

Expected Python project files for v1:

* `pyproject.toml`
* `uv.lock`
* `.python-version`
* `pyrightconfig.json` when custom type-check settings are needed

## Coding Rules

* Prefer small, explicit modules over clever abstractions.
* Keep controller logic deterministic and readable.
* Avoid coupling business rules to CLI output formatting.
* Do not make JSONL event structure a required business dependency.
* Do not mix schema definitions with prompt prose.
* Keep error objects structured and machine-readable.
* Write code and tests that run cleanly under `uv`.
* Treat type errors as design feedback, not as noise to suppress.

## Change Discipline

When implementing a task:

* do not broaden `must_do` without updating the source task definition
* call out `must_not_do` violations instead of silently expanding scope
* preserve unrelated user changes
* prefer additive, reviewable patches

## Validation

Before considering work complete:

* run the narrowest relevant test set first
* confirm schema and state-machine behavior when touching controller logic
* if real Codex integration is touched, run a minimal smoke test when feasible
* explicitly note skipped checks or blocked validations

Default local gates for meaningful changes:

* `uv run pytest`
* `uv run ruff check .`
* `uv run ruff format --check .`
* `uv run pyright`

## Decision Heuristic

When in doubt, optimize for:

1. stable contracts
2. testability
3. deterministic behavior
4. narrow scope
5. later extensibility

Do not optimize first for feature breadth.
