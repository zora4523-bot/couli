# 官方画面证据索引

观察日期：2026-10-01，Asia/Shanghai。使用独立浏览器会话 `refs-v2` 正常打开官方网页、浏览截图轮播并截取页面，没有下载原始媒体。截图已逐张打开核对。以下证据只支持图中可见内容，不能证明真实 App 当前全部交互。

临时证据目录：`/tmp/couli-reference-evidence/`。本索引不附带第三方图片；截图不提交到公开仓库，不用作凑狸 Logo、图标或商品素材。该目录可能被系统清理，失效后应从官方链接重新观察。文件名中的数字是本轮浏览器轮播位置，不是 App 版本号。

| 参考 / 官方来源 | 有效截图文件（均在上述目录） | 已直接看到 | 证据边界 |
| --- | --- | --- | --- |
| [Apple Store](https://apps.apple.com/cn/app/apple-store/id375380948) | `apple-store-01.png`、`apple-store-02.png` | iPhone 宣传图中的商品卡与价格、订单摘要、预计送达与进度条 | 静态商店素材；没有下单或回跳实测 |
| [返利网](https://apps.apple.com/cn/app/id591584458) | `fanli-app-store-01.png`、`fanli-app-store-02.png` | 首页输入区域、粘贴按钮；个人页可用余额、提现及其他资金入口 | 不能证明剪贴板权限、到账速度、费用或提现结果界面 |
| [Perplexity Search](https://www.perplexity.ai/hub/products/search) | `perplexity-search-citations.png` | 问题、回答、来源数量、引用标记、展开来源卡 | 官方网页界面示意，未确认为手机端截图；不是商品卡画面 |
| [Rakuten Rewards](https://play.google.com/store/apps/details?hl=en&id=com.ebates) | `rakuten-google-play-01.png`、`rakuten-google-play-02.png`、`rakuten-google-play-balance.png` | Confirmed / Pending 分组、See Activity、Shopping Trips、收款方式与礼品卡入口 | 开发者 Google Play 素材；不能凭样机外框认定运行系统；未实际提现 |
| [一淘](https://apps.apple.com/cn/app/id451400917) | `etao-app-store-01.png`、`etao-app-store-02.png` | 钱包图与三个编号步骤、优惠商品图、购物车商品行 | 钱包兑换支付宝卡包不是现金提现；没有验证跟单时效和外跳返回 |

补充文字来源：

- [Perplexity 购物介绍，2024-11-18](https://www.perplexity.ai/en-GB/hub/blog/shop-like-a-pro)：说明商品卡及商家跳转方向，是有日期的产品发布资料；本轮内嵌演示未形成可读卡片截图，不能用来证明当前移动布局。
- [Rakuten Account FAQ](https://www.rakuten.com/help/category/account-questions-26578301675411)：解释账户不同金额状态及 Shopping Trips 的用途，不能替代实际页面操作验收。

采集限制与未采用材料：

- 美国区 App Store 在此浏览器重定向到中国区；Rakuten 改用 Google Play 官方开发者页，Perplexity 改用官方产品页。
- `perplexity-shopping-cards.png` 是黑色视频区域，`perplexity-shopping-hero.png` 有 Cookie 浮层；二者不是有效产品界面证据。iPhone 下载页只有下载入口，也不作布局证据。
- Rakuten 移动官网本轮未正常显示手机界面图片，其网站截图不作 App 布局证据。
- 曾查看什么值得买官方 App Store 图；为维持最终 5 个参考并更贴近粘贴和提现场景，选择返利网。`smzdm-app-store-*.png` 仅为候选观察材料，不计入最终五项证据。

国内粘贴、购买外跳返回、订单跟踪、余额提现四场景的采用范围与未知项，见 [README §7](README.md#7-国内四个关键场景证据与尚待验证处)。第三方画面仅作参考，凑狸的功能、文案和平台承诺仍以 `规划/` 为准。
