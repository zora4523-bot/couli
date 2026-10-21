# 帮助中心 Help（App 内 H5）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Help`（h5 `/help`，auth none，游客与基本模式可达，可选参数 `article_id`）；从哪来：「我的」、设置、原生页的 `help_links` 入口（比价说明、找回指引、登录求助、提现规则）、邀请页；去哪：`Rules`、`RiskNotice` / `Appeal`（申诉文章按钮）、联系客服（[app-contact-cs.md](app-contact-cs.md)）
- 需求：01 §4.2 `Help` 行；F-H5-01；规则只引编号：BR-TEXT-18（客服话术与常见问题）、BR-TEXT-13、BR-TEXT-03「比价说明入口」、BR-PRICE-07、BR-ATTR-17 细则「找回页的填写指引」、BR-ID-36、BR-INV-18 细则、BR-INV-24、BR-WDR-04 细则、BR-TEXT-11；验收：AC-H5-01（同号规则）、AC-S1-74、AC-S1-72-PDD、AC-S1-157、AC-S1-185；任务：F1-03
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/help/**`
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 分类与常见问题 | Help-v2.dc.html（4a5546b509d6） | 进入 | listArticles（category=help）；常见问题第一行「返利规则」进 `Rules` |
| 分类文章列表 | HelpCategory.dc.html（d3026b2d8821） | 点分类 | listArticles（help_section=对应分类） |
| 找回指引：淘宝 / 京东 / 拼多多 | HelpArticle-v2.dc.html（3685fd8ae055）、HelpArticleJd-v2.dc.html（68ffc6ec62d9）、HelpArticlePdd-v2.dc.html（2ce123f4201a） | `help_links.claim_guide.<platform>` | getArticle；图为自绘示意图（不用平台截图） |
| 怎么申诉：可申诉 / 处理中 / 账户正常或游客 | HelpArticleAppeal.dc.html（9d92c381992d）、HelpArticleAppealPending.dc.html（351214e3823a）、HelpArticleAppealNormal.dc.html（b2f6a28bb79c） | 按当前账号状态切换主按钮 | getArticle；getMe · risk、listAppeals（经桥或 H5 令牌；游客不调） |
| 邀请好友规则 | HelpArticleInviteRules-v2.dc.html（d762d2754cab） | 邀请页「完整规则」 | getArticle；正文待负责人提供（06 Q-F4） |
| 邀请奖励活动规则 | HelpArticleInviteReward.dc.html（484f4baa796f） | 邀请页「活动规则」、登录页【规则】 | getArticle；正文待运营起草 |
| 收不到验证码 | HelpArticleLogin.dc.html（ba58d58acf95） | `help_links.login_help` | getArticle；正文待运营提供 |
| 新手 | HelpArticleNewbie.dc.html（6cdbdfa63901） | 分类「新手教程」 | getArticle |
| 分享规则（公开版） | HelpArticleShareRules.dc.html（935601e3992c） | 分享页、分享赚入口 | getArticle；内测隐藏（TRADE-21） |
| 提现规则 | HelpArticleWithdrawRules-v2.dc.html（489237b392f0） | `help_links.withdraw_rules` | getArticle；数值由配置渲染（BR-WDR-04 细则、BR-TEXT-13） |
| 比价订单说明 | HelpArticlePriceCompare-v2.dc.html（76cdad420e62） | `help_links.price_compare`（唯一一篇，淘宝订单详情「查看说明」也打开它） | getArticle；正文由运营定稿 |
| 深色（首页 / 文章） | HelpDark.dc.html（fb8a31afc715）、HelpArticleDark.dc.html（625f39bb2211） | 系统深色 | 同上；自绘示意图不换色 |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | 请求失败 / 无网络 | 50001；本地 |

## 2. 组件

分类宫格（名称 + 副标题）、常见问题列表、文章页（标题 + 更新日期（BR-TEXT-11 月-日）+ `article-body` 正文 + 自绘示意图）、底部「没找到答案？联系客服」卡；申诉文章底部主按钮按状态：【去申诉】→ `RiskNotice` / 【查看申诉进度】→ `Appeal` / 正常态不给申诉按钮。

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 常见问题与正文 | 运营内容（BR-TEXT-18、BR-TEXT-13 词库扫描），不进字典 |
| 加载失败 | BR-TEXT-14 表 C `h5.load_failed` |
| 分类名与副标题、「没找到答案？ / 联系客服，人工帮你看」、找回指引小标题与图注、申诉文章状态句与按钮 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| listArticles | 首页、分类 | 20001（help_section 与 category 不配） |
| getArticle | 文章页 | 30701 |
| getMe / listAppeals | 申诉文章（已登录） | 10001（转游客写法） |

## 5. 权限点与开关

分享规则文章只在公开版；`help_links` 未配置的键不显示入口（契约 Config.help_links）。

## 6. 稿上没画、实现要做的

大字号下长文与示意图（`AdaptLargeTextHelp` 为证据稿，不在本批）；读屏的示意图替代文字；文章内链接经桥打开。文章正文、订单号样例（`sample-data.md` 登记的找回样例）与更新日期为样例或占位，不自拟规则。

## 7. 待定与不一致

- 04 / 契约 `help_links` 缺分享规则与 `faq.invite_code_bind`；首页常见问题的人工排序没有字段承载，待上游（契约线）。
- 基本模式下帮助页「联系客服」（微信 SDK 未初始化）怎么处理未定，待上游（编排 / Jev）。
- 返利规则、邀请规则、提现规则正文待负责人提供（06 Q-F4），比价说明与活动规则正文待运营定稿，待上游。
