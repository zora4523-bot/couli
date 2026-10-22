# 基本模式 BasicMode（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- **底稿首页以第 1 批 `HomeGuest-v3` 为准**：本批 `BasicMode-v2` 画「与游客首页的差别」时用的是旧游客首页（第 1 批 v1.1 对抗评审 V1-14）；第 1 批 `HomeGuest-v3` 已改为完整商品流 + 价值卡、只少个人模块，商品流、价值卡与金刚区按 `HomeGuest-v3` 实现，本页只保留下面 §2 列的基本模式差别；画板下次改稿时同步
- 路由：`BasicMode`（auth none，入口 in_app）；从哪来：首启弹窗或二次说明点【仍不同意】、隐私中心撤回同意；去哪：`Search`、`ProductDetail`（只读）、`Settings`（右上【设置】，[app-settings.md](app-settings.md) `SettingsBasic`）、`PrivacyCenter`、`Agreement`、`About`、`Help`；【开启完整功能】→ `Launch` 首启弹窗
- 需求：01 §4.2 `BasicMode` 行；F-PRIV-02、F-PRIV-03；规则只引编号：BR-ID-02 细则、BR-ID-11、BR-ID-16（基本模式不读剪贴板）、BR-PRICE-03、BR-TEXT-24；验收：AC-PRIV-02（同号规则）、AC-S1-154、AC-S1-158、AC-S1-185；任务：APP-02、HM-02
- 可参考的已合并页面：第 1 批首页（原生仓库派发前核对）
- 是否资金或归属页面：否（不能登录、不能购买）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 首页（只读） | BasicMode-v2.dc.html（df31418fe202） | 未同意隐私政策 | 只发 BR-ID-11 允许的匿名请求（首页配置、搜索、详情只读），不初始化任何 SDK、不注册设备 |
| 深色 | BasicModeDark.dc.html（d7770416eca3） | 系统深色 | 同上；商品图与平台图标按图片处理 |

画板上的商品与价格为样例；底稿与第 1 批的差异见页首说明。

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 顶栏 | 搜索框（占位见 §3 `basic.search.placeholder`）+ 右上【设置】 | — | 进搜索、设置 |
| 开启完整功能卡 | 卡片 + 主按钮 | — | 重新展示首启隐私弹窗 |
| 商品流 | 同第 1 批 `HomeGuest-v3`：网格商品卡与横滑卡（按画板；原写「列表商品卡」为规格笔误，2026-10-22 编排裁定 D10-115 G-V12）+ `PlatformBadge`（官方图标）+ 列表底口径句（`price_basis.general`） | 首页配置 | 点购买、收藏等需要同意的动作先走隐私弹窗（BR-ID-02），不因路由丢弃自动弹窗（BR-ID-11） |
| 不放的 | 任何粘贴入口、剪贴板识别、个人模块 | — | — |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 开启完整功能卡 | BR-TEXT-14 表 D `privacy.basic_mode.notice` / `.enable` |
| 列表底口径 | 表 C `price_basis.general`（BR-PRICE-03） |
| 搜索框占位 | 表 C `basic.search.placeholder`（基本模式不提粘贴链接，D10-115 更正） |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getPage（首页配置）/ searchProducts / getProduct | 首页、搜索、详情（匿名） | 30701、50304、30141、30143 |

## 5. 权限点与开关

Router 在基本模式只放行首页、搜索、商品详情与设置、隐私中心、协议、关于、帮助（03 §4.4 / APP-02）。

## 6. 稿上没画、实现要做的

从基本模式开启完整功能后清除只读状态并重新初始化；深链、推送在基本模式下按入口守卫丢弃；读屏提示当前为基本模式。

## 7. 待定与不一致

- 画板「与游客首页的差别」按旧游客首页画，开发以第 1 批 `HomeGuest-v3` 为准；画板随下次改稿同步（微调项，见变更记录待回写清单）。
- 基本模式下帮助页「联系客服」的处理未定，见 [app-help.md](app-help.md) §7。
