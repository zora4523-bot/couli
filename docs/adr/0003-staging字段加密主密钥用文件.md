# ADR-0003 staging 的字段加密主密钥用本地文件

- 状态：已采纳（负责人 2026-10-07 在对话中选「staging 先用文件密钥」）
- 日期：2026-10-07
- 取代：ADR-0001 §2「鉴权与密钥」行「云上用 KMS 实现」中 **staging** 的部分；prod 不变
- 被取代：无
- 相关：ADR-0001 §2；ADR-0002（staging 节点）；`规划/02` §12.3、§12.6；`规划/08` BR-ID-33；代码仓库 `apps/api/src/modules/platform/config/keyring.ts`、`keyring-startup.ts`（B1-01k）；部署底座 B1-01zc

## 1. 背景

字段加密（手机号、身份证、收款账号、联盟凭据，BR-ID-33）用信封加密：一把主密钥包着数据密钥环。ADR-0001 §2 定「本地用文件密钥，云上用 KMS」，代码据此规定 APP_ENV=staging / prod 只能用 `kms`、拒绝 `local`。KMS 接入还没实现，所以 staging 的五个进程现在都起不来，部署底座（B1-01zc）首次部署时发现。staging 节点在火山引擎（ADR-0002 §10 实测记录），接哪家 KMS 也未定。

## 2. 决定

- **staging**：允许 `FIELD_KEY_PROVIDER=local`。主密钥是节点上一个只有 root 可读的文件（`openssl rand -hex 32` 生成，600），以只读方式挂进需要它的容器；密钥环文件同样放节点上。主密钥只给 staging 用，不与任何其他环境共用，不进任何仓库，不发到对话里。
- **prod**：不变，只能 `kms`；`local` 在 prod 照样拒绝启动。
- **local / test**：不变。

## 3. 理由

staging 只有合成数据和少量测试账号（`规划/02` §3.2），主密钥泄露的影响限于这些测试数据；等 KMS 接入会让后端部署、三端联调整体推迟。prod 的保护不降低。

## 4. 影响

- 代码：`keyring.ts` / `keyring-startup.ts` 的 staging 规则与对应冻结规则测试要改（保护路径第一类，按 `ops/approvals.yaml` 第 24 条两家评审后加标签）；需要一个生成本地密钥环文件的命令。由代码仓库新任务承担。
- 运维：staging 节点上的主密钥文件丢了，已加密的测试数据无法解密（staging 可以重建测试数据，不另做备份；需要时负责人另存一份）。
- 以后 staging 改用 KMS：只换 `FIELD_KEY_PROVIDER` 与密钥环，本 ADR 标作废。
