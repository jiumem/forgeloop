# Forgeloop

Forgeloop 是面向 Codex 的 Tracker 驱动工程 Skill 套件，覆盖仓库配置、设计探索、Spec/Ticket 发布、串行实现、独立双轴审查、修复、集成、恢复和最终验收。

完整中文说明见 [README.zh-CN.md](README.zh-CN.md)。

## 快速开始

```text
使用 $setup-forgeloop 为当前仓库配置 Tracker、集成策略和领域文档。
使用 $to-spec 将已充分讨论的上下文发布为正式 Spec。
使用 $to-tickets 将该 Spec 拆成带 Blocking 的垂直 Tickets。
使用 $run-initiative 从正式 Spec 运行完整交付闭环。
```

版本 `3.0.0` 是破坏性升级。升级前请阅读 [2.5.0 → 3.0.0 迁移指南](docs/migrations/2.5.0-to-3.0.0.md)。

## 验证

```bash
python3 plugins/forgeloop/scripts/validate_suite.py --mode release
python3 plugins/forgeloop/scripts/validate_runtime_contract.py
python3 /Users/nuc8/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/forgeloop
```

## 许可证

[MIT](LICENSE)
