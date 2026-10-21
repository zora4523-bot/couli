# 可信容器 WebPage 与通用加载 / 断网态（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`WebPage`（auth none，入口 in_app / push，不能由深链打开，参数 `url` 只接受 `bridge_origins` 内的 https）；所有 kind=h5 的路由（`Messages`、`InviteShare`、`Help`、`Notice`、`Rules`、`Agreement`、`Ledger`、`FindOrder`、`Earnings`）都在本容器里打开；通用加载失败 / 断网两张供收藏夹、消息、帮助、找回记录等页面共用
- 需求：01 §4.2 `WebPage` 行；F-H5-02、F-H5-04、F-CFG-08；规则只引编号：BR-ID-10 细则「路由入口矩阵」、BR-ID-32、03 §5（容器与桥）、03 §8.3（页面级开关与维护页）；验收：AC-H5-04（同号规则）、AC-S1-82、AC-S1-157、AC-S1-185；任务：APP-04、HM-03、F1-01
- 可参考的已合并页面：`apps/h5/src/components/retry/**`、`apps/h5/src/components/base/ErrorState.tsx`（H5 内的重试页）
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正常 | WebPage.dc.html（8462e7f48f77） | 白名单 origin 加载完成 | `/v1/config.bridge_origins`、`h5_base_url`、`h5_release` |
| 加载中 | WebPageLoading.dc.html（1be4a2650b67） | 首屏未完成 | 本地骨架 |
| 加载失败 | WebPageError.dc.html（d9be49c55f09） | 加载失败或白屏检测命中（F-H5-04） | 本地；【重试】重新加载 |
| 页面维护中 | WebPageMaintenance.dc.html（d093e9ad2b39） | 页面级开关 `h5.route.<page>.enabled=false` | getConfig · features.flags；原生直接显示维护页，不加载 H5（03 §8.3） |
| 通用：加载失败重试 | StateLoadFailed.dc.html（aea7c5d30a24） | 原生页列表或详情请求失败 | 表 A 50001 / 5xxxx |
| 通用：网络错误 | StateNetworkError.dc.html（022db8798446） | 无网络 | 本地网络状态（断网没有错误码） |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 容器 | `TrustedWebView` + 原生标题栏 | url | 只注入本 App 桥；不向页面注入脚本或样式（03 §5.1） |
| 失败 / 维护 / 断网 | 原生错误页：图标 + 说明 + 主按钮 | — | 失败与断网【重试】；维护【返回】 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 加载失败 | BR-TEXT-14 表 C `h5.load_failed` |
| 通用加载失败辅助句 | 表 A `error.50001` / 5xxxx |
| 断网「网络不可用 / 请检查网络后重试」、维护页说明句与【返回】 | 08 无键（断网建议 `net.unavailable`），用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getConfig | 启动时已取（bridge_origins、页面级开关） | — |
| issueH5Token（桥 `auth.getH5Token`） | H5 页内按需 | 10405 |

## 5. 权限点与开关

`/v1/config.features.flags` 的 `h5.route.<page>.enabled`（页面级维护开关，03 §4.3、§8.3）；`bridge_disabled_methods`（契约 Config）。

## 6. 稿上没画、实现要做的

白屏检测上报（首屏 3 秒，F-H5-04）；容器返回键先页内后退；读屏播报失败与维护状态；深色下容器底色随令牌、H5 跟随系统（00 D35）。

## 7. 待定与不一致

- 维护页说明句与【返回】是设计起草（08 无键），断网句建议登记 `net.unavailable`，待上游（BR-TEXT-14）。
