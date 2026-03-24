# runs/ — 本地运行产物目录

## 职责

存放每次 loop 运行产生的本地工件，包括：

- `task_state.json` — 运行态快照
- `coder_result_*.json` — 各轮 coder 产出
- `review_result_*.json` — 各轮 reviewer 产出
- `events.jsonl` — 可选的事件流日志

## 约定

- 每次运行建议以 `{task_id}/{timestamp}/` 为子目录隔离
- 此目录已被 `.gitignore` 排除，不入版本控制
- 工件格式遵循 `schemas/` 中定义的 JSON Schema

## 当前状态

空目录。P5（loop 集成）时开始产出真实运行工件。
