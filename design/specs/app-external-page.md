# 第三方页容器 ExternalPage（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`ExternalPage`（auth none，入口 in_app / push / deeplink；深链打开时主机须在下发的白名单内；参数 `url` 必填、`title`、`nav_style` 可选）；从哪来：首页卡片、运营配置的外链；去哪：系统浏览器（【在浏览器打开】，只在用户点击时）、`Search`（【去搜索】）、原生商品详情（页内商品页转回原生）
- 需求：01 §4.2 `ExternalPage` 行；F-LINK-11、F-PRIV-08；规则只引编号：BR-ATTR-29（含细则）、BR-ID-33 细则（url 原样、不拼个人数据）、03 §4.4、§5.1、§5.6；验收：AC-S1-70、AC-S1-80、AC-S1-82、AC-S1-131、AC-S1-185；任务：APP-04、HM-03
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：是（不留没有归因的购买入口）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 | ExternalPage.dc.html（62659243f951） | 非联盟平台页面加载完成 | 路由参数 url / title；`/v1/config.external_hosts` |
| 拦下平台页面 | ExternalPageBlocked.dc.html（49d847862a25） | 页内导航去往联盟平台网页（规则表含包内快照） | 本地导航判定（APP-04）；只给【去搜索】 |
| 不处理下载 | ExternalPageDownloadBlocked.dc.html（1f9899f2b9b1） | 页内发起下载 | 本地；取消下载后提示一次 |
| 连不上 | ExternalPageError.dc.html（ed710d9cdf8b） | 主框架连不上、解析失败、超时或证书错误 | 本地；隐藏【在浏览器打开】 |
| 平台商品无法识别 | ExternalPageProductUnresolved.dc.html（349dec8df20a） | 页内平台商品页转原生时识别不了 | 本地：按 `link_patterns` 识别不出商品；留在当前页 |
| 深色 | ExternalPageDark.dc.html（a3eb6e6553ad） | 系统深色 | 原生标题栏随令牌；第三方页面原样显示 |

画板上的 `brand.example.com` 与页面内容为占位。

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 标题栏 | 固定显示当前主机名 + 副标题（title）+【关闭】+【在浏览器打开】 | 当前 URL 主机名、title | 返回键先页内后退；命中平台链接形态时不显示浏览器出口 |
| 容器 | `ExternalWebView`（不注入桥、不改页面，UA 只加本 App 后缀） | url | 只放行 https；非 https、`intent://`、下载一律取消并上报 |
| 提示 | 页内轻提示 / 错误页 | — | 拦下后留在当前页 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 标题栏 | BR-TEXT-14 表 C `external_page.close`、`external_page.open_in_browser` |
| 拦下平台页面 | 表 C `external_page.union_host_blocked` |
| 下载 | 表 C `external_page.download_blocked`；当前页没有浏览器出口时 `external_page.download_unsupported` |
| 连不上 | 表 C `external_page.load_failed` / `.retry` / `.close` |
| 商品无法识别 | 表 C `external_page.product_unresolved` |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getConfig | 启动时已取（external_hosts、external_page.nav_host_sample_bp、link_patterns） | — |

## 5. 权限点与开关

活动转链上线前（P1）不用于联盟平台的活动页与商品页，后台保存时拦截（BR-ATTR-29）。

## 6. 稿上没画、实现要做的

全屏视频播放；子框架导航逐端核对、做不到的端按保守降级（03 §5.6）；读屏播报拦截与错误；从深链打开时的主机白名单校验。

## 7. 待定与不一致

无。
