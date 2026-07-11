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
