# 去购买（商品详情与各处商品卡上的购买链路，App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 页面：不是独立路由，状态画在 `ProductDetail` 上，首页、搜索、热销榜、AI、识别卡上的购买共用；授权半屏与下单须知另见 [app-auth-sheet.md](app-auth-sheet.md)、[app-jump-tip.md](app-jump-tip.md)；登录成功后直接继续购买、不插页（00 D36 ②）
- 需求：01 F-LINK-01、F-LINK-03～07、F-PROD-07；规则只引编号：BR-PRICE-08、BR-PRICE-13、BR-PRICE-14、BR-ATTR-17、BR-ATTR-21、BR-ID-17～19；验收：AC-LINK-xx（同号规则）；任务：05 APP-06 / HM-05
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：是（open 决定 link 与归属；价格、返利以复核为准）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 正在确认授权结果 | ProductAuthConfirming.dc.html（f5f53fc6de38） | 授权回来到继续购买之间 | bindUnion；失败或超时按授权失败处理 |
| 关闭授权说明后 / 授权未完成 | ProductAuthDeclined-v2.dc.html（c5539d265ae0）、ProductAuthFailed-v2.dc.html（14ea5ac603b6） | 关闭半屏 / 授权失败 | 本地；【仍去购买（无返利）】 |
| 淘宝暂时无法下单 | ProductAuthUnavailable-v2.dc.html（f775768afb21） | 站长授权失效期间 | 30101 / 30102 `reason=auth_unavailable` |
| 返利已停用 | ProductAuthBlocked.dc.html（dc9d0fb3bf00） | 30153；30103、30151 同版式 | 30153、30103、30151 |
| 正在打开 / 超时 | ProductBuyOpening-v2.dc.html（903bc25c3932）、ProductBuyTimeout-v2.dc.html（80e4e2d03ad9） | open 在途 / 超时 | openLink · OpenLinkUnchanged；本地超时 |
| 复核失败但有缓存 | ProductRequoteCached.dc.html（090fa6e4532c） | requote_failed（BR-PRICE-13） | openLink · 200 |
| 价格无法确认 | ProductPriceUnconfirmed.dc.html（ced60eef7ace） | 复核失败且无缓存 | 50303 |
| 维护中 | ProductConvertPaused-v2.dc.html（ff932ffd13da） | 转链暂停 | 50301 |
| 商品已下架 | ProductOffShelf-v3.dc.html（a29f3a731e96）；深色 ProductOffShelfDark.dc.html（9a3bdffa1234） | open 复核为下架 | 30141；列表卡、AI 卡写法在同一画板说明 |
| 外跳降级 | ProductJumpNotInstalled-v2（e5cadf078ccf）、ProductJumpBrowser-v2（afb8f78a30c7）、ProductJumpHarmonyH5-v2（cce2969ec0db）、ProductJumpSdkFailed-v2（042eb188f2f1）、ProductJumpUnsupported-v2（42abebb66ddc） | 未装淘宝 / 京东、鸿蒙降级网页、SDK 打不开、本设备不支持 | `contracts/apps.json` 降级链（F-LINK-06）；本地 |
| 待跟单卡 ×3 | ProductPendingTrack-v2（e90f43626a97）、ProductPendingTrackDecided-v2（f6c793b18da1）、ProductPendingTrackClaim（55d77235a336） | 外跳回来；通知权限未定 / 已定；满条件出「未跟单？去找回」 | listPendingTracks（`show_claim_entry`，BR-ATTR-21 ②③）；dismissPendingTrack |
| 价格变动确认 / 取消 | ProductPriceChanged-v2（b4762e20bbf2）、ProductPriceChangedCancelled-v2（438bcebacef1）；深色 ProductPriceChangedDark（fb48da5c7168） | 复核价差达阈值 | openLink · OpenLinkPriceChanged |
| 价格变动且返利变 0 / 取消 | ProductPriceChangedRebateGone-v2（8a59a8cccb84）、ProductPriceChangedRebateGoneCancelled-v2（8e2b1229747e） | 两者同时 | 同上 |
| 返利变 0 / 取消 | ProductRebateGone-v2（fda0dc4c0c5d）、ProductRebateGoneCancelled-v2（49af909f51a5） | new_rebate_max_fen=0 | openLink · 200 |
| 券已失效 | ProductCouponGone.dc.html（b2f4ae6b6880） | availability=coupon_gone（BR-PRICE-14） | openLink · 200 |
| 比价无返利 / 取消 | ProductPriceCompareNoRebate-v2（a20873a07d91）、ProductPriceCompareCancelled-v2（12ebd4f5436e） | no_rebate_cause=price_compare | openLink · OpenLinkPriceCompare |
| 商品卡能力降级 | ProductCardDegrade-v2.dc.html（d4ffaa8f7552） | 五种平台能力降级，条件出现 | product_card 字段 |

文件名省略的后缀均为 `.dc.html`。画板上的商品、价格、返利、订单均为样例数据。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 购买按钮 | `BuyButton`（loading、禁用、「稍后再试」） | cta | 点击调 openLink；在途可取消 |
| 确认 | `Dialog`（主次按钮按 08 表 A / 细则） | open 响应 | 继续 / 取消后卡片更新为最新值 |
| 下架 | 原位置灰（图片去色、标题次要色、不显示价格与返利）+「商品已下架」+【搜相似商品】 | availability | 【搜相似商品】是唯一可点（AI 卡另有【换一批】） |
| 待跟单卡 | 卡片 + 开启通知 +「去找回」入口 | pending-tracks | 去找回 → `FindOrder`（[app-find-order.md](app-find-order.md)） |

## 3. 文案键

错误与拦截：BR-TEXT-14 表 A 30101～30153、30141、50301、50303；打开中 / 超时：`buy.opening`、`buy.opening.cancel`、`buy.timeout`；`jump.taobao_sdk_unavailable`；下架：表 A 30141、`btn.search_similar`；按钮：`btn.buy.*`。

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| openLink | 点购买 | 10001、30101、30102、30103、30111、30121、30141、30143、30144、30151、30153、50301、50303、10405 |
| listPendingTracks / dismissPendingTrack | 外跳回来、关闭卡片 | 20001、10405 |

## 7. 待定与不一致

- 待上游（规划）：下架后不显示价格、返利、券与价格走势是画板做法，BR-PRICE-14 细则只写置灰与【搜相似商品】（待回写清单第 2 条）。
- 画板说明与细则：ProductOffShelf-v3 不是「回到原卡后原按钮照常可用」的情形——下架卡回来后仍只有【搜相似商品】可点（BR-PRICE-08 细则；清单第 13 条）。
- 设计自定（可微调）：30153 弹窗【联系客服】为主、【仍去购买（无返利）】为次、无右上关闭；「正在确认授权结果」不给【取消】。
