# 协议 Agreement（App 内 H5）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Agreement`（h5 `/agreement`，auth none，入口 in_app / push / deeplink，参数 `type`、`version`）；从哪来：首启弹窗、登录页、设置（协议选择半屏）、隐私中心、强更页进入的隐私中心；去哪：返回来源页
- 需求：01 §4.2 `Agreement` 行；F-PRIV-01、F-PRIV-04、F-PRIV-05；规则只引编号：BR-ID-11、BR-ID-12、BR-ID-01 细则「受限会话」；验收：AC-PRIV-05（同号规则）、AC-S1-77、AC-S1-157、AC-S1-185；任务：F1-03
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/agreements/**`
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 隐私政策正文页 | Agreement-v2.dc.html（c0dfe5894c4f） | 打开任一协议类型（样例为隐私政策） | getAgreements / getAgreementVersion · 200（version、url、text_sha256）；正文待法务提供 |
| 深色 | AgreementDark.dc.html（ae7bf8c3496f） | 系统深色 | 同上 |
| 断网 | 不适用（无画板） | 无网络 | 显示安装包内的副本（画板设计说明，BR-ID-11） |
| 不存在的版本 | 不适用（无画板，用通用失败态） | 30701 | StateLoadFailed.dc.html（aea7c5d30a24） |

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题栏 | 协议名 + 返回 | type | — |
| 正文 | 富文本（`article-body`，节点白名单）+ 版本与生效日期 | 正文、version、published_at | 无需登录即可查看 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 加载失败 | BR-TEXT-14 表 C `h5.load_failed` |
| 正文 | 法务内容（后台协议发布），不进字典 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getAgreements | 进页（取当前版本） | — |
| getAgreementVersion | 带 `version` 打开 | 30701 |

## 5. 权限点与开关

无；强更受限会话可读（session scopes 含 deletion_only，按契约）。

## 6. 稿上没画、实现要做的

长文目录与锚点；读屏标题层级；大字号正文；包内副本与线上版本不一致时以线上为准并记录。

## 7. 待定与不一致

- 隐私政策、用户协议正文待法务提供（06 Q-F1 / Q-F14），待上游。
