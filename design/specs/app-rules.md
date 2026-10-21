# 返利规则 Rules（App 内 H5）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Rules`（h5 `/rules`，auth none，入口 in_app / push / deeplink）；从哪来：帮助中心常见问题第一行；去哪：返回
- 需求：01 §4.2 `Rules` 行；F-H5-01；规则只引编号：BR-TEXT-13（「比价」只出现在比价说明那一篇）、BR-TEXT-01（「已扣回」）、BR-ID-22（拼多多备案）、BR-TEXT-11；验收：AC-H5-01（同号规则）、AC-S1-157、AC-S1-185；任务：F1-03（11 §2.6 试行首选页）
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/rules/**`
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 文章（示例） | Rules-v2.dc.html（d2e113e9883b） | 打开返利规则 | listArticles（category=rule）/ getArticle · 200；正文待负责人提供 |
| 深色 | RulesDark.dc.html（3e73723b35e4） | 系统深色 | 同上 |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | 请求失败 / 无网络 | 50001；本地 |

画板正文为示例版式，不是定稿规则。

## 2. 组件

标题 + 更新日期（BR-TEXT-11 月-日）+ 分节正文（`article-body`）。

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 正文 | 运营 / 负责人内容（过 BR-TEXT-13 与 BR-INV-20 词库扫描），不进字典 |
| 加载失败 | BR-TEXT-14 表 C `h5.load_failed` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| listArticles / getArticle | 进页 | 30701 |

## 7. 待定与不一致

- 返利规则正文待负责人提供（06 Q-F4），待上游；画板正文只作版式参考，不按画板字句上线。
