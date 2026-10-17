# 变更记录：实现回到 Claude，Codex 只做对抗评审（2026-10-17）

- 状态：已确认（负责人 2026-10-17 17:2x 在对话中明确）。
- 负责人原话：「codex 做完手动的开发任务，接下来的主要开发还是安排其他账号的 Claude 5.5 opus 模型；困难的工作你也可以安排更高级的推理或者模型来执行开发；codex 负责对抗 review」。
- 类别：00 §8 第 ② 类（改变协作分工；不改业务规则、契约形状与技术栈锁定项），负责人决定。
- 依据：规划/11 §1.1、§7.3 第 16 项；05 §2；代码仓库 `ops/approvals.yaml` 第 34 条（停用第 30 条，第 31 / 33 条只对在途任务有效，第 19 / 27 条不变）。
- 被取代的决定：`docs/changes/20261016-未开工任务改由Codex实现.md`（§1 未开工任务默认 Codex 实现，§1.1 放开 H5 与管理后台前端）。该记录保留，只作已开工 Codex 任务的依据。

## 1. 内容（执行口径，编排会话按原话拟写）

1. **新认领的任务一律由 Claude 实现**：默认 Claude Opus 5.5 子代理（`claude-opus-5-5`）。困难任务（归因流水线 B1-08h / i、账本记账 B2-02f、Agent 编排核心、三端资金页、跨模块事务等）由编排会话指定用 Opus 5.5 高推理（effort high / xhigh）或 Fable 5.1（`claude-fable-5-1`）；台账 `impl` 仍写 `claude`，模型写在注释。
2. **已派出 / 已开工的 Codex 实现任务做完为止**（含 Codex 轮次中的），不中途换人；「已开工」的界定同 2026-10-16 记录：有 `spec_commit`、`test(spec)` 提交或实现提交，只认领、只写任务书不算。代码仓库 `tools/guard/codex-impl-tasks.json` 冻结、不再新增任务号；清单里 `impl: codex` 且尚未开工的任务，下次台账 PR 改回 `impl: claude`、`tester: codex` 并移出清单。
3. **Codex 继续负责**：写规则 / 验收测试（先写、先红，资金类必须）；过审 Claude 写的规则测试（在途 Codex 任务）；代码对抗评审（2026-10-09 口径不变：Claude 写的实现只由 Codex 新只读会话评审，一家即可；Codex 写的在途实现由 Claude 新子代理评审）。
4. **H5 与管理后台前端同样回到 Claude 实现**；已开工的 Codex 前端任务做完，前端线浏览器截图对照定稿设计稿、差异记 `design-diffs.md` 的流程不变，设计稿未定稿的页面仍不派实现。
5. **三端原生 App 的新任务同样回到 Claude 实现**；2026-10-16 至 10-17 间开工的 Codex 原生任务做完为止，构建与模拟器验证仍由编排者在沙箱外跑。

安全边界不变：资金、订单归属、打款、订单补拉、数据库恢复与主库切换、发布流水线接入、迁移、契约本就由 Claude 实现，`codex-impl-tasks.json` 的 `forbidden_paths` 照旧；`apps/h5/**`、`apps/admin/**` 不回填 `forbidden_paths`（回填会拒收在途前端台账，清单冻结即足够）。改派不改风险级与合并门槛。

## 2. 涉及

| 位置 | 改动 |
| --- | --- |
| 规划/11 §1.1 | 新增「2026-10-17 起：实现回到 Claude，Codex 只做对抗评审」一条；「2026-10-16 起」一条标停用；主实现一条补「困难任务可指定 Opus 高推理或 Fable 5.1」；原生三端一条改写 |
| 规划/11 §7.3 | 第 15 项状态改「2026-10-17 由第 16 项停用」；新增第 16 项 |
| 规划/05 §2 | 默认分工说明补 2026-10-17 口径 |
| `docs/templates/task-ledger.md` | `impl` 字段说明补模型写注释、Codex 任务不再新增 |
| 代码仓库 `ops/approvals.yaml` | 新增第 34 条（row 16）；第 30 条加 `superseded_by: 34`（rebate-platform PR #644） |
| 代码仓库 `tools/guard/codex-impl-tasks.json`、`tools/lib/codex-impl-tasks.test.ts` | 说明补「清单冻结」；测试持 2026-10-17 冻结集，只许删不许增 |
| 代码仓库 `tools/guard/lib/approvals.test.ts`、`tools/ops/task.ts`、`tools/README.md`、`tools/agent/README.md` | §7.3 行号上限 16；注释与说明 |
| couli-runs 各线 | `B3-lane/notices.md` 2026-10-17 17:3x 条已通知各执行代理 |

## 3. 对在途任务的处理

- 在 `codex-impl-tasks.json` 里且已开工的 Codex 任务（含 Codex 轮次中的）：照 2026-10-16 流程做完、合并；契约机械提交（approvals 第 31 条）照旧可用。
- 在清单里但尚未开工的：下次台账 PR 改回 `impl: claude`、`tester: codex`，同一 PR 从清单移除；Claude 已写好但还没进 `spec_commit` 的规则测试不直接沿用给 Claude 实现：改回后由 Codex 按 §2.3 第 3 步重写并重新先红、过审（资金与归属必须重写——硬规则 3；其余可由 Codex 在原测试基础上接手，仍以 Codex 为测试作者记录）。
- 已认领、未入清单的：直接按 Claude 实现入账。
- 评审：Codex 对抗评审的轮次与档位不变（§2.4、§2.5）。

## 4. 验收与恢复

- 验收：2026-10-17 之后新入账的任务台账 `impl: claude`（代码仓库 `task.ts check` 对清单外台账拒收 `impl: codex`）；`codex-impl-tasks.json` 的 `tasks` 不再出现新编号（`tools/lib/codex-impl-tasks.test.ts` 冻结集用例）；困难任务的台账注释写明模型；证据文件的代码评审为 Codex 新只读会话。
- 恢复：负责人要再放开时，在 §7.3 新增一项并在代码仓库 approvals 新增条目（不复用第 30 条），清单解冻、删除冻结集用例；已回到 Claude 并合并的任务不回退。
