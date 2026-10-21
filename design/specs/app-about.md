# 关于 About（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`About`（auth none，游客与基本模式可达，入口 in_app / push）；从哪来：设置「关于凑狸」；去哪：`Agreement`、返回
- 需求：01 §4.2 `About` 行；F-OBS-06；规则只引编号：BR-TEXT-16（AI 公示）、BR-ID-15、00 D16、`design/app-icon/README.md`；验收：AC-S1-136、AC-S1-158、AC-S1-185；任务：APP-12、HM-08
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 登记后（显示生成式 AI 服务公示） | About-v2.dc.html（93b849722a71） | `agent.filing_text` 非空 | getConfig · agent.filing_text（原样显示一个文本块，客户端不拼接） |
| 登记前 + 复制诊断信息 | AboutBeforeFiling.dc.html（976dc087f1ba） | `agent.filing_text` 为空：整节不显示；点【复制诊断信息】 | 本地：版本、构建号、渠道等（F-OBS-06）；复制后轻提示 |
| 深色 | AboutDark.dc.html（f24efdd79bfb） | 系统深色 | 同登记后；App 图标按图片处理 |

画板上的版本号与公示文本块为占位（方括号表示原样显示配置值，不显示虚构编号）。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 头部 | 正式 App 图标（`design/app-icon/icon-1024.png` 缩样）+ 应用名 + 版本 | 本地版本与构建号 | — |
| 信息列表 | App 备案号、生成式 AI 服务公示、协议入口 | filing_text；备案号见 §7 | 协议进 `Agreement` |
| 诊断 | 次按钮【复制诊断信息】 | 本地 | 复制内容不含账号、手机号、密钥或完整设备标识（F-OBS-06） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 复制诊断信息 | BR-TEXT-14 表 C `about.copy_diagnostics` / `.done` |
| AI 公示 | 配置 `agent.filing_text`（BR-TEXT-16） |
| 「App 备案号」「生成式 AI 服务公示」标题、诊断说明句 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getConfig | 启动时已取（本页读 LKG） | — |

## 5. 权限点与开关

`agent.filing_text` 为空时整节不显示（BR-TEXT-16）。

## 6. 稿上没画、实现要做的

复制成功的读屏播报；大字号下文本块换行；诊断信息字段清单按 F-OBS-06 校对。

## 7. 待定与不一致

- App 备案号待负责人提供（06 Q-C4），没有之前该行的显示方式未定，待上游。
