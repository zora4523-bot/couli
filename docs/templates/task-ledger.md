# 任务台账格式

用途：`rebate-platform/ops/tasks/<编号>.yaml`，一任务一文件，覆盖四个代码仓库；每个文件不超过 40 行。规则见 `规划/11` §2.1。

- 编号沿用 `规划/05` §3 的原编号和原含义；拆分加小写字母后缀。入账脚本校验编号前缀在 `SPEC_REF` 版本的 05 里存在。
- 入库的 `status` 只有 `todo` 和 `done`；`done` 在本任务自己的 PR 里改。
- 在途状态不进仓库，存 `couli-runs/state/<编号>.json`（见下文）。
- `done` 满 30 天移到 `ops/tasks/archive/<年月>/`。

## 1. 入库字段

| 字段 | 必填 | 取值 | 说明 |
| --- | --- | --- | --- |
| `id` | 是 | 05 的任务编号，可带后缀 | 文件名与它一致 |
| `repo` | 是 | `rebate-platform` / `ios` / `android` / `harmony` | 任务落在哪个仓库 |
| `title` | 是 | 一行 | 与 05 对应行含义一致 |
| `type` | 是 | `impl` / `contract` / `migration` / `deps` / `test-change` / `guard-change` / `sync` | `contract`、`migration`、`deps` 各自全局串行；`migration` 分两段做：实现者只写 SQL，编排者在沙箱外执行并生成类型（规划/11 §2.3） |
| `refs` | 是 | BR / AC 编号列表 | 任务书按它抽规则原文 |
| `refs_hash` | 是 | 编号 → 条目正文哈希 | 由入账脚本从规格索引填；正文变了任务标 `stale` |
| `contract_sections` | 否 | 04 的节号列表，如 `['2', '7']`、`['6.1', '8.4']` | 只用于 `type: contract`：任务书逐字带这些节，BR 只列编号与标题（规划/11 §5.3） |
| `deps` | 是 | 任务编号列表，可空 | 全部 `done` 才就绪 |
| `paths` | 是 | glob 列表 | 实现阶段允许改动的路径；与在途任务相交则不派发 |
| `test_paths` | 有测试作者时必填 | glob 列表，只能在保护路径第一类之内（`test/{spec,acceptance,properties,replay}/**` 等） | 测试阶段允许写的测试资产路径（规划/11 §2.3 第 2、3 步）；`tester: none` 时不填 |
| `impl` | 是 | `claude` / `codex` | 主实现。默认 `claude`（Claude Opus 5.5 子代理，规划/11 §1.1）；`codex` 只用于 RV0 / RV1 超限换家（规划/11 §2.5） |
| `tester` | 是 | `codex` / `claude` / `none` | 规则 / 验收测试作者。有测试作者的默认 `codex`（实现前先写、先红）；不需要规则测试的任务（文档、台账等）保持 `none`；三端的快照与模拟器冒烟随同线写；资金与归属必须与 `impl` 不同。2026-10-05 前入账的任务按真实作者记（规划/11 §1.1 过渡规则） |
| `accept` | 是 | 命令或测试 ID 列表 | 完成判定 |
| `status` | 是 | `todo` / `done` | |
| `pr` | 否 | PR 号 | 合并时填 |

风险级不写在台账里：由 `tools/guard/risk-of-paths.ts` 按 `paths` 和 `ops/risk-map.yaml` 算出。

## 2. 示例

```yaml
id: B2-02a
repo: rebate-platform
title: ledger：凭证与分录写入、余额缓存、账户行锁
type: impl
refs: [BR-FUND-13, BR-FUND-16, BR-FUND-19]
refs_hash:
  BR-FUND-13: <12 位哈希>
  BR-FUND-16: <12 位哈希>
  BR-FUND-19: <12 位哈希>
deps: [B2-01]
paths:
  - "apps/api/src/modules/ledger/**"
test_paths:
  - "test/spec/ledger/**"
impl: claude
tester: codex
accept:
  - "pnpm verify"
  - "test/spec/ledger/**"
status: todo
pr: null
```

同一任务的一行摘要（`pnpm ops:status` 的输出格式）：

| 编号 | 仓库 | 标题 | 风险级 | 实现 / 测试 | 依赖 | 在途状态 | 尝试 | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2-02a | rebate-platform | ledger：凭证与分录写入、余额缓存、账户行锁 | RV2 | claude / codex | B2-01（done） | review | 1 | #37 |

## 3. 在途状态（不入库）

`couli-runs/state/<编号>.json`，先写临时文件再改名；每天同步到 `rebate-private/ops-state/`。

| 字段 | 说明 |
| --- | --- |
| `state` | `ready` / `spec` / `doing` / `verify` / `review` / `longrun` / `pr` / `blocked` / `ask` / `stale` |
| `attempts` | 按阶段分开的已用次数：`test`（Codex 写测试）、`impl`（Opus 实现）、`impl_fallback`（换家实现）、`spec_review`、`code_review`；派发前加一（规划/11 §2.5） |
| `opus_failures` | Opus 无产出、超时、容量错误的次数（连续与累计各记一个数）；连续 3 次或累计 5 次即按规划/11 §2.5 换家，RV2 则 `blocked` |
| `runs` | 每次运行的阶段、代理（`codex` / `claude`）、模型、起止时间、结果文件路径；验证运行另记 `mode`（`container` / `ci` / `host`） |
| `spec_commit` | 规则测试提交号；此后规则测试不得改动 |
| `pid`、`started_at` | 当前后台运行 |
| `owner_session`、`lease_until` | 哪个会话持有、租约到期时间（20 分钟，续期） |
| `ask_created_at` | 进入 `ask` 的时间，用于 24 / 72 小时跟进 |
| `last_error` | 上一轮失败输出文件的路径 |
