# 分享商品 ProductShare（含分享海报，App 原生）

- 核对版本：规划提交 b8b7dac（负责人 2026-10-21 定稿，`docs/changes/20261021-App内高保真第1批定稿.md`）；代码主干 67d7a4df（2026-10-21 核对；派发前再核对一次）
- 画板存放：`couli-runs/design-hifi/project/<文件名>.dc.html`（PNG 在 `review-shop/v1/png/`），不入公开仓库；完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 1 批定稿」
- 路由：`ProductShare`（参数 `platform`、`product_key`，可带来源 `link_id`；需要登录、已绑手机、已完成该平台授权；入口 in_app；M-公开，内测期与【分享赚】一起隐藏，TRADE-21）；从哪来：商品详情【分享赚】、`ShareHub`；去哪：微信、系统分享、相册
- 需求：01 F-SHARE-01～03、F-SHARE-08、F-SHARE-10、F-SHARE-12、F-SHARE-13；验收：AC-SHARE-xx（同号规则）；任务：05 APP-13 / HM-10
- 可参考的已合并页面：无（派发前按代码主干核对）
- 是否资金或归属页面：是（分享链接带分享者归因，BR-ATTR-05、BR-ATTR-10）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 生成中（详情页加载卡） | ProductShareConverting-v2（ec81dc299be1） | 点【分享赚】后 | `POST /v1/shares`（04 §6.3；契约未落，见 §7） |
| 分享链接生成失败 | ProductShareUnavailable-v2（df1fc6393a45） | 生成失败（授权类错误另走授权引导） | 同上，失败 |
| 淘宝口令 | ProductShare-v2（3cd465ec8ad7） | 生成成功（淘宝有券） | 同上 · 200 |
| 京东短链（无券） | ProductShareJd-v2（e4717dadb85d） | 京东无券 | 同上 |
| 已复制 | ProductShareCopied-v2（cbdc5651dec3） | 点复制 | 本地 |
| 编辑 / 已编辑 / 改勾选前确认 | ProductShareEdit-v2（80d1f7770303）、ProductShareEdited-v2（d65a1733ecab）、ProductShareEditOverwriteConfirm-v2（49c469417313） | 编辑文案、编辑后改勾选 | 本地；勾选项只按 `copy.parts` 实际返回的段出现 |
| 未选图 | ProductShareNoImage-v2（306d5d3d6dd2） | 素材图一张都没选 | 本地 |
| 未装微信 | ProductShareNoWechat-v2（406fd2f861d0） | 本机无微信 | 本地 |
| 相册用途说明 / 已保存 / 保存失败 | ProductSharePhotoPermission-v2（c4fecbe847ee）、ProductShareSaved-v2（c34ad6e47378）、ProductShareSaveDenied-v2（d35e0665bd5f） | 保存图片前（iOS / 鸿蒙）/ 成功 / 无相册权限 | 本地（BR-TEXT-14 表 D 权限用途） |
| 分享海报 | PosterShare-v2（319eafa28ce7） | 选海报 | `poster_url`（服务端出图，TECH-13） |
| 深色 | ProductShareDark（df86a7532ead） | 系统深色（00 D35） | 同浅色 |

文件名省略的后缀均为 `.dc.html`。画板上的商品、价格、口令、短链均为样例数据。

## 2. 组件

| 区域 | 组件 | 数据 | 交互 |
| --- | --- | --- | --- |
| 商品摘要 | `ProductCard`（大卡）、`PlatformBadge`（14px） | product_card | — |
| 素材图 | `ShareMaterialPicker` | images[] | 多选、全选、保存张数提示 |
| 文案 | `ShareCopyEditor` | copy.parts | 勾选、编辑；末尾固定口令 / 链接与价格口径句（不能删） |
| 操作 | 复制、去微信、系统分享、保存图片 | — | 未装微信不列微信渠道 |
| 预估推广收益提示 | 文本 | share 报价 | 不进分享文案 |

## 3. 文案键

生成失败：`share.generate_failed`、`share.retry`；复制 / 保存 / 微信：`share.copy_full`、`share.copy_link_only`、`share.copy_tpwd_only`、`share.copied`、`share.save_images`、`share.saved`、`share.open_wechat`、`share.wechat_unavailable`、`share.system_share`；勾选与覆盖：`share.include*`、`share.copy_text.regen_confirm`；推广收益提示：`share.est_promo`；文案末尾口径句：`price_basis`、`price_basis.general`（BR-PRICE-17）。

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| `POST /v1/shares`（契约未分配 operationId） | 进页生成物料 | 授权类 30101 / 30102 / 30111 走授权引导；其余以契约为准 |

## 6. 稿上没画、实现要做的

键盘弹起时编辑区可见（适配稿 `AdaptKeyboardProductShareEdit` 为证据稿，不在本批）；海报不放平台图标、来源只写文字（凑狸自有素材）。

## 7. 待定与不一致

- 待上游（契约）：`POST /v1/shares` 与路由 `ProductShare` 尚未进 `openapi.yaml` / `routes.json`。
- 待上游（规划）：分享文案末尾附价格口径句按 BR-PRICE-17 画；08 BR-TEXT-20 细则「分享页文案」默认模板与例子没有这一行（待回写清单第 5 条）。
