# 任务书模板

用途：每个阶段一份，是该阶段执行者的唯一输入（规划/11 §2.3 第 2 步）：

| 阶段 | 派给 | 允许改的路径 | 自己能跑的验证（规划/11 §4.1 验证入口） | 固定尾句 |
| --- | --- | --- | --- | --- |
| 测试 | Codex，经 `tools/agent/codex-run.sh impl` | 台账 `test_paths` + 任务 `paths` 内只抛 `NotImplemented` 的骨架 | 只做类型检查、lint；不执行测试 | 测试阶段尾句 |
| 实现 | Claude Opus 5.5 子代理 | 任务 `paths`；规则测试冻结 | 只经 `tools/ops/verify-container.sh` 跑 `verify:fast` | Opus 实现尾句 |
| 换家实现 | Codex，经 `tools/agent/codex-run.sh impl`（只限 RV0 / RV1，规划/11 §2.5） | 任务 `paths`；规则测试冻结 | 只做类型检查、lint；不执行测试、不调用 Docker | 换家实现尾句 |
| 评审 | 评审方（规划/11 §1.1），只读 | 无 | 不执行 | 按评审 schema 输出 |

由 `pnpm ops:brief <任务编号>` 按阶段生成到 `couli-runs/<任务编号>/`，不入库。规则见 `规划/11` §2.3、§5.3。

生成约束：

- 只用 `git show $SPEC_REF:<路径>` 读规划仓库，不读工作区。
- 上限 24KB；超限说明任务该拆。
- 「规则原文」一节原样摘录，不改写、不概括；表格行去掉「受影响的表 / 接口」一列。
- 规则原文命中禁用词（`tools/guard/banned-terms.txt`）即生成失败，先开同步任务。

以下为任务书正文格式，`<…>` 由脚本填。

---

# 任务 <编号>：<标题>

- 仓库：<rebate-platform / ios / android / harmony>；分支：`task/<编号>`；第 <n> 次尝试
- 规格版本：`SPEC_REF=<提交号>`
- 阶段：<测试 / 实现 / 评审>
- 风险级：<RV0 / RV1 / RV2>；实现：<claude / codex>；规则测试作者：<另一家，默认 codex>
- 依赖任务：<已完成的前置编号>

## 1. 目标

<一到三句话：做完后什么能用；关联的 AC 编号>

## 2. 规则原文（来自 08，版本同 SPEC_REF）

<对每个 refs 编号依次输出：>

### <BR 编号>（状态：<已确认 / 默认假设 / 待验证 / 待决策>）

<表格行正文>

<该编号的「细则」小节全文>

### 一跳引用

<上面条目引用到的其他 BR 的表格行正文>

列名、错误码、枚举值以 `contracts/` 与 `db/schema.sql` 为准；技术实现以 ADR-0001 为准。规则原文与它们冲突时不要自行取舍，在输出的 `blocked_reason` 里写明。

契约任务（`type: contract`）的第 2 节改为「契约依据（04 相关节原文；BR 只列编号与标题，版本同 SPEC_REF）」：先列 `refs` 的编号与标题，再逐字内嵌台账 `contract_sections` 点名的 04 各节，不带 BR 原文与一跳引用（规划/11 §5.3）。

试行的页面任务（规划/11 §2.6）：工具适配前，由编排会话在生成后的任务书第 2 节、「### 一跳引用」之前补「### 依据摘录」，内容是页面规格全文、规格取自的规划提交号、复制到本任务运行目录的设计稿路径；同类型已有合并的页面时给它的路径。规则原文照常内嵌。第 2 次尝试起任务书会重新生成，这一段要重新补上，评审前确认它还在。

### 必须复用（来自台账 `reuse`；自写等价物视为缺陷，规划/11 §3.1）

<每项一行：库 / 组件 / 端口 / 原语名与用途。实现里不得自写同类功能；确需自写的，在 JSON 输出的 decisions 里写明理由，评审按 S1 核>

## 3. 可以改的路径

<测试阶段：台账 test_paths 列表，加任务 paths 内的骨架文件；实现阶段：任务 paths 列表；评审阶段：无，只读>

## 4. 不能改的

- 保护路径：<由脚本列出与本任务相关的保护路径>
- 已有规则测试（实现阶段起，`spec_commit=<提交号>` 之后不得改动）：<测试文件列表>
- 测试阶段：不写实现，骨架只抛 `NotImplemented`。
- `ops/`、`docs/` 下任何文件；结果只写进 JSON 输出。

## 5. 必须遵守的仓库规则

<paths 命中的各级 AGENTS.md 全文，按从根到子目录的顺序内嵌>

## 6. 验收命令

```
<pnpm verify:fast 或更小范围的命令>
```

实现阶段（Opus）：必须变绿的规则测试：<测试 ID 列表>。跑测试只用可信副本的 `tools/ops/verify-container.sh <任务编号>`（只跑 `verify:fast` 这一层，参数以代码仓库为准），不在宿主上直接跑测试；完整验证由编排者在隔离容器里跑。

换家实现（Codex）：必须变绿的规则测试同上，但沙箱里只做类型检查与 lint，不执行测试；测试由编排者在隔离容器或 CI 里跑，失败输出附进下一轮的第 7 节。

测试阶段：本节改为「必须先红的测试」：<测试 ID 列表>。沙箱里只做类型检查与 lint，不执行测试；写好的测试全部列进 `outside_needed`，由编排者在隔离容器或 CI 里确认先红（有效的红按测试类型判，规划/11 §2.3 第 3 步）。

各阶段都不要跑集成测试、迁移和类型生成，需要时写进 `outside_needed`。

## 7. 上一轮失败输出（第 2 次起才有）

```
<上一轮沙箱外验证或评审发现的末 200 行>
```

## 8. 输出

按给定的 JSON 结构返回，字段全部必填：

| 字段 | 含义 |
| --- | --- |
| `task_done` | 是否认为完成 |
| `files_changed` | 改动文件列表 |
| `commands` | 跑过的命令与退出码 |
| `tests_passed` | 验收命令是否通过 |
| `deps_needed` | 需要新装的依赖：名称、版本、理由；没有填空数组 |
| `outside_needed` | 需要编排者在沙箱外跑的命令（迁移、类型生成等）：命令、理由；没有填空数组 |
| `blocked_reason` | 没做完或发现规格冲突时写原因；没有填空串 |
| `notes` | 需要评审方注意的地方，三句以内 |

固定尾句按阶段三选一（评审阶段另按评审 schema）：

- 测试阶段（Codex）：Do not commit. Do not install dependencies. Do not modify any file under `ops/` or `docs/`. Do not write implementation code. Do not run tests. 只做类型检查与 lint；不要运行需要网络、Docker、数据库或监听端口的命令。
- 换家实现（Codex）：Do not commit. Do not install dependencies. Do not modify any file under `ops/` or `docs/`. Do not modify existing rule tests. Do not run tests. 只做类型检查与 lint；不要运行需要网络、Docker、数据库或监听端口的命令。
- Opus 实现（Claude Opus 子代理）：Do not commit. Do not install dependencies. Do not modify any file under `ops/` or `docs/`. Do not modify existing rule tests. 跑测试只用 `tools/ops/verify-container.sh`，这是唯一允许调用 Docker 的命令；不要在宿主上直接跑测试、连数据库、跑迁移或类型生成，也不要自己起网络服务。
