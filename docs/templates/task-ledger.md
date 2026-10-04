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
| `lane` | 否 | `direct` / `template` / `full` | 只用于页面任务，缺省 `full`（规划/11 §2.6）；不影响风险级 |
| `exemplar` | 否 | 代码仓库内的路径 | 只用于页面任务：照哪张示范页做（登记在 `docs/exemplars.md`）；示范页任务自己不填 |
| `ui_refs` | 否 | 路径列表 | 只用于页面任务：该页的页面规格与设计稿（位置见规划仓库 `design/README.md` 第 15、16 项）；入库的按 `SPEC_REF` 读 |
| `deps` | 是 | 任务编号列表，可空 | 全部 `done` 才就绪 |
| `paths` | 是 | glob 列表 | 允许改动的路径；与在途任务相交则不派发 |
| `impl` | 是 | `codex` / `claude` | 主实现 |
| `tester` | 是 | `codex` / `claude` / `none` | 规则测试作者；资金与归属必须与 `impl` 不同 |
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
impl: codex
tester: claude
accept:
  - "pnpm verify"
  - "test/spec/ledger/**"
status: todo
pr: null
```

同一任务的一行摘要（`pnpm ops:status` 的输出格式）：

| 编号 | 仓库 | 标题 | 风险级 | 实现 / 测试 | 依赖 | 在途状态 | 尝试 | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2-02a | rebate-platform | ledger：凭证与分录写入、余额缓存、账户行锁 | RV2 | codex / claude | B2-01（done） | review | 1 | #37 |

## 3. 在途状态（不入库）

`couli-runs/state/<编号>.json`，先写临时文件再改名；每天同步到 `rebate-private/ops-state/`。

| 字段 | 说明 |
| --- | --- |
| `state` | `ready` / `spec` / `doing` / `verify` / `review` / `longrun` / `pr` / `blocked` / `ask` / `stale` |
| `attempts` | 实现与评审各自的已用次数；派发前加一 |
| `spec_commit` | 规则测试提交号；此后规则测试不得改动 |
| `pid`、`started_at` | 当前后台运行 |
| `owner_session`、`lease_until` | 哪个会话持有、租约到期时间（20 分钟，续期） |
| `ask_created_at` | 进入 `ask` 的时间，用于 24 / 72 小时跟进 |
| `last_error` | 上一轮失败输出文件的路径 |
