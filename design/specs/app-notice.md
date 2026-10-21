# 公告 Notice（App 内 H5）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Notice`（h5 `/notice`，auth none，入口 in_app / push / deeplink，可选参数 `article_id`）；从哪来：首页公告条、推送；去哪：公告详情、返回来源页
- 需求：01 §4.2 `Notice` 行；F-H5-01；规则只引编号：BR-TEXT-11（日期写法）、BR-TEXT-13 细则「首页公告条的关闭与内容版本」、04 §3.2 `articles`；验收：AC-H5-01（同号规则）、AC-S1-157、AC-S1-185；任务：F1-03
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/notices/**`
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表 | Notice-v2.dc.html（0f412404d73e） | 打开公告 | listArticles（category=notice）· 200；按发布时间倒序（published_at DESC, id DESC） |
| 详情 | NoticeDetail-v2.dc.html（b71bf593f92d） | 点一条或带 `article_id` 打开 | getArticle · 200；配图可选，样例公告没有配图 |
| 深色 | NoticeDark.dc.html（7af3d53ff1e2） | 系统深色 | 同列表 |
| 不存在 / 已下线 | 不适用（无画板，用通用失败态） | getArticle 30701 | 30701 |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | 请求失败 / 无网络 | 50001；本地 |

画板上的公告标题、日期与正文均为样例。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 列表行 | 标题 + 摘要 + 日期（同年写月-日，BR-TEXT-11） | title、published_at、正文首段 | 进详情；没有「置顶」标签 |
| 列表底 | 「没有更多公告了」 | next_cursor 为空 | — |
| 详情 | 标题 + 日期 + 富文本正文（`article-body` 组件，节点白名单） | body | 正文链接按 H5 规则经桥打开 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 加载失败 | BR-TEXT-14 表 C `h5.load_failed` |
| 正文 | 运营内容（后台 CMS），不进字典 |
| 「没有更多公告了」 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| listArticles | 进入、翻页、重试 | — |
| getArticle | 进详情 | 30701 |

## 5. 权限点与开关

无；匿名可读（基本模式能否进入按 BR-ID-11 细则）。

## 6. 稿上没画、实现要做的

详情长文滚动与返回位置保持；读屏按标题、日期、正文顺序；大字号正文。

## 7. 待定与不一致

- 04 `articles` 没有置顶与摘要字段：本页按发布时间倒序、摘要取正文首段，待上游（04 / 契约线确认）。
