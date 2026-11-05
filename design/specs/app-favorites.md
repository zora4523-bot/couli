# 收藏夹 Favorites（App 原生）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Favorites`（需要登录；入口 in_app / push，不能由深链打开，01 §4.2）；从哪来：「我的」宫格、分享赚 `ShareHub`「从收藏夹选」（公开版）；去哪：`ProductDetail`、购买（同搜索列表卡）、`ProductShare`（公开版【去分享】）、`Home`（空态）
- 需求：01 §4.2 `Favorites` 行；F-PROD-12（① – ⑧）、F-SHARE-11 ③；规则只引编号：BR-PRICE-03（列表底口径句）、BR-PRICE-13、BR-PROD-10、BR-TEXT-24、BR-ATTR-10、BR-ID-10；验收：AC-S1-139、AC-S1-138（从收藏夹选）、AC-S1-158、AC-S1-185；任务：APP-16、HM-12（M-公开，不计入内测出门）
- 可参考的已合并页面：搜索列表卡（第 1 批 `Search-v2` 同一组件，原生仓库派发前核对）
- 是否资金或归属页面：否（购买仍只经 `POST /v1/links/{link_id}/open` 复核）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 列表（含失效商品） | Favorites-v2.dc.html（b45d3fa5a8df） | 有收藏 | listFavorites · 200 · example（items[].invalid、product_card） |
| 空态 | FavoritesEmpty-v2.dc.html（c623d5a9f2ab） | 没有收藏 | listFavorites · 200，items 置空 |
| 管理（多选删除） | FavoritesManage-v2.dc.html（e6d7c799bd76） | 点导航栏「管理」 | 本地选择；删除调 batchDeleteFavorites |
| 分享赚「从收藏夹选」（公开版） | FavoritesPickShare.dc.html（ecf1c8d7d03e） | 从 `ShareHub` 点「从收藏夹选」 | listFavorites；卡片按钮换【去分享】进 `ProductShare`；失效项不能选；收藏为空用 `share_hub.favorites_empty`（版式同空态，未单独出稿） |
| 深色 | FavoritesDark.dc.html（2e22407b8b3d） | 系统深色 | 同列表；商品图与平台图标按图片处理不换色 |
| 加载失败 / 断网 | StateLoadFailed.dc.html（aea7c5d30a24）、StateNetworkError.dc.html（022db8798446） | 请求失败 / 无网络 | 50001；本地 |
| 删除中 | 不适用（无画板） | 请求在途 | 本地：删除按钮置灰 |
| 无返利汇总提示（2026-11-05） | 不适用（无画板） | 已加载的项里有 `product_card.rebate_basis=no_rebate` | listFavorites；这些项不出卡，列表顶部一条汇总提示与【清除】（batchDeleteFavorites），08 BR-PRICE-08 细则「无返利不出卡」 |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 列表卡 | 列表商品卡（同搜索）+ `PlatformBadge`（14px 官方图标，读屏读平台中文名） | product_card、platform | 点卡进详情；主按钮同搜索卡 |
| 失效卡 | 置灰卡 + 底行右侧次按钮【删除】 | invalid=true | 不显示价格与返利、不可购买；删除读屏名带商品名 |
| 列表底 | 价格口径句（每屏一次） | — | 有券 / 无券混排用 `price_basis.general` |
| 管理态 | 勾选 + 全选 + 底栏【删除（n）】 | 已加载项 | 全选只选当前已加载项（F-PROD-12 ⑤） |
| 空态 | 页面底色上的线性星形图标 + 说明 +【去首页逛逛】 | — | 回首页 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 空态 | BR-TEXT-14 表 C `favorites.empty` |
| 失效标记、删除成功 | 表 C `favorite.invalid`、`favorite.removed` |
| 无返利汇总提示与清除（2026-11-05） | 表 C `favorites.no_rebate.notice`、`favorites.no_rebate.clear` |
| 列表底口径 | 表 C `price_basis.general`（BR-PRICE-03） |
| 从收藏夹选 | 表 C `share_hub.go_share`、`share_hub.favorites_empty` |
| 管理 / 完成 / 删除 / 全选 / 失效说明 / 空态按钮 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| listFavorites | 进入、下拉刷新、翻页（游标） | 10001 |
| removeFavorite | 失效卡【删除】 | 20001、10405 |
| batchDeleteFavorites | 管理态【删除（n）】；无返利汇总提示的【清除】 | 20001、10405 |

## 6. 稿上没画、实现要做的

管理态勾选状态的读屏播报；删除后轻提示与焦点回到列表；加载更多与到底；大字号下卡片两行标题。开关：不做开关隐藏（F-PROD-12）；平台转链开关关闭时卡片按 BR-PROD-10 降级；「从收藏夹选」只在公开版（TRADE-21）。画板上的商品、价格与券均为样例（`couli-runs/design-hifi/sample-data.md`）。

## 7. 待定与不一致

- 契约 `routes.json` 尚无 `Favorites`（01 §4.2 有），「从收藏夹选」的承载（`Favorites` 带模式参数或 `ShareHub` 内子页）也未定，待上游（契约线）。
- flow-map §12.10「先进商品详情再点分享赚」与 01 F-SHARE-11 ③ 不符，以 01 为准，待上游（设计文档回写）。
- 契约 `texts.default.json` 尚无 `price_basis.general`、`share_hub.*`，待契约线同步。
- 2026-11-05 商品详情 v3 定稿带出的组件改动（`docs/changes/20261105-商品详情v3定稿.md`；负责人「列表卡也统一用这种平台标签」，并定这类改动按规划好的组件为标准）：卡片标题前的平台标识改为实底文字标签（03 §10.2 `PlatformBadge` 标题标签形态，`platform.tag.*`），购买按钮改为一行「购买预估返 ¥x」（`btn.buy.rebate`；拿不到金额「购买可返利」，08 BR-TEXT-12 细则「购买按钮」），卡上不显示「预估返后」（BR-PRICE-09）；券前行等其余写法等列表卡改版时按组件规范统一；列表底部口径句与卡上 i 图标照旧（BR-PRICE-03；列表卡改版时按组件规范复核，变更记录 §7）。本页画板仍是旧写法，按组件实现，画板待同步。收藏夹里取到无返利的商品不出卡（不显示标题、图、价格与购买按钮），只在列表顶部出一条汇总提示「有 N 件收藏的商品暂无返利」（`favorites.no_rebate.notice`，N 按已加载各页累加）与【清除】（`favorites.no_rebate.clear`，删除这些收藏记录，不弹确认）；不给【搜相似商品】，不自动删除，恢复有返利照常出卡；已失效照旧置灰；收藏全是无返利时不出空态；「从收藏夹选」同样不列（01 F-PROD-12 ③，08 BR-PRICE-08 细则「无返利不出卡」；不出卡依负责人「无返利的商品不会出现在 APP 上」，提示形式与【清除】是代理补全的默认；同日回写的「按已失效写法置灰、可删除」审查后作废）。画板未画这条提示，按文案键实现。
