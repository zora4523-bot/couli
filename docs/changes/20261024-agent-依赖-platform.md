# 2026-10-24 Agent 模块依赖 platform 与 union（BR-AI-02 ③ 白名单）

- **状态：已写回**。00 §8 第 ② 类（放宽一条已确认规则的依赖白名单）。负责人 2026-10-24 在编排会话中授权：「调用 jev 来选，不用询问我这种问题」——本项由 Jev 判断后按其结论取 A（编排裁定 D10-287，D10-275 ② 定案）。
- **来源**：依赖门禁 CT-06zq（rebate-platform #1404）在主干跑白名单检查时发现，agent 模块实际依赖 platform（39 处，含数据库等可写句柄）与 union（仅类型），而 BR-AI-02 ③ 的白名单没有这两项；编排 D10-273 ② / D10-275 最初按第 ① 类同步处理，回写 1023e 的独立评审指出这是放宽已确认规则、属第 ② 类，D10-275 ② 随之更正并交负责人。
- **范围**：只改 08 BR-AI-02（正文一句、细则 ③ 一项）与本记录；不改工具集合、只读入口与 ledger / payout / settlement / growth / commission 的限制；不改代码。

## 1. 三个选项与 Jev 的判断

| 选项 | 内容 | 是否最合适（Jev） |
| --- | --- | --- |
| A | 同意 Agent 依赖 platform（配置、日志、时钟、数据库连接；数据库只读写 Agent 自己的表）与 union（仅类型），回写 BR-AI-02 与代码一致；另加一道门禁拦 Agent 写别模块的表 | 0.87 |
| B | 不同意：Agent 拆掉对 platform 的依赖，改经其他模块的端口取配置、日志与数据库，BR-AI-02 不改 | 0.07 |
| C | 先只在细则里记为现状、正文不动，等以后再定 | 0.07 |

另问「A 加上『拦 Agent 写别模块的表』这道门禁后，是否守住了 BR-AI-02 想防的风险（Agent 绕过其他模块的业务规则直接改数据）」：0.75。判断脚本在 couli-runs/B3-lane/jev-d10-275.py（运行目录，不入库）。

## 2. 写回内容

- BR-AI-02 ③ 白名单另含：
  - `platform` 的基础设施部分：配置、日志、时钟、数据库连接。经数据库连接**只读写 Agent 自己的表**（04 §3 agent 段）；读别模块的数据照旧只走各模块的只读入口。
  - `union` 的类型导入（只 import type）。
- 写表限制由一道新门禁执行（D10-287 ②，归 agent 线）：对 agent 模块做 AST 静态扫描，Kysely 的 insertInto / updateTable / deleteFrom 与原生 SQL 写语句只许出现 Agent 自有表；主干先确认零违规。门禁合并前，这条限制只靠评审守住。
- 不变：工具集合、只读入口（ledger/read.ts、payout/read.ts）与导出登记、对 growth / commission / settlement 与各模块写服务的禁止。

## 3. 后续

- agent 线：写表门禁任务（编号由 agent 线取，合并后在 BR-AI-02 细则 ③ 补上编号）。
- rebate-platform：`ops/approvals.yaml` 登记本决定（负责人授权由 Jev 判断）。
- 规划/02 §4.1 agent 依赖列表随下一批同步（不在本次）。
