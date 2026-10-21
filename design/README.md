# 凑狸 · 品牌与设计素材

品牌设计待办（规划/06 §E Q-E1–Q-E6）的素材位置。项目统一入口是根目录 [brand.config.json](../brand.config.json)，使用与修改流程见 [品牌接入](../docs/brand-integration.md)。素材继续在本目录维护，不在根目录复制第二套 Logo 或配色。

2026-10-01：第二版 Logo、语义配色和设计令牌已作为项目当前采用基线，视觉方案沿用已有修订。先看 [品牌概览](brand/brand-overview.png) 与 [可点击展示页](brand/index.html)，再看 [Logo 使用规范](logo/README.md)、[配色](colors/colors.md)及[五个 App 参考](references/README.md)。当前展示页通过根配置生成的 CSS / JS 消费品牌；三端工程尚未创建，素材和展示页接入不代替系统图标制作、平台资源接入或真机验收。

令牌数值唯一维护于 [design-tokens.json](tokens/design-tokens.json)；[variables.css](tokens/variables.css) 与 [brand-config.js](brand/brand-config.js) 由根目录 `python3 scripts/sync-brand.py` 生成，`python3 scripts/sync-brand.py --check` 只读检查生成物漂移。H5 基础控件样式源为 [foundations.css](tokens/foundations.css)，同步时追加进生成 CSS。不要手改生成文件。

展示页可直接在浏览器打开；需要本地 HTTP 预览时，在仓库根目录运行 `python3 -m http.server 8765 --bind 127.0.0.1 --directory design`，访问 `http://127.0.0.1:8765/brand/index.html`。页面无外部脚本或字体依赖，示例数据不会调用商品、AI、支付服务；官方参考链接由点击打开。

**所有素材都不得包含淘宝、天猫、京东、拼多多、美团等平台的商标或近似元素**（规划/01 F-PRIV-08）；平台来源小图标只能放在 `icons/platform/`，并按联盟商标使用规范使用（06 Q-F8）；界面可以使用 `icons/platform/` 里的官方平台标识作来源、授权、支付与分享去向标识（2026-10-05，负责人统一准备）。

本仓库公开，放进来的文件任何人都能看到。未公开的方案、商标申请材料、合同等不要放这里。单个文件不超过 100 MB（GitHub 限制）。

## 清单

| # | 事项 | 放哪里 | 截止 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | 英文名、Slogan | `brand/name.md` | 尽快 | 中文名「凑狸」、英文名 Couli 已定（2026-10-06）；Slogan 待填 |
| 2 | 商标查询与注册 | 不放仓库（只在 `brand/name.md` 记录注册号与类别） | 建议现在 | 待办 |
| 3 | Logo 源文件 | `logo/source/` | W1（10-11） | 第二版作为当前基线：图形、横版、竖版、单色、反白 SVG；对应 PNG 在 `logo/export/`，根配置统一引用 |
| 4 | App 图标 | `app-icon/` | W1（10-11） | 1024 SVG/PNG 与分层源已交付；三端工程资源已接入（BRAND-01，2026-10-19：rebate-ios d0ca07c、rebate-android cd38146 + fdd8265、rebate-harmony c8a30ec，模拟器主屏已核对）；`.icon` 与真机验收待后续 |
| 5 | 启动页 | `splash/` | W1（10-11） | 待办 |
| 6 | 品牌主色、辅色、功能色 | `colors/colors.md` | **10-06** | 第二版作为当前基线；数值唯一源在 `tokens/design-tokens.json`，此文档维护语义与对比度记录 |
| 7 | 参考 App UI/UX 3–5 个 | `references/` | **10-06** | 已交付 5 个官方参考及实看画面记录；包含一淘、返利网，详见参考证据索引 |
| 8 | 设计令牌 | `tokens/` | 10-07 | 当前基线 JSON 已接入本仓库展示页；CSS / 浏览器配置可生成与查漂移，三端工程接入按[品牌接入](../docs/brand-integration.md)后续执行 |
| 9 | 7 个关键页确认 | `wireframes/`（原安排：代理出线框，你确认） | — | 2026-10-04 起不再逐页确认线框，页面改在高保真稿上确认，见第 15 项与[变更记录](../docs/changes/20261005-出图范围补登.md)；7 页线框已出稿，在分支 `design/key-page-wireframes`（未合并），只作高保真稿的内容来源 |
| 10 | Tab 与金刚区图标 | `icons/tab/`、`icons/grid/` | 随第 15 项 | 待办 |
| 11 | 平台标识素材（来源、授权、支付 / 收款、分享去向） | `icons/platform/`（要求见该目录 README） | W1 | 部分已交付（2026-10-19：淘宝、京东、拼多多与 6 个后续平台的官方图入库，天猫、微信、微信支付、支付宝、企业微信待提供；2026-10-05 起负责人统一准备，规划/06 Q-E7、Q-F8；2026-10-06 改为本目录作内置兜底、上线后在后台替换，BR-TEXT-24） |
| 12 | 空态、错误态插画 | `illustrations/` | W3（10-25） | 待办 |
| 13 | 分享海报、邀请海报 | `posters/` | W3（10-25） | 待办 |
| 14 | 商店上架素材 | `store/` | W7 提审前（11-22） | 待办 |
| 15 | 定稿的高保真稿 | App 与 H5 页面放 `hifi/`，**关键页定稿稿含深色版**（规划/00 D35，2026-10-18：登录 4 张先出；首页、详情、订单、钱包、我的在各自定稿批次加深色版；其余页面由实现按令牌推导、评审抽查深色截图）；管理后台稿入库前先逐张核对样例数据与风控规则标识，核对前不放进本公开仓库（代理默认，你可以改） | 随各页定稿 | 部分已交付：管理后台第 1 批（工作台、一框搜、用户查询与详情、订单查询与详情、找回审核）负责人 2026-10-18 定稿「全部按推荐」，画板清单与 sha256 见下方「管理后台第 1 批定稿」；管理后台第 2 批（财务：提现审核与打款、月结账单与对账差错、调账与核销、余额流水与导出、资金看板）负责人 2026-10-18 定稿「全部按推荐」，画板清单与 sha256 见下方「管理后台第 2 批定稿」，规格 `specs/admin-{withdrawals,withdrawal-detail,payouts,settle-bills,recon,adjustments,ledger,fund-dashboard}.md`（2026-10-18）；两批规格都在 `specs/admin-*.md`，画板文件本身留在本机运行目录不入库；App 内高保真第 2 批（2026-10-21 负责人定稿；钱：钱包与流水、订单、找回、提现、AI 订单进度，含 15 张深色稿），画板清单与 sha256 见下方「App 内高保真第 2 批定稿」，规格 `specs/app-*.md` 14 份（2026-10-21）；App 内高保真第 3 批（「我的」与其他：我的、邀请、收藏与消息、设置与账号、注销与账号受限、隐私与协议、帮助与客服、基本模式与更新、容器、AI 页面引导，168 张含深色 29 张）负责人 2026-10-21 定稿「全部定稿吧 先开发 后面在微调」，画板清单与 sha256 见下方「App 内高保真第 3 批定稿」，规格 `specs/app-*.md` 26 份（2026-10-21）；App / H5 其余页面以各批定稿登记为准，未登记的草稿在 claude.ai 画布与本机运行目录，未入库。稿件版本以页面规格里记的文件名与 sha256 为准 |
| 16 | 页面规格（一页一份，给实现者照做） | `specs/` | 各页定稿后 | 进行中：已有 56 份——首份 [specs/admins.md](specs/admins.md)（F1-06i 后台账号列表，2026-10-10，规划/11 §2.6）、管理后台第 1 批 7 份 `specs/admin-{dashboard,search,users,user-detail,orders,order-detail,claims}.md`（2026-10-18）与第 2 批 8 份 `specs/admin-{withdrawals,withdrawal-detail,payouts,settle-bills,recon,adjustments,ledger,fund-dashboard}.md`（2026-10-18）；App 内高保真第 2 批 14 份 `specs/app-{wallet,ledger,earnings,order-list,order-detail,appeal-order,find-order,withdraw,withdraw-reverify,withdraw-records,real-name,payout-account,labor-agreement,agent-chat-orders}.md`（2026-10-21）、第 3 批 26 份 `specs/app-*.md`（2026-10-21，清单见下方「App 内高保真第 3 批定稿」）；模板 [page-spec.md](../docs/templates/page-spec.md)；格式仍在试行，其他页面等试行后再定 |

完成一项后，把「状态」改为「已交付」，或者直接告诉 Claude。

## 管理后台第 1 批定稿（2026-10-18）

负责人 2026-10-18 21:3x 定稿：「第 1 批定稿，全部按推荐」。第 1 批 = 管理后台每天用的 7 页：工作台 / 待办中心、顶栏一框搜、用户查询、用户详情、订单查询、订单详情、找回审核。三条按推荐的决定（工作台「未关闭告警」卡本期不做、位置保留；一框搜无命中不区分「没有」与「没权限」；找回通过后归属锁定、误判只能驳回让用户重提）的落点见 [变更记录](../docs/changes/20261018-后台第1批定稿.md)。

- 规格：[admin-dashboard.md](specs/admin-dashboard.md)、[admin-search.md](specs/admin-search.md)、[admin-users.md](specs/admin-users.md)、[admin-user-detail.md](specs/admin-user-detail.md)、[admin-orders.md](specs/admin-orders.md)、[admin-order-detail.md](specs/admin-order-detail.md)、[admin-claims.md](specs/admin-claims.md)。
- 画板存放：本机运行目录 `couli-runs/design-hifi/project/<文件名>.dc.html`，1 倍 PNG 在 `couli-runs/design-hifi/review-admin/png/`；Codex 对抗审查 3 轮的记录在 `couli-runs/design-hifi/review-admin/review-log.md`。画板与 PNG **不入本公开仓库**，版本以下表 sha256 为准。
- 入库前核对（2026-10-18，逐张，共 51 张）：样例数据不含真实手机号、证件号与真实个人信息（手机号、身份证只以脱敏样式出现）；风控规则编号、处置与阈值为样例（规格里已标）；平台只以文字标识来源，无平台商标图形。

| 页面 | 画板文件 | sha256 |
| --- | --- | --- |
| 工作台 | AdmDashboard.dc.html | `3718723d53238796be2da7871188ba1c05b28a1ac570c394cdf763b236f12d19` |
| 工作台 | AdmDashboardFinance.dc.html | `fc9ce929aa933c0a2865137e0f06e968ed046f49aa3ed5da4d0d9f5274cfded6` |
| 工作台 | AdmDashboardStates.dc.html | `fc31a2cac3d9947a75b33abd50dcf850bd9412aa0cdc2535e77f8667c671d7a7` |
| 工作台 | AdmAdaptDashboard1280.dc.html | `c07d67b2541cd14cdcfcc3b5c0fe949b2cb9ddf71d9bd9cbcfb67f2d2fa82cbb` |
| 工作台 | AdmHomeNoPerm.dc.html | `57e50047eeae5c1f22b7066e92a4328238787aa5ce88b075d0b98be9fc0ddbee` |
| 一框搜 | AdmSearchMulti.dc.html | `39ed7d2ee07e7aa6e28b0957d1d6baddd3e57333355cfdb9b507e1f2d847e479` |
| 一框搜 | AdmSearchNoHit.dc.html | `226c89429f99d3bbf059e4e8b439b31ec868141ef698a48bda1c812026c9caa9` |
| 用户查询 | AdmUsers.dc.html | `d4329585aec84e0cad02ee4d4d352e7dc839fd0190680b27e2adaea758701bf1` |
| 用户查询 | AdmUsersStates.dc.html | `480cc63b87daf36d792f0fd9ec2d12276e064a339d523fb2d93a416a4668a42b` |
| 用户详情 | AdmUserDetail.dc.html | `617be995aeda6445268c63b65fd712aee327fb5fe76d398cac39bc65b8a7808a` |
| 用户详情 | AdmUserDetailFunds.dc.html | `13bbcdfe35068c6d39a0c50b1c498cfe4f67c0adb4603b2b50f875fae50314ff` |
| 用户详情 | AdmUserDetailOrders.dc.html | `99fb8d156049cb837cf5f57d57baeedb44977126b0d8d4188348285ff72d9ade` |
| 用户详情 | AdmUserDetailClaims.dc.html | `0bfa17cdabc22478940cb0d24f5240fc6e4c9e5cad74fd8350cab748a3253556` |
| 用户详情 | AdmUserDetailWithdrawals.dc.html | `7c60b7911225dee8c3f636258ab0df8a619e6f7856e41c6fedf587b35d9a431c` |
| 用户详情 | AdmUserDetailWithdrawalsList.dc.html | `60717727c39fdb9c8fb52b826f93699759b3a00fafddcda7de7c0902a689e49e` |
| 用户详情 | AdmUserDetailTabStates.dc.html | `e1b4965fdc31b5719a075519eb4bb05f53dd3918fadea1bdb52c39f6c7cd4013` |
| 用户详情 | AdmUserDetailRisk.dc.html | `de99943fd976f50d3be2bc5304d3cf2d08890799d0b59a33de89d67d9a273703` |
| 用户详情 | AdmUserDetailNoPerm.dc.html | `3e627744c7b5f7d3abd57bfa3995e792bf3f6e182c0069d8ad8974dd4b23a2d9` |
| 用户详情 | AdmUserDetailDeleting.dc.html | `d6c327e0c084e3a49bfb17e938a1b4f0cda9385152fbea1b641844439b876872` |
| 用户详情 | AdmUserDetailDeleted.dc.html | `46fe2ba3149ca5c599c14072963ed988ee10d9a20bf5f5c4799c8761fb03feae` |
| 用户详情 | AdmUserLevelChange.dc.html | `d000af860f450c26bdc3ca52be05c723a73679df310d9c7029714e28ee911939` |
| 用户详情 | AdmUserInviterChange.dc.html | `639f2c6e034e1059e29af6f28d4a9d1374edb35bc453cb98c52a805818955638` |
| 用户详情 | AdmUserInviterChangeOk.dc.html | `134610f7a9ad823a19bbff7dceddf4a63af3436ccc4e5b2647add06baa43a6a4` |
| 用户详情 | AdmUserInvitees.dc.html | `22b6d035c66683244b26591547d664ef18ea9820c8cc4c7614abd6d11efaa61e` |
| 用户详情 | AdmUserBalanceAdjust.dc.html | `04b54121cb684c003e21333a80ab51c3386e3d8ff866b6136f1528884f14d3e1` |
| 用户详情 | AdmUserUnionReset.dc.html | `0453f5ec337a84d935ca57f43fca38ea721385ba00e8750649b31b53fcc71d2a` |
| 用户详情 | AdmUserUnionDisable.dc.html | `13f5bc22b7d617b2f1b322c64553cb7b7b6055007aa0130768691d47fee94f90` |
| 用户详情 | AdmUserFreeze.dc.html | `b9037fbe7bb9893bfadb5756e4d3184ef502a4c74c3db902d6781602371fcbbe` |
| 用户详情 | AdmUserUnfreeze.dc.html | `093f142185109ac323bac081321bba04fdda4a98fa174e03c3082ea10a788327` |
| 用户详情 | AdmUserRealnameFix.dc.html | `aa337d48e22be7ea0f37d30458c84868099f79ea7546824cbfbfb4f5235df0b5` |
| 用户详情 | AdmUserEdit.dc.html | `4fb9af006f38467ad099df1c97d4ba9b1d46f7a56746d05a6855e06bb19c9baa` |
| 用户详情 | AdmUserDataExport.dc.html | `a08b538fac720520288e6595ccfb71f0645d4325a481367e9be73f3126ee966c` |
| 订单查询 | AdmOrders.dc.html | `1c3ac708e1cb7bee6f46a5cc54d0fb6d24588c79f63c9fbf9a912cf891966c0f` |
| 订单查询 | AdmOrdersStates.dc.html | `73070371e3a0413e0b813cccb3b14b78dafb572ab1172b77ad06012f55d0aa5b` |
| 订单查询 | AdmAdaptOrdersWideTable.dc.html | `9905d20e0535e689a3c3581f0ec6781a8e8a51f28fa640fb992451ff68727bc9` |
| 订单查询 | AdmOrderSync.dc.html | `f9056167321eea3b767696d945b034d5601482c297d68ea054807e3906e79967` |
| 订单查询 | AdmOrderSyncRecords.dc.html | `8b00d0ca32cdc250966dbe812547cac1a354a4f55d7adbb8af8b6969ec47aa19` |
| 订单查询 | AdmRightsImport.dc.html | `f31ad8e7922d445c860212ed126b7bf7bb8d1cd44aead4f4ec5c2c6bb0066d9a` |
| 订单详情 | AdmOrderDetail.dc.html | `53283883bcc3b17f5d2210a93285bb36dec60838bca712501ba99c6676685245` |
| 订单详情 | AdmOrderActionStates.dc.html | `3632a14934398109572d9f47f9d477cd0a5542c48bbecbedff5c2ed65b146aee` |
| 订单详情 | AdmOrderSettleHold.dc.html | `243fce26daf1619355300744929697ddbd125ae2402b9bc8d91a1c0556d5aa51` |
| 订单详情 | AdmOrderSettleHoldDone.dc.html | `9e51e2ce7c63c297971ee847008502e7bac3c513c96a27557791d3f19975e207` |
| 订单详情 | AdmOrderSettleResume.dc.html | `8974196755fd68481b920b0d7c06b8cca1eec0d597952202b0c93b6cf1449a0e` |
| 订单详情 | AdmOrderAssignUnattributed.dc.html | `fa1ac7750b5557defc1bbf02698a8297b9680985a592437bb3548a453592dbe1` |
| 订单详情 | AdmOrderAssignUnattributedConfirm.dc.html | `802e589c64caacc58a3c9823ca794be96bc344724f7e7d9dddf2d201651b2fbb` |
| 订单详情 | AdmOrderAssignUnattributedConfirmReceived.dc.html | `60f77ba3186a5a0b892f5a4e3e63731ea544b4dbec5e327d6074424ec0a2548b` |
| 订单详情 | AdmOrderAssignUnattributedDone.dc.html | `ed47cdb2c6b80c1d97695b732c9165bcf2abd7cadd28f268e29f540e770e13a9` |
| 订单详情 | AdmAdaptOrderDetail1280.dc.html | `87dc95eb08015290a14272c8e2f2f2d9b80b82bb9cc64d35dba79512906b7202` |
| 找回审核 | AdmClaims.dc.html | `1c0db82aebe6972b3886afc5adbd72e9f6b8763b425b11c838d664da0b59817f` |
| 找回审核 | AdmClaimsStates.dc.html | `65e5cb76805900b18de866e17f88cce6ec828a3b844fdcdd466d3d228ad8248c` |
| 找回审核 | AdmClaimReview.dc.html | `6af101e473e5c8e080013851c8c73229b3a9fe01dc6c19e56fa6fdab78ebdec2` |

## 管理后台第 2 批定稿（2026-10-18）

负责人 2026-10-18 22:1x 定稿：「第 2 批定稿，全部按推荐」。第 2 批 = 管理后台财务页：提现审核与打款（列表、详情、驳回、补录、批量手动、自动到账判定与设置、打款队列、打款记录、余额录入）、月结账单与对账差错、人工调账与核销、余额流水与导出、资金看板。三条按推荐的决定（自动到账总开关只在紧急开关页改、需 `switch.all`；调账一步提交、待批列表只留系统预填单；打款延迟不另加主动通知、维持 BR-WDR-26）的落点见 [变更记录](../docs/changes/20261018-后台第2批定稿.md)。

- 规格：[admin-withdrawals.md](specs/admin-withdrawals.md)、[admin-withdrawal-detail.md](specs/admin-withdrawal-detail.md)、[admin-payouts.md](specs/admin-payouts.md)、[admin-settle-bills.md](specs/admin-settle-bills.md)、[admin-recon.md](specs/admin-recon.md)、[admin-adjustments.md](specs/admin-adjustments.md)、[admin-ledger.md](specs/admin-ledger.md)、[admin-fund-dashboard.md](specs/admin-fund-dashboard.md)。
- 画板存放：本机运行目录 `couli-runs/design-hifi/project/<文件名>.dc.html`，1 倍 PNG 在 `couli-runs/design-hifi/review-admin/png/`，总览 `review-admin/overview-2a-finance.png`、`overview-2b-finance.png`；Codex 对抗审查记录在 `review-admin/review-log.md`。画板与 PNG **不入本公开仓库**，版本以下表 sha256 为准。用户详情【调整余额】抽屉 AdmUserBalanceAdjust.dc.html 已在第 1 批登记，本批只引用。
- 入库前核对（2026-10-18，逐张，共 45 张）：样例数据不含真实手机号、证件号与真实个人信息（手机号、收款账号、卡号、姓名只以脱敏样式出现，微信收款标识不显示）；自动到账阈值、水位比例与时效、核销阈值、支付宝 / 微信响应码与状态值为样例或占位（规格里已标）；平台只以文字标识来源，无平台商标图形。
- 画板与规划不一致、实现以规划为准的项（提现状态名与差错单类型名按 BR-TEXT-25、调账单「待批」应为「待批准」且人工发起的【保存待批】【撤回】不实现、部分按钮档位应为动态码、受阻原因筛选与一键组批未画、结算明细上传页本期不做）已逐条写在各规格第 7 节；画板改名另立一轮。

| 页面 | 画板文件 | sha256 |
| --- | --- | --- |
| 提现审核 | AdmWithdrawList.dc.html | `2ac7d0122ace42bec28296bd67bac3d0bb50629bd2192ea503ec3a21de164dbd` |
| 提现审核 | AdmWithdrawListFilterDraft.dc.html | `cfb0cfabf00f110fe969967782a25fbe829469a55dea542276d636e46d5cba59` |
| 提现审核 | AdmWithdrawListFilterApplied.dc.html | `21ba428a5b45bdeb5ec8446808089d7aae7d68ffe5e725220c2c46ad35cfdda0` |
| 提现审核 | AdmWithdrawBatchApprove.dc.html | `f9a4adb6ad1ffabeb6045ca87770e380f79cb824dac92e36b6580390f39b886e` |
| 提现审核 | AdmWithdrawManualBatch.dc.html | `126414a8fdf8c0f026cb9798339b2951143449341416ea91d20f733e6bcea51f` |
| 提现审核 | AdmWithdrawAutoSettings.dc.html | `de60f79a4925280c61ec6ebabede970b10f9d0ad55f52f450ac3c0e5b217c680` |
| 提现审核 | AdmAdaptWithdrawList1280.dc.html | `244e9dbabce1e6f9d788014ee1fb690f41d8f8fbab5187ec118a3f4591642030` |
| 提现审核 | AdmAdaptWithdrawList720.dc.html | `33388a9511fa2e2f078ce95c318a5bb290a0cd877f9d1ce1be465bf8b982a828` |
| 提现单详情 | AdmWithdrawDetail.dc.html | `4e55d52a231d2fe9b2fd887510f58e474fe9d5a8f11182ec9b2914458886a7c0` |
| 提现单详情 | AdmWithdrawReject.dc.html | `ef320b8d193ead2b82f4f3da58503b26da2aa89f1f91e3da3d2c03e4510f308f` |
| 提现单详情 | AdmWithdrawAutoDecision.dc.html | `6053736c459a1a9bc463d3d192ed742122b0b3a782f86f6e7ff215c4956a3357` |
| 提现单详情 | AdmWithdrawManualEntry.dc.html | `5e6a9684fec96793081bca8b2409a5441f02d46a4e46245b92263d8f4d1edce8` |
| 提现单详情 | AdmWithdrawDetailWechat.dc.html | `7b7f39d6bb4f73b7e28791edcd9a766ab349b72a9102f55c3f234835a3feed79` |
| 打款队列与记录 | AdmPayoutQueue.dc.html | `831870049e6eea13818ff8de48cbeccbfac82a4cf14515d58ffef44f3b4577f1` |
| 打款队列与记录 | AdmPayoutQueuePaused.dc.html | `c75be89783f7593d3eb33818d480f3b0ba3137753105e5a7465ffdcd3b210a0c` |
| 打款队列与记录 | AdmPayoutExecuteConfirm.dc.html | `a990b72f488667c5202d0de7a0f7b4838c3a3c4db6d765482fc88a2e4b182d6b` |
| 打款队列与记录 | AdmPayoutExecuteDone.dc.html | `e110d8dea503f5c772ab30bfed1df55ef5af29e78667509f1f9b9e60f3c24820` |
| 打款队列与记录 | AdmPayoutUnknown.dc.html | `df557e7d41f6e4356a36a9fdca4337df84aab9659a008f7e8204b5068aa24ecc` |
| 打款队列与记录 | AdmPayoutAttempts.dc.html | `0ee0eadd1f3f8eeae1167ce71a6d4094898e38173fa74f0aca223f936a3728cf` |
| 打款队列与记录 | AdmPayoutBalanceEntry.dc.html | `402d13ce3293b964a1399cbf24983576bae1f0ca74675a5f8d3a8cfa3d0fcc6e` |
| 打款队列与记录 | AdmPayoutBalanceEntryInvalid.dc.html | `7663d65ef3575acd36b21d96d5e0c0f739d949fa23d312fe8f99b5b550c8421e` |
| 月结账单 | AdmSettleBills.dc.html | `790b1a57eab4e282eb33f4712b154c32c613c89c51a829226325134099a214a5` |
| 月结账单 | AdmSettleBillDetail.dc.html | `d412d70cbc763824d3249755e85b542b6143c096e34cab806449e2f833954fe3` |
| 月结账单 | AdmSettleBillConfirm.dc.html | `e6cdc11cf92560146e690d6e6d928c3e0a6955a803a51b629e2c6433f6eedb0a` |
| 月结账单 | AdmSettleBillRunning.dc.html | `004bf542cad98240865965a25608f3547ca91c508ead7562f7061e335426e14c` |
| 月结账单 | AdmSettleSupplementLaunch.dc.html | `114405a5fa50e03159e353076bf954b991ea66aba4112fb793baea2383ea0999` |
| 月结账单 | AdmSettleSupplementCreated.dc.html | `a59522351031edab635b69948f6164fe111ffc001832b7f58b3b1d8404d99fb8` |
| 月结账单 | AdmSettleSupplementEmpty.dc.html | `a4cb3eda1808f9800ba929e779a6bf3bcd951b89a23eb87080d78b7f3be5ac8a` |
| 月结账单 | AdmSettleStatementUpload.dc.html | `afbb1e226bbd88c5d6095e0b80b306611dbdd75c7dab343bd14d35b0299bd22f` |
| 月结账单 | AdmSettleStatementUploadReady.dc.html | `862b8a4ed35d6f121b8ef96998066508c66ad678eab40366025b56520f0c5545` |
| 月结账单 | AdmSettleStatementUploaded.dc.html | `09d7d44e27b471ece8d163122fd430ece0fc8100b30cad9f4c2549efbf951648` |
| 对账与差错 | AdmRecon.dc.html | `894f7d854fa01a6c5879d68c3cd820f6862db36f25459026331f184abe845328` |
| 对账与差错 | AdmReconDiffsList.dc.html | `4ddb589b0b6a6f8633472a9eea94f200304e009ee4a502f2a80b17089408af51` |
| 对账与差错 | AdmReconDiffs.dc.html | `70b1104410e4d79b458a16f219229e5bc1cb91048930e60f0582a44e0950cca2` |
| 调账与核销 | AdmAdjust.dc.html | `0fb0f5ab98e3cbc6cf17cf382ff8b2ec98dcce2664ee86e84a9104535a329e0a` |
| 调账与核销 | AdmAdjustApprove.dc.html | `52583862069d47ff26f84a42720f19b1242cd9b9b2acb89c969a42aacfac333f` |
| 调账与核销 | AdmAdjustReverse.dc.html | `5593542cdec1bf7826e09b55045311698ab05af70fa63642c88b1f187460de9a` |
| 调账与核销 | AdmAdjustReversed.dc.html | `cfcb7c1cdff57ce80ea92ceeb163eef3934f6cf8ea3ee718ce1e9160f5b2f04f` |
| 调账与核销 | AdmWriteoff.dc.html | `75bc4f7b03d5ee908d501166845ede57e2769f4f0180667a292a89b1f9f3fa23` |
| 调账与核销 | AdmWriteoffBlocked.dc.html | `5df5525e44c5c105df2968e9ba04c59fcf462a2d00d78ffb1cfbfcf8a709af9a` |
| 调账与核销 | AdmWriteoffDone.dc.html | `e4980fc58e348d6768b1143eb28c255a9271cbd08a3b3184a4c307025137f0f4` |
| 余额流水与导出 | AdmLedger.dc.html | `a569ebb9f83ddbc73c09486d01a0617c349a73816eee3b3d2642add196a6b4f3` |
| 余额流水与导出 | AdmExportTasks.dc.html | `089779a6f3b97f9b597574d731bd1bfa4382ea6d7557df6846a4d8b9073a7ad9` |
| 资金台账与看板 | AdmFundLedger.dc.html | `f60abba6f181d0597debc249e5b22aa682e2db1fe41c062b0600ddfc20321014` |
| 资金台账与看板 | AdmReportFunds.dc.html | `d7957c385f84bb40f7d7556d67994d00b69709bd5b709c3ece6358682bc1c4c9` |

## App 内高保真第 2 批定稿（2026-10-21）

负责人 2026-10-21 在对话中定稿：「全部定稿吧 先开发 后面在微调」（应用内高保真三批全部定稿，本节登记第 2 批）。第 2 批 = 钱：钱包与余额流水、收益看板、订单列表与详情、订单申诉、订单找回、提现申请与核实身份、提现记录、实名认证、收款账号、劳务协议签署、AI 助手的查订单与查收益，共 132 张画板（117 张浅色 + 15 张深色；93 张本批新写或另存 -v2，39 张原稿沿用）。登记与待回写清单见 [变更记录](../docs/changes/20261021-App内高保真第2批定稿.md)。

- 规格：[app-wallet.md](specs/app-wallet.md)、[app-ledger.md](specs/app-ledger.md)、[app-earnings.md](specs/app-earnings.md)、[app-order-list.md](specs/app-order-list.md)、[app-order-detail.md](specs/app-order-detail.md)、[app-appeal-order.md](specs/app-appeal-order.md)、[app-find-order.md](specs/app-find-order.md)、[app-withdraw.md](specs/app-withdraw.md)、[app-withdraw-reverify.md](specs/app-withdraw-reverify.md)、[app-withdraw-records.md](specs/app-withdraw-records.md)、[app-real-name.md](specs/app-real-name.md)、[app-payout-account.md](specs/app-payout-account.md)、[app-labor-agreement.md](specs/app-labor-agreement.md)、[app-agent-chat-orders.md](specs/app-agent-chat-orders.md)。深色稿列在对应规格第 1 节。
- 画板存放：本机运行目录 `couli-runs/design-hifi/project/<文件名>.dc.html`，1 倍 PNG 在 `couli-runs/design-hifi/review-money/v1/png/`，浏览页 `review-money/v1/money-boards.html`；Codex 对抗审查 3 轮（第 3 轮 PASS）记录在 `review-money/v1/codex-review-r*.md`。画板与 PNG **不入本公开仓库**，版本以下表 sha256 为准。
- 入库前核对（2026-10-21，逐张，共 132 张）：手机号只以脱敏样式出现（138****5678、139****0000），无 18 位证件号与银行卡号样式的真实号码（银行卡只有「6214 **** **** 1234」与「尾号 1234」）；12 位以上的数字串只有示例订单号与交易流水号；嵌入图片 98 处全部是 `icons/platform/` 淘宝、京东、拼多多原图的 96px 缩样（装饰，alt 为空），其余图形为自绘线性图标与商品示意图，凑狸自家品牌元素无平台商标或近似元素；支付宝、微信只写文字（官方图标未入库）。
- 画板与规划、契约对不上的地方（契约缺字段或错误码、08 缺字典键等）已逐条写在各规格第 7 节，标「待上游」，实现以规划与契约为准。

| 页面 | 画板文件 | sha256 |
| --- | --- | --- |
| 钱包 | Wallet.dc.html | `39420611de0a1c525e37bf49556640254dee380222c33e9583bf521def318d9b` |
| 钱包 | WalletHidden.dc.html | `ae2774deea9b391e077cbb343e8e728091b72d6975c41af9aff8353a014efbcb` |
| 钱包 | WalletFrozen.dc.html | `d683bb4b078e2525eb7a94f7df6faffce34e8b6f0dcb76be22ebde7f9d80cc4a` |
| 钱包 | WalletNegative-v2.dc.html | `ae0f3613fd5b153080d7ed39d240e00892d474142466d398e0bacf88949fd480` |
| 钱包 | WalletRiskFrozen-v2.dc.html | `92f868009ea9f17029326c746ac334311baf75e6dcce46dfb8a227b87ff4f73c` |
| 钱包 | WalletRiskFrozenTap.dc.html | `7d3b9c66dda3b41d05579b4a38e0047fe00403dae64e9aa1ad31134e4ace891c` |
| 钱包 | WalletStates.dc.html | `ca3762283157213eedab812de0bf4952ee55091c49ebd27c08ec784a3cbb6fac` |
| 钱包 | WalletEarningsEntry.dc.html | `1e89481e8ebe8627f5e76fef149b54f7949cfc0c03ab561bbffdd1ccf8f9f2cd` |
| 钱包 | WalletStale.dc.html | `57a01df4654bc4e8baa3a5c863bda2c751e0e7f246be7cf88174bfe221b03b55` |
| 钱包 | WalletNoteEstimate.dc.html | `306ddd4a1455ba4b21c15ed782bafee3abdd7dbfe6c62da84c2edd493cdd9433` |
| 钱包 | WalletNoteFrozen.dc.html | `d3cb96cbbb60588a02308b2f5db749de964ba35ca53e4086dd4464a118dd4e44` |
| 钱包 | WalletNotePaused.dc.html | `dbda4217e9ad70cc63dc9a1199753a11353f8c71bfffbb37331111d576b663ac` |
| 钱包 | WalletDark.dc.html | `f56890ac6f5ce95710d07b790cdba0edaf1efa6e53e53658d2bd632c6d29de2a` |
| 余额流水 | Ledger.dc.html | `baa5d8ab954a89257a671f8b74126f1d51c4b932778b129c24f2983043ec9c8c` |
| 余额流水 | LedgerInviteReward.dc.html | `ca59251e3f6916ac7234450949727b61a7cc201f659fe0eba362282e98f473ea` |
| 余额流水 | LedgerStates.dc.html | `a0e19a192d84820dd2cecdff77aac1f1f8e285059553e49b83bf867d8db8e11c` |
| 余额流水 | LedgerEmpty.dc.html | `1a58eb1390d805e237772c2b8f560dfee8279c57cc84e92b46b7b8beaec381be` |
| 余额流水 | LedgerDark.dc.html | `58b7b8c060beaf9f75456d2f087248382ab3bf5075d325249be8285fb963b02a` |
| 收益看板 | Earnings-v2.dc.html | `e9ba66bd9739575e102945191d0d37938cffff4181c0a93a6910778105811658` |
| 收益看板 | EarningsPlatform-v2.dc.html | `174279b9b2c76dc3f312932e071ed8bdb691cf4e5b7cde6768590675d7287ff0` |
| 收益看板 | EarningsEmpty-v2.dc.html | `b892253566909f483d33b37973f0c90709c1901bb1a4eb596641a9c7259d9d0b` |
| 收益看板 | EarningsMetricNote-v2.dc.html | `5485ffd51a49872fb5e79deb95b57cc1346e9d963b6cd269c41e1f065ab58645` |
| 收益看板 | EarningsDark.dc.html | `3d17b69efb5a0e829ae14b53df77a4d85a64b466939792adfc867cb54f365e77` |
| 订单列表 | Orders-v2.dc.html | `7f56b9f5ffe0692199e3169b5463f1c1a4f7dc5e89760bd070df6505309d6624` |
| 订单列表 | OrdersShare-v2.dc.html | `92b09141ab1d68348c6741895e9a0cccb2cf63ec61f7356d9787f8d15e0d12c8` |
| 订单列表 | OrdersEmpty.dc.html | `427293e05b21a96ac33443af0c805888f7bb1f5db221c281c326be23edb47a7e` |
| 订单列表 | OrdersShareEmpty.dc.html | `b3d648e2013f2dc0049fc7bd882a542ab504bc9ca35106eaa1f9e7c7a9e4834a` |
| 订单列表 | OrdersFilterMonth-v2.dc.html | `33fe2f489da09fbbda1412c92f817e196c89713a9c1e01152b8d43ab527d5eff` |
| 订单列表 | OrdersFilterPlatform-v2.dc.html | `2b34babe402c09db158ffe0071758328f88337a94f7b1e9f81252cdd64cff429` |
| 订单列表 | OrdersSearch-v2.dc.html | `b07ddb68814ff937fba219b258a2637ca03441155792c028bf26313998af7a79` |
| 订单列表 | OrdersSearchEmpty.dc.html | `ab5b424a11a143234a4dece363770c36d198d7df6760e722a5dd09e7ecf5c2f1` |
| 订单列表 | OrdersStale-v2.dc.html | `c7933dc74d6e91dbf725f8ea237d1e802030f8ab68b1ccf9a46645b13d09cd66` |
| 订单列表 | OrdersClaimPinned.dc.html | `9b1b9a1119717572c63a054da2976b95f137844286a4a39a0c493114c26d001c` |
| 订单列表 | OrdersHidden.dc.html | `b7b4ec5fecb52b1fef068d2e4ddf41704b2b2af11732844f4ea16876ec74d83c` |
| 订单列表 | OrdersDark.dc.html | `6be77e80f0ea5613ac2b65e2dee5e2524adaeabe1568d0cf69ab92d2fc460837` |
| 订单详情 | OrderDetailEstimated-v2.dc.html | `a15fa064d12ccc7f4ba99667d4191bc3009461e7445947c53910f10cc4dbcc74` |
| 订单详情 | OrderDetailSettled-v2.dc.html | `d2a89981fd3d911fbac5adb9b7bc57bf000fda8176fc384ef7b22b464c3ce55c` |
| 订单详情 | OrderDetailNoRebate-v2.dc.html | `5e5321b5e4415e474583808e95ba7a8a9dce6d20fd694c12232483a4699b7c06` |
| 订单详情 | OrderDetailPresale-v2.dc.html | `98880476cb0e235856b0a39e01f825b0d3a5607cbe38ddf73bbe4822040dbbb4` |
| 订单详情 | OrderDetailRightsPending-v2.dc.html | `8f5501159c79b7f958a6d4bcf1a49f25fc9c843d57cf37c2878a1cd1e08e37dc` |
| 订单详情 | OrderDetailReviewing-v2.dc.html | `4139226928a552fea4010e4726e8ec19cc7bf9e9252beb4b790ac8fa94c6058c` |
| 订单详情 | OrderDetailClawedBack-v2.dc.html | `35458ec45b74cdbe8df1889bda04fa3509617dbe544111d1ecedfea64fd56d02` |
| 订单详情 | OrderDetailPartClawed-v2.dc.html | `f430a33b1300c6e0c64a2d784f82cd735560e49cf1eee7a717adc571d5c0848f` |
| 订单详情 | OrderDetailShare-v2.dc.html | `456e329d2c90419637bcb98646bdf8fc5209bbb2542642b4307263964045c5bb` |
| 订单详情 | OrderDetailPriceCompareNoRebate-v2.dc.html | `b180e9a84a720ea8b0ffee8e6ead5480429c45011c603197450d37662b24d9a8` |
| 订单详情 | OrderDetailPriceCompareRisk-v2.dc.html | `d93c597bcd6aabd9a58d3461389c0194fe634aeb3100e97abefed279db036791` |
| 订单详情 | OrderDetailBlacklist-v2.dc.html | `b6adbd7d4fd9ae3924b4ec4d6d3e785eff63b15e64de1656fca0c2cbd0494560` |
| 订单详情 | OrderDetailAppealPending-v2.dc.html | `3cfe115e446fb4069fa448414959ceff2507f89a788d7a7ccea4cf09efcaf532` |
| 订单详情 | OrderDetailAppealRevoked-v2.dc.html | `bbc968b9f653c744cc28bbb348feb36ee97d8d2ac0858a603dd0ef20a91b19ce` |
| 订单详情 | OrderDetailAppealUpheld-v2.dc.html | `97333d4fd0d661457a85c7f523ee22b9db35051837171a07d405193a657c2364` |
| 订单详情 | OrderDetailAppealUpheldFinal.dc.html | `0ce8facfc114cd45c9dfbb3082f64588e4752b352ccac2c2d0d724cbcf8ab903` |
| 订单详情 | OrderDetailUnknown.dc.html | `1ff2ff17b09d7b30a60d40d40a54df9a091ad0ae5a06b54239a42c68b8858dc6` |
| 订单详情 | OrderDetailReasonStates.dc.html | `f84ac6bc70bb87264e1d665b3ff0aa7526ffd782bf7e0db92d8ac4020ad4d482` |
| 订单详情 | OrderDetailDark.dc.html | `ad0a35f6342036541efcacbaec45702831190a3a9f3bf9a6694e567ef4c1a435` |
| 订单申诉 | AppealOrder.dc.html | `7cca26488329fe9f19c95c78597136db53e170deea3452ea27934c54cf9de356` |
| 订单申诉 | AppealProgressOrder-v2.dc.html | `a3f271827ce7c052f770c68ac452b12cf1adadda25fa741df4c8f6fa1c10fe5d` |
| 订单找回 | FindOrder-v2.dc.html | `e7e3559e3f058ab4468d775e049fc4cb25152f3c2d0f4a97c0233d8a35c96e45` |
| 订单找回 | FindOrderNotFound-v2.dc.html | `1b64c39c89940505e4972fd5508893274682545fd6446da62644e1ed0785626d` |
| 订单找回 | FindOrderRecords-v2.dc.html | `44cbb7bf2cb2cb526f3b7ea63639719e361171094a2018b1fbc6e13c70e6f59c` |
| 订单找回 | FindOrderRecordsEmpty.dc.html | `e62f4bacad8a258396e489adddd1d33702784fbba19c79c39088982ea384c9b0` |
| 订单找回 | FindOrderErrors.dc.html | `926a3ea2ec59fc3b2cf9d435636da26bbac6d7989b5dedac7a706aae5dd23730` |
| 订单找回 | FindOrderDark.dc.html | `782182a3b4bfc04bd694eb301d82212b6b949a7145fd7cfab2fe8b90a1f31dbb` |
| 订单找回 | FindOrderRecordsDark.dc.html | `3dcf8b722120dc8aad00f2a0e6fad91ea1d5b2ffe135a111a2adc16ff1f64f40` |
| 提现申请 | Withdraw.dc.html | `a3ec02370d99078fc615b59dda40e15ee26ab6f6c9fd892e8161e8e655defe89` |
| 提现申请 | WithdrawCalculating.dc.html | `e9a88c0e068badfdb857f851c2936d140bc1da3aac9ed4e3ef813a8663571abe` |
| 提现申请 | WithdrawEstimateFailed.dc.html | `140ef89d5f643028394cdeb61d8b41af92522556850a8036c356223963186428` |
| 提现申请 | WithdrawNoteNet.dc.html | `11c0b7aa32025667b0efcd80fd80657a53a868e782c411fc08e8e53cb1a27124` |
| 提现申请 | WithdrawRealName.dc.html | `9d9752406b6da17b172dfe0862bb7e586f286ab8c3a691160e835b96f067c953` |
| 提现申请 | WithdrawStepUp-v2.dc.html | `a4c1a513c31311bf36e5dbed7f6e1ec5f5d53a2fc079b9da1f3a947b277d94ff` |
| 提现申请 | WithdrawSubmitting.dc.html | `9530119ea5112172fe7c01ad247be72f21e0a456a80cc160735e82a495f89a6b` |
| 提现申请 | WithdrawBlocked.dc.html | `fbb6c6026350d149b2e1dec4cc14e6d4946ed78f690641f1cef3735b9847c992` |
| 提现申请 | WithdrawWechat.dc.html | `1efb6202ac5604cf81459e2b477956dc250323e6c77836abd545039d0ff7aab3` |
| 提现申请 | WithdrawPendingConfirm.dc.html | `763bac6c8891262d5a02cf22470fc281ffea5b6907a9a8bbc2e4cbd862d9e2e4` |
| 提现申请 | WithdrawPendingBusy.dc.html | `66b7777490f2263a4b55c257f108d912049a51bf15037a718ad2fb08c04df784` |
| 提现申请 | WithdrawPendingStill.dc.html | `dd30ef7943f0b951739fa425a97aa4ea0100ac24e848e195883601e09a4b49f3` |
| 提现申请 | WithdrawAbandonConfirm.dc.html | `bde016ab1cd2776a765f054cec5daa4ab944df3be483cbfb1a426a6ed7c6c9e5` |
| 提现申请 | WithdrawAbandoned.dc.html | `920130f93ef913cdb3c7bdc0601e7ace3308e8a54921041a1b95260936e93a1a` |
| 提现申请 | WithdrawAbandonCompleted-v2.dc.html | `0de2354c778f5dfda7e49160ef03207e3b66a8f64afa0b3a02a260c85a996a1d` |
| 提现申请 | WithdrawPageStates.dc.html | `c0ae73615beb08f0063ee702fde0b5a5b53929cd5f0801063f65c4815263f82f` |
| 提现申请 | WithdrawDark.dc.html | `63b4a1de0690940de3fd921f4cc0d5262697f40d698fa23cbd069faec31e73db` |
| 提现申请 | WithdrawStepUpDark.dc.html | `adc11c54ead61d2580590d8da5a4e3839e1a53dc0f290bff8942e2c8b024367d` |
| 核实身份（旧号加验） | WithdrawReverifyId.dc.html | `56a3ce56c3213d1a5115412e4d618bd7b6489cb25d6fa9e91cfab2fd40a1c232` |
| 核实身份（旧号加验） | WithdrawReverifyOauth.dc.html | `550ce0c4aef1a69fc3d6c0dce591c4d18677e81c47f939a24adf09cccd40e810` |
| 核实身份（旧号加验） | WithdrawReverifyManual.dc.html | `6b7bee12389d8a18fac0b915ddf7cbdbd9a611c9808a17dff2980a8b5f544262` |
| 提现记录 | WithdrawRecords-v2.dc.html | `cf01250a92030211d9b421f9829931c04609d3a515e7065b6ffc87041c58869d` |
| 提现记录 | WithdrawRecordsPending-v2.dc.html | `54c438899928c46935d2d6725c704171131a350d1f04c47923cc4b286b0adcc5` |
| 提现记录 | WithdrawRecordsPaid-v2.dc.html | `c0b9ef897858435c99dbf4fd11fab0b6c89efdfff4943ae22773e64551df3079` |
| 提现记录 | WithdrawRecordsFailed-v2.dc.html | `54118c4372a1e0cef9cf79fb50d2b908a64b56a83214e33a4cc288a5e2e89350` |
| 提现记录 | WithdrawRecordsAutoDeciding-v2.dc.html | `bd02a3bebdfadfdc1811d983b37788bb163bc49ed72a63c291786edca0e042c3` |
| 提现记录 | WithdrawRecordsAutoWaiting-v2.dc.html | `e6fdc88d7fa1c05227109b829a80a6109f6ab3027bd9463dbf1ad82f064275d0` |
| 提现记录 | WithdrawRecordsPaying-v2.dc.html | `358b5b21a0b5e1792858bc8b7b4c895d1d0916082f96a5ecbb789181cc1d8465` |
| 提现记录 | WithdrawRecordsDelayed-v2.dc.html | `66778438689342f8a4c203ba6a2e442cfb6ab46840428beb572f0f64c08a4557` |
| 提现记录 | WithdrawRecordsReviewOverdue-v2.dc.html | `7f5a7afbd5fa8879e3ec26ebdcdc51970896fd93a9c3761be3b339d6bc012b6e` |
| 提现记录 | WithdrawRecordsEmpty.dc.html | `466c0c5432b79b04059c88fa3faa61a6c41b58e243844a7d51d73af11a6c93ce` |
| 提现记录 | WithdrawRecordsWechatConfirm-v2.dc.html | `5ce143522bb8d0c80a78dab173f5f9e0d912d4594fd4589db965e422c00eca3e` |
| 提现记录 | WithdrawRecordsWechatTimeout-v2.dc.html | `1370a40a1c78745b1b99828e79e06d1175d0c7953ced150c990f45235c7f2fc0` |
| 提现记录 | WithdrawRecordsStates-v2.dc.html | `772af712d7174cde0e69c48b3ea64713cc501abf4e5d91835c1db40a32574f62` |
| 提现记录 | WithdrawRecordsMore.dc.html | `d4c9e8f21e9762a36d52a9730cd06475ef2fff6f0625608bee5daafc1c704de5` |
| 提现记录 | WithdrawRecordsDark.dc.html | `df8977f3cae20798fdf3cc63623a58b0e5e0a67c8e129b214bd03ffc333e051b` |
| 实名认证 | RealName.dc.html | `f3849dc0623d451af79e9689a2f97a07e1a223fb0765749f19f36a0beffa4dbb` |
| 实名认证 | RealNameConsent-v2.dc.html | `532e3deab4476eba8fe05e54e452ec0c9cad633a04e0cc9d14402d20936df0b0` |
| 实名认证 | RealNameErrors.dc.html | `60a7b9e9af2a661a3673e0540649af44d5a516c072c988e11a5ac3638ca3e136` |
| 实名认证 | RealNameDark.dc.html | `678c745cf10c5bc977eed9e03296a1cf81bec9ce2f75253dbb18fce46205c99d` |
| 收款账号 | PayoutAccount.dc.html | `7fc83faf1ae65a7a929290f374b98a034e39c04aee82d60b5012294f0d4c1cb7` |
| 收款账号 | PayoutAccountBank-v2.dc.html | `9506fc56ee0d49bb0481e728ae67d123788dcc6ee6d4ceb19670ba2e31a01003` |
| 收款账号 | PayoutAccountBound.dc.html | `41867ffd379d700ae13189a71eaa77e6c0474db5c208304ea5ac2b5098e86d36` |
| 收款账号 | PayoutAccountBoundBank.dc.html | `e7a6b2cac56a0ca04ce08f1edfd6f37552c42cc96560da1b35ff0fcb4f95de21` |
| 收款账号 | PayoutAccountBlocked.dc.html | `39392aaf7eeab9eaf162f16b875edd01cb058ad804b3beae1e3085ac08a8f92a` |
| 收款账号 | PayoutAccountPendingConfirm.dc.html | `0344664380d10f1fbacfa56c9e0724359c550632556da37820c2258ef5b564c7` |
| 收款账号 | PayoutAccountPendingAbandonConfirm.dc.html | `8068ad5c7642cf04be57c38997f01368442f2be0454d9dc273a97d0d7a36726e` |
| 收款账号 | PayoutAccountPendingBusy.dc.html | `a0ffffe9b2898aa613cce9abbe87cb36cde8ae1c4dc45f079bdb489b44fa10e9` |
| 收款账号 | PayoutAccountPendingCompleted.dc.html | `14a515de90368cca81b2e758a56b7408ed34684c5aa73c307cd82b1f335accf0` |
| 收款账号 | PayoutAccountPendingAbandoned.dc.html | `780035f86c64ad141979ad6be43eb092f20903d97f98721f6e3fa59c66652af8` |
| 收款账号 | PayoutAccountPendingStill.dc.html | `8fef2ccfad07eb133be7b516bc87ee201a8e8a5fd668990c688722d8b5587783` |
| 收款账号 | PayoutAccountWechatBound.dc.html | `59579a90afc640dba37629cc947a6ca7d4a16f20a871a6d10715593a3720ec3e` |
| 收款账号 | PayoutAccountWechat-v2.dc.html | `7632e45b64ca81af013a3711254418e0527fc821368bb67c0a6f8ad37c79009c` |
| 收款账号 | PayoutAccountWechatAuthorizing-v2.dc.html | `f62b0c0aeb54979c3fa36243371e55403db2d658a6f5ca7dde2ece5f5d978587` |
| 收款账号 | PayoutAccountWechatAuthFailed-v2.dc.html | `6e9cb55a018b8d8166f71a0c160e8a4fef39e0af9e1fa91c2e0f6d77ea82b285` |
| 收款账号 | PayoutAccountErrors.dc.html | `589ccce611a36f07e9f777e5544e61f38e1bd43801515d9ffc5744447a6e9c76` |
| 收款账号 | PayoutAccountBoundDark.dc.html | `0ab4dcdb26717152673f1396b331783f3f43a8aa13872575d55a63aa0e2003c0` |
| 劳务协议签署 | LaborAgreement-v2.dc.html | `50ac2210482c36b4de520248a8d15c07891c5613eafbcbfbf95c6c884f1af220` |
| 劳务协议签署 | LaborAgreementResign.dc.html | `c9170c3e9c59ef7b8adf4ac0bef55b12cc4eee6f27b5d019ecdb20d8eb40f4b7` |
| 劳务协议签署 | LaborAgreementDark.dc.html | `8b8f12b44a56e7847a0f386380c800099b9478b8f6c897fe1ff4e2dd649a095f` |
| AI 助手（查订单与收益） | AgentOrderAnswer-v2.dc.html | `9ded17321bfb99e01c7d0a6473fc0ad7f1285961d798492a9717e6adac0eabaf` |
| AI 助手（查订单与收益） | AgentOrderNeedLogin.dc.html | `fa0f2c4a8d96d650796a399e4352d7790883b81b1dd8ddeb85932e93cb48ca68` |
| AI 助手（查订单与收益） | AgentOrderNeedPhone.dc.html | `c821e4bbea7a9f5d6958efd38e83f4131a3e0d8b3856c624abb56070edb506c5` |
| AI 助手（查订单与收益） | AgentOrderNotFound.dc.html | `9f9df0dc89e9977e87dc2b11f39bf380cbeca2959b1cde66a17e05d4fabab729` |
| AI 助手（查订单与收益） | AgentOrderEmpty.dc.html | `66a26bead3e4484ce853278f53c139fbeca53cb02994372638db57920282fbe0` |
| AI 助手（查订单与收益） | AgentEarningsCard.dc.html | `3e83207f3de9bb917e2272c3ae411a2adccc875ad28224b63e28abbfa46b3d66` |
| AI 助手（查订单与收益） | AgentEarningsHistory.dc.html | `4932706c6e6e579e9ca9770d870b65300a2673b92c5b0f78dbc25b2c6d16f11b` |
| AI 助手（查订单与收益） | AgentOrderAnswerDark.dc.html | `34438e4dc69469b61af056136814db2a50b61ea60605165cfe360b1937603561` |
| AI 助手（查订单与收益） | AgentEarningsCardDark.dc.html | `ddfa7ca2462bb299c221703528fc94cc9e2c88a17528e2e94c865e8a2c6c3854` |

## App 内高保真第 3 批定稿（2026-10-21）

负责人 2026-10-21 在对话中定稿：「全部定稿吧 先开发 后面在微调」（应用内高保真三批全部定稿）。第 3 批 =「我的」与其他：我的、邀请好友与填写邀请码、收藏夹、消息中心与公告、通知设置、设置与修改昵称、授权管理、绑定 / 更换手机号、账号注销、账号状态与申诉、启动隐私弹窗、隐私中心、协议、关于、帮助中心与返利规则、联系客服、基本模式、版本更新、可信容器与第三方页容器、AI 页面引导卡。登记、入库前核对与待回写清单见 [变更记录](../docs/changes/20261021-App内高保真第3批定稿.md)。

- 规格（26 份，按页面）：[app-me.md](specs/app-me.md)、[app-invite-share.md](specs/app-invite-share.md)、[app-invite-backfill.md](specs/app-invite-backfill.md)、[app-favorites.md](specs/app-favorites.md)、[app-messages.md](specs/app-messages.md)、[app-notice.md](specs/app-notice.md)、[app-notify-settings.md](specs/app-notify-settings.md)、[app-settings.md](specs/app-settings.md)、[app-auth-manage.md](specs/app-auth-manage.md)、[app-bind-phone.md](specs/app-bind-phone.md)、[app-phone-change.md](specs/app-phone-change.md)、[app-delete-account.md](specs/app-delete-account.md)、[app-risk-notice.md](specs/app-risk-notice.md)、[app-appeal.md](specs/app-appeal.md)、[app-launch.md](specs/app-launch.md)、[app-privacy-center.md](specs/app-privacy-center.md)、[app-agreement.md](specs/app-agreement.md)、[app-about.md](specs/app-about.md)、[app-help.md](specs/app-help.md)、[app-rules.md](specs/app-rules.md)、[app-contact-cs.md](specs/app-contact-cs.md)、[app-basic-mode.md](specs/app-basic-mode.md)、[app-force-update.md](specs/app-force-update.md)、[app-web-page.md](specs/app-web-page.md)、[app-external-page.md](specs/app-external-page.md)、[app-agent-chat-page-guide.md](specs/app-agent-chat-page-guide.md)。
- 画板存放：本机运行目录 `couli-runs/design-hifi/project/<文件名>.dc.html`，1 倍 PNG 在 `couli-runs/design-hifi/review-me/v1/png/`，浏览页 `review-me/v1/me-boards.html`，逐张改动与依据见 `review-me/v1/README.md`；Codex 对抗审查 2 轮（r2 PASS）记录在 `review-me/v1/codex-review-r*.md`。画板与 PNG **不入本公开仓库**，版本以下表 sha256 为准。
- 入库前核对（2026-10-21，逐张，共 168 张）：无 11 位手机号、18 位证件号与银行卡号样式的真实号码（手机号只以 138****5678 等脱敏样式出现；帮助文章示意图里的 19 位数字是 `sample-data.md` 登记的淘宝订单号样例）；嵌入图片只有 4 种——`icons/platform/` 的淘宝、京东、拼多多官方图标缩样（只用在来源标签与授权行）和 `app-icon/icon-1024.png` 缩样（关于、强更、邀请页与海报），凑狸自家素材不含平台商标或近似元素；没有外链图片。
- 作废不实现（文件留在运行目录，不登记）：`InviteBackfillDone`、`InviteBackfillBound`、`InviteBackfillExpired`、`InviteBackfillHasOrders`、`CsHandoff`、`CsVerify*`、`MessagesCsVerify`。
- 底稿首页同步（第 1 批 v1.1 对抗评审 V1-14）：`MainUpdatePrompt-v2`、`MainUpdatePromptDark` 背后的首页以第 1 批 `Main-v3` 为准，`BasicMode-v2` 的游客首页底稿以 `HomeGuest-v3` 为准；规格已注明，画板下次改稿时同步，sha256 照原样登记。
- `StateLoadFailed`、`StateNetworkError` 是通用加载失败 / 断网态，登记在「通用状态」，各页规格第 1 节引用。

| 页面 | 画板文件 | sha256 |
| --- | --- | --- |
| 我的 | Me.dc.html | `63524bac6c77965b80d4f027515f42055f246773376d647530cd06cab80f94a4` |
| 我的 | MeEarningsEntry.dc.html | `8ebac9f53fe2d2ee59c4f62974328924ef80aba125d7d4572ef6f4870b1d6d94` |
| 我的 | MeGuest.dc.html | `5d2e6b070643130eec182854d53642d9427ffe367edb4e42d4e77f5e5a4d0a3f` |
| 我的 | MeHidden.dc.html | `689a0823ec0083c74c0ee204fda5ba64f102fa826373e6b22b365744db290f82` |
| 我的 | MeInviteBackfill-v2.dc.html | `b3f9a0369ed8359c381ad5273beb3bba19a5f02ec48709f0344c36049522fd89` |
| 我的 | MeInviteBound.dc.html | `d87097d0aaa96a8321bf3a7fd492d50094ba8e7e9dd39afc4bead28989ef2a76` |
| 我的 | MeMinor.dc.html | `2f8c3f44b8b64f39030c1d31177c79e4d53a2d16d84c6caf3e2caed2484f2dd9` |
| 我的 | MeStates.dc.html | `9d15fd5093b81930239f32c1a4cd247124f9e3e5c1cdebcda49b10e35306d4a2` |
| 我的 | MeDark.dc.html | `77cd55030482a394a670cb71b51844a43f6d4a1135a8c2a1e34e60c59c9f6659` |
| 邀请好友 | InviteShare-v2.dc.html | `8bcd1fbfb42f168e4a72e08ebe33daef5acb46661e179980c7e44493ca3d4ae3` |
| 邀请好友 | InviteShareReward.dc.html | `859b68194f91302fdcbdf1f1c9550490cc28977db944bf75c9bdb9fd490f82b9` |
| 邀请好友 | InviteShareUnavailable-v2.dc.html | `388fc83a1a313dd07dda2e752b381e44ec92005c6fc01ca4018f3b087711227f` |
| 邀请好友 | PosterInvite-v2.dc.html | `887f00a3eefb5f15f996a448d873071acadda9976765bf3f4ab33fac308bd759` |
| 邀请好友 | InviteShareDark.dc.html | `8648a72219aa3df0b7849d1db22375efb816dcc42e760ff65f2ca34b88701b68` |
| 填写邀请码 | InviteBackfill-v2.dc.html | `4974164c60d13cb2a2ca63906a906b0549c5ff84d7a61ae048b652e5ca9c0394` |
| 填写邀请码 | InviteBackfillError-v2.dc.html | `fb0d4d4362180824c0d16e0d8786a5cb6034d12e68d4d3ad56bb8cb42ada73b7` |
| 填写邀请码 | InviteBackfillErrorStates.dc.html | `16b7a693347c4b236575fd6af6bf858faea5f993bc383761f9274757978f029b` |
| 填写邀请码 | InviteBackfillDark.dc.html | `3f320d44244976443ab2b2d7be6c0834a501f41cdd7d7486c049d4f88114c218` |
| 收藏夹 | Favorites-v2.dc.html | `b45d3fa5a8df53fff192001afb1ae68c105bea84c537e8f09fd653308a942c84` |
| 收藏夹 | FavoritesEmpty-v2.dc.html | `c623d5a9f2abca78677219bb8892708881d56cc3ce0a1f9524b14be77302f7be` |
| 收藏夹 | FavoritesManage-v2.dc.html | `e6d7c799bd764dcbd39a1424bed021dbe4f595dc7de269cd17355873d54b219b` |
| 收藏夹 | FavoritesPickShare.dc.html | `ecf1c8d7d03e784a09b8233730f982e013cfadebefa8742b66a0c62b74a1b632` |
| 收藏夹 | FavoritesDark.dc.html | `2e22407b8b3de28d2c16cf9ea8ab70e4c31cd8d88d76ff2556fc039a7dbca2ba` |
| 消息中心 | Messages-v2.dc.html | `bb6b6607c6fc6c54f2ca18a38352016b3b88da3a9f454d85ef79f913c892d9ad` |
| 消息中心 | MessagesEmpty.dc.html | `94d15c9ab971d9e770da5dfda026e0c33aa6e48f66a113e07f546a182c4a8573` |
| 消息中心 | MessagesDeletion-v2.dc.html | `93ba88f2b3b49c0254366455010f9e9804e58808797baf88629a6f25eeecf650` |
| 消息中心 | MessagesDeletionNegative.dc.html | `af24fdc4dd84417877b4bef956c7a262f3d8a6b61a19e4b30a4a0110c44a49f4` |
| 消息中心 | MessagesOrderAppeal-v2.dc.html | `086f4e43a14708aa56480dfcd09d89be3a0028aa0656663531890614c90399a0` |
| 消息中心 | MessagesRiskFrozen-v2.dc.html | `857c88b5655fd172341b94eec59b77bbd08808f2f6b4d554f3cf4c4085bb7033` |
| 消息中心 | MessagesUnbanned-v2.dc.html | `c22ee9eb6ca59dcacde53ca573605c59c05b67903f5ad5aeb8fbb4029a659782` |
| 消息中心 | MessagesCatalog.dc.html | `4c923c97f4e28495a83d5d601831065af16204fc55bf078b185a93ab04a5886b` |
| 消息中心 | MessagesDark.dc.html | `a20422604b8127fd8f6ec85d74126dc49531317223519ebc83561ce1a90662ed` |
| 公告 | Notice-v2.dc.html | `0f412404d73e8465dc2c01bd2b1702f5866423f3b0b31005442a41b98ad07401` |
| 公告 | NoticeDetail-v2.dc.html | `b71bf593f92d311c5134d7054b152989a9b9f2c8ae2dc2d89f47465eb5e8d085` |
| 公告 | NoticeDark.dc.html | `7af3d53ff1e26f5294ac8955a4ed5bcaab52a760f090bc0b804ccd629d6f728e` |
| 通知设置 | NotifySettings.dc.html | `078b68c7a982da44d52773c1d2ac580c28666296717b7afcd856edf0d3927951` |
| 通知设置 | NotifySettingsOn.dc.html | `8fac5337de42c1b18b784c090fdf60095adc6027dd043a773bdcbe8da49fd55b` |
| 通知设置 | NotifySettingsNotAsked.dc.html | `03b8c6b8eea16af6372b8b34c3319c6b9354c31e1db20b666eabd5742db878d9` |
| 通知设置 | NotifySettingsDark.dc.html | `0a70a74ac8f1b97cc86f682b63c214dc00bc2b96d37d08a8a35a0e837f48386c` |
| 设置 | Settings-v2.dc.html | `d076d94490d7eb7d11f0db2c1fb9c49c1b4a42a7719417f1e3450076af1b7f79` |
| 设置 | SettingsGuest-v2.dc.html | `7663f3b8db53d7afb68b1a86eef06b36f3ee5cba47898b2584c0833fd12b6816` |
| 设置 | SettingsBasic.dc.html | `dca586aae4d5ab3dce28a4211547be77dd7076aa3fdaca95a183fe3208c4b30c` |
| 设置 | SettingsClipboardConsent.dc.html | `668e9c73da58a50878913f6ad7c83652e69fabb64e244dbaa38c783f2dc99ae3` |
| 设置 | SettingsAgreementSheet-v2.dc.html | `7a2f9deca0568cded6f1f79bf6bd594953ba5904791846016e87dcd3239f389e` |
| 设置 | SettingsClearCache-v2.dc.html | `2aff1c58b7b3ac79afe2444d897da557a867b5b6103d90cca438edf6c214baf6` |
| 设置 | SettingsCacheCleared-v2.dc.html | `b8697ade455532645bcf5f57741d7d93c16bd88f9b29b3f6a0e29bf89e9d6053` |
| 设置 | SettingsLogoutConfirm-v2.dc.html | `fbdb33920e199db8928b68bd584a1a74c5bc196bb5a77844bf298790f2e5f278` |
| 设置 | SettingsDeletionWithdrawn-v2.dc.html | `e1997e11d790ba17d0f84c32a0769647ddc7b81e9833627d0aab5610aa435236` |
| 设置 | SettingsNickname.dc.html | `18c611dc0ba74e98360292cdcb364f21147736c16a76545f70dfd2a571150e99` |
| 设置 | SettingsNicknameSaved-v2.dc.html | `0703e0b867ee310a895e4475c8263f923d1104eca469acdcbe117a56c8a006a7` |
| 设置 | SettingsNicknameLimit.dc.html | `75c51720903e5cc4e73c9905896530042388d9f27ceb2c322b53d7af217343c4` |
| 设置 | SettingsNicknameSensitive.dc.html | `12cbff8376266e330ee3eb2b34f5d05668eaf1d40a54e4cb2f49203bcf75dc4e` |
| 设置 | SettingsDark.dc.html | `a7f7f53b5d4a9fce4cdb2863f0db2ef0048c7d6dfce4bda9fdc79fb722ec9cf1` |
| 授权管理 | AuthManage-v2.dc.html | `6ec2c5069bcaffe6773e7734aea8702524ccdea3df29945b90dff210ef57e2c1` |
| 授权管理 | AuthManageBlocked-v2.dc.html | `574ac747fe2d858c1b18d8020c1af9ad1778d3504a51fb71baf91222c0fb7492` |
| 授权管理 | AuthManageStates.dc.html | `15de53bd2b70f3952bb1eafa49ee40ad4069e14aa9e8c5eaaa15e85551624227` |
| 授权管理 | AuthManageDark.dc.html | `6d723fa682b2d6923d09ccec98dad3197da878dd6b39530ff4bdea26865f37bf` |
| 绑定手机号 | BindPhone-v2.dc.html | `4fdff9d70e97a223804b8f531d0b72a8b963ecce48cd384795fa8b84605f6662` |
| 绑定手机号 | BindPhoneMerge-v2.dc.html | `d89ad26e1582b1098e99b72378f21d24a3406765ff3efc6f9b52eb672dfa4479` |
| 绑定手机号 | BindPhoneDark.dc.html | `80a6aaaf5641da91ee47298d11150697cf453675b5fcfd1ae744a2390e8d17a7` |
| 更换手机号 | PhoneChange-v2.dc.html | `1d1bd865a3e34b37e50bb3f252168a37eb7dfad0eac7d594378a6ce2937e321c` |
| 更换手机号 | PhoneChangeCode.dc.html | `6a3cbdf3dd344a13e9342a0db98a7f0b066375340dd85963cf95640b9ec7ea19` |
| 更换手机号 | PhoneChangeCodeError.dc.html | `bdd15e1d00e3d6245316ad22c7e9f49b7227ca267addf7da6abf2f7784045a1a` |
| 更换手机号 | PhoneChangeNew-v2.dc.html | `0c98cf15078366aa6dbcf73a92d34e62d18b38afdeac2f868cc57a040ddc44c3` |
| 更换手机号 | PhoneChangeNewCode.dc.html | `1987f56addb8efc0fc7a364da0b3ed7e000a1dcd28aad930bc12e5b2e629cadb` |
| 更换手机号 | PhoneChangeStepUp.dc.html | `fc17181ebdcf8062f3d9b4bad3cedab4b993f81632ff81bb2cb51752ec02e78e` |
| 更换手机号 | PhoneChangeDisabled.dc.html | `5197b3edcb8ca226466dc487d25a7d76f1724b5d9671861c96453c12cbeeaedf` |
| 更换手机号 | PhoneChangeNewBlocked-v2.dc.html | `e60305593c1559cffdd6928c594bb0e39c876b616a2248d375cdc29ecbac07e0` |
| 更换手机号 | PhoneChangeDone.dc.html | `3f47cfe39eabdc8affc71ab0db55d624d339ccedb93e8de21af945069f7c6474` |
| 更换手机号 | PhoneChangePendingCompleted.dc.html | `691ff322070028b3a49376b6364f59a8796f2494f225132f4caecd7ec701e063` |
| 更换手机号 | PhoneChangePendingConfirm-v2.dc.html | `c1e7e6c0956ecc6da728f48f1843c58614354ced766f8420b1e0076cb34e0daa` |
| 更换手机号 | PhoneChangePendingBusy-v2.dc.html | `d44b0aefe59668ca8601c5ba0c0d8884bbfc57fbca66eb22425f91cecd6b9d83` |
| 更换手机号 | PhoneChangePendingStill-v2.dc.html | `3e10aa31db8442b4793d180b245919e5b5172a3b3f5689e4dbc629e3b216b6f9` |
| 更换手机号 | PhoneChangePendingAbandonConfirm-v2.dc.html | `50458ccf981483b8c4e57ad05486382c5c1faf7d1091c77f408e238820ec8413` |
| 更换手机号 | PhoneChangePendingAbandoned-v2.dc.html | `ae968e41937fade84cb6c6ce0099b7ecdc0f6fa0aa972b9f1daecde085104da6` |
| 更换手机号 | PhoneChangePendingStates.dc.html | `49c4ff4380563d4238e00a6ee99da1b4cc1009bbe92c389b3f8d1436921e9ba6` |
| 更换手机号 | PhoneChangeCodeDark.dc.html | `a84b40775de95d259cfde3d2da162604a7c0abd04908237824d36d758dbe3e6b` |
| 账号注销 | DeleteAccount-v2.dc.html | `9b74b389e07dbb69ac88005ecb330b8f1c44a5c1aa989d64f59f649e32ea6d84` |
| 账号注销 | DeleteAccountNegative-v2.dc.html | `ab5422686c0e0db3d907b567127b14e08606271f758e19b90e0c7f71b962519d` |
| 账号注销 | DeleteAccountStepUp.dc.html | `8445746f2573896054757d5d7fa0da0b525a2ea7846aeafa9d489c7ab6943de5` |
| 账号注销 | DeleteAccountStepUpOauth.dc.html | `b624fff7b3b882f320daa9b8cae05ccc3a0eb16f866f8a3af14005cf2a47e0af` |
| 账号注销 | DeleteAccountCooling-v2.dc.html | `1151e001443d5d6d68d7e5f9aa8d083f8935263f19729bb92a4c70245d7bafd2` |
| 账号注销 | DeleteAccountStates.dc.html | `ccdf48577918d6e531029ee8c5fe154a453c43b6dc9af533c3090bb6cd4cb97f` |
| 账号注销 | DeleteAccountPendingConfirm-v2.dc.html | `d7f4be15ebc37e02f12c06f1a985c94ee9b254f58b594085dfc626c774c99991` |
| 账号注销 | DeleteAccountPendingAbandonConfirm-v2.dc.html | `d875086763c99e23be3fca07caa8deeb21fd7c8af546ee55d0f069b57056d670` |
| 账号注销 | DeleteAccountPendingBusy-v2.dc.html | `8f9aaf7a52ed6de0fc87c0f9b36c6210eded8b5e4d720143c25ef7b6d89e63bd` |
| 账号注销 | DeleteAccountPendingStill-v2.dc.html | `978a75afdafe0947395af5e1b1ee264ce5dbc90959955cf10849c0a288a6c64c` |
| 账号注销 | DeleteAccountPendingAbandoned-v2.dc.html | `8c9782a8958908441e1dec25478dc3e7076c3b0c0a253a318b38a0bcd3437f74` |
| 账号注销 | DeleteAccountPendingCompleted-v2.dc.html | `bc9bfc74adf3cda289de7aef3fd5b149a2e1cac524027f66c92dccd210051393` |
| 账号注销 | DeleteAccountPendingStates.dc.html | `817fda267b005aa36f6e883efd61fc8dea519dc3efcd2bb01923626fa2e5b7a0` |
| 账号注销 | DeleteAccountDark.dc.html | `46c626b04b230f2a628ec8901a58f4719ba4dc9a2f47f2713bade9a5d2a47e20` |
| 账号注销 | DeleteAccountCoolingDark.dc.html | `cf1601c78a36123747f53a1e208c693538961b4a504f127fe7175955af91563b` |
| 账号状态 | RiskNoticeBanned-v2.dc.html | `8c6270eba567c667aad56e69403e67e2ab565236c5674646ce15080f1558d68b` |
| 账号状态 | RiskNoticeBannedAppealing-v2.dc.html | `1ee8c613ca2bdfef76c8f44cd1ec6cb5e6cd498aa10afead6875be971faa7518` |
| 账号状态 | RiskNoticeBannedUpheld-v2.dc.html | `590aeb864498a75b02ab6fd56a4f4458e01d1428790071e2473562d56a992804` |
| 账号状态 | RiskNoticeFrozen.dc.html | `f11e629fb6a93d84c8c890688a541a5bc9a28467d5932c0a1f08f412471bb35d` |
| 账号状态 | RiskNoticeFrozenAppealing.dc.html | `eaea66bca60421cee6ed375f71879de28061ae40a53e17628072bf8d1de4c17b` |
| 账号状态 | RiskNoticeStates.dc.html | `97b956d881d07542377df187572f9b8d305923a54c222b64a441a52cc96a81af` |
| 账号状态 | RiskNoticeDark.dc.html | `fd65380f1a8a1130ffe339db64f8d1e8a64d1ed2e402d4a28e1d309433d43923` |
| 申诉 | Appeal.dc.html | `867e969a8ca2e90ef2874841fa851dc73f3ec4aeff45650efb8675bb85b766e2` |
| 申诉 | AppealFrozen.dc.html | `c16f5816f4c9739bc10e71adeca51e2aba3b416586631e4b21d1d2dd6b3df340` |
| 申诉 | AppealProgress-v2.dc.html | `4ad2437f61abc7195b01a1790d6609883b94e095209e2dc0a23e9e19eb8a9881` |
| 申诉 | AppealProgressFrozen-v2.dc.html | `9e94939c1429d52ea45334df3da8f7d1262c5f6632ff6739dae02c5f0bdbe0bf` |
| 申诉 | AppealResultLifted-v2.dc.html | `251aa4ccf1d428679742224d8a1183971b32258659eb654ca31aa7415b675fe6` |
| 申诉 | AppealResultLiftedFrozen-v2.dc.html | `9cb0634a9e66d3d985e2b99073fe07b2a8f8aa663e33ea4d760d08d3db1f156c` |
| 申诉 | AppealResultUpheld-v2.dc.html | `e083d8b577bab1bb634daab681d2a29b5818fa3a685b530097ca71c9d297d119` |
| 申诉 | AppealResultUpheldFrozen-v2.dc.html | `367dba9c465f225bc9c881cf9cde86d6323b6a15d183f6f52c59a4edf5944f49` |
| 申诉 | AppealDark.dc.html | `62a4eda4ba263c2ffea2dac54a8c0709a44342993a72811faa477a9c2a235ad5` |
| 申诉 | AppealProgressDark.dc.html | `89b821ca3740de1fe28ea3737e7ba64c2dc85b7947d4e6b56a005482c28896ab` |
| 启动 | LaunchPrivacy-v2.dc.html | `a9508e0b1833b621523f4f2d8ae31eb7532e7d749ac6dafb3120dea887262e74` |
| 启动 | LaunchSecondNotice-v2.dc.html | `5e9c8122542974e6472b48835cb3c9d171f6c1aad190e5f39e1498a598276571` |
| 启动 | LaunchPrivacyDark.dc.html | `601ee4066aaf3421a5fc0d9a8f80c1ea134d653c39e151ec3c11e91a611d56af` |
| 隐私中心 | PrivacyCenter.dc.html | `4d60cd5f4c7c0b7191b128f1a236b0fa5e93cd31e480b6e6388f5ef0a824d686` |
| 隐私中心 | PrivacyCenterBasic-v2.dc.html | `a7745af326cc13869eec7c1492e80836536f89a34d37013370070e1ccad7952d` |
| 隐私中心 | PrivacyCenterWithdraw.dc.html | `903bc26faeb6293b70a79f37567cee3cdfba3e51797a6772a341670c7d7a986e` |
| 隐私中心 | PrivacyCenterForceUpdate.dc.html | `2def87c570a3b1f66b781bde10b5870d72778fec61028e77cc9485cd6808790d` |
| 隐私中心 | PrivacyCollectList-v2.dc.html | `01468077a062c072acb79a00c52288a06ca7b29e203a37b97a10c6fe4d7617dc` |
| 隐私中心 | PrivacyShareList-v2.dc.html | `6a1059851bade8eebb1dc500c6cbe0af409f6cfe6b9a13415ddfc2f5374314e6` |
| 隐私中心 | PrivacyCenterDark.dc.html | `64049c0d2da354dd7986c87b32c2ff2a41288363b04964f48a0f75936d88d558` |
| 协议 | Agreement-v2.dc.html | `c0dfe5894c4f78c46f502c195e17cafe6f5cc92c5fb4c7a1659978a9c9dc477c` |
| 协议 | AgreementDark.dc.html | `ae7bf8c3496f46d0c9798594d8c037282f7c6007137bcca3a242f89e716286dc` |
| 关于 | About-v2.dc.html | `93b849722a71f28e586a8d5bdf6d60ee4d138a1f43cbe2c700f666c9463f600b` |
| 关于 | AboutBeforeFiling.dc.html | `976dc087f1baff93014da987f6878504ad47ae181f51621ea4cf33d54f7656d2` |
| 关于 | AboutDark.dc.html | `f24efdd79bfb53ac2a0ad4f72075af0344c5c5df164e5a7c2c48c71326873d9a` |
| 帮助中心 | Help-v2.dc.html | `4a5546b509d63aa7595058b2a33cd07ad278313da7b7e965a297b90c6b1d35d8` |
| 帮助中心 | HelpCategory.dc.html | `d3026b2d8821eb5d403e1174293ab93cdaca5e045f1473e352c6f102ec827ffe` |
| 帮助中心 | HelpArticle-v2.dc.html | `3685fd8ae05529c1294d6e14048e6d34185b03f7133ef9de75a5eb593d5b9c5d` |
| 帮助中心 | HelpArticleJd-v2.dc.html | `68ffc6ec62d937823a29074cf6151fb6ced96cdbafcb35baabb8a5da91b2f691` |
| 帮助中心 | HelpArticlePdd-v2.dc.html | `2ce123f4201a45d81643f099a37f6a2e5ead8b129c9def78aeaf85dd6dad2213` |
| 帮助中心 | HelpArticleAppeal.dc.html | `9d92c381992dc6e87438ebc09f6fc7fcc0dd6ab2fab14062d55a65c7e7943a18` |
| 帮助中心 | HelpArticleAppealPending.dc.html | `351214e3823aa4900ac8033d34cfd1f94521d63d9b9e885b0ee6658321718a27` |
| 帮助中心 | HelpArticleAppealNormal.dc.html | `b2f6a28bb79c417e7095ff1cb6f688d95e5a480ec2cd104301a49c9f6c32e94c` |
| 帮助中心 | HelpArticleInviteRules-v2.dc.html | `d762d2754cab788cb22e81fbfc5715c6f05fc8363bb1c7fe74400ea17eadcf35` |
| 帮助中心 | HelpArticleInviteReward.dc.html | `484f4baa796f27e5c2f379c5ce6e689d6a34b5bccdec4b1242297f0e52977df8` |
| 帮助中心 | HelpArticleLogin.dc.html | `ba58d58acf95a152d6c9c104c8d929861a0bb07cfc93b93f15c05a7c35be76e1` |
| 帮助中心 | HelpArticleNewbie.dc.html | `6cdbdfa639010e0f7228ccf46c64aaddd730846157e75b7fc45feb88396aed87` |
| 帮助中心 | HelpArticleShareRules.dc.html | `935601e3992c0a43553e8cbb5815e278b4381bfa81a934765f8925d10f6115d5` |
| 帮助中心 | HelpArticleWithdrawRules-v2.dc.html | `489237b392f0bada3fa4683ca2bec1c9c6fffd9afee0ac2f4125029307702971` |
| 帮助中心 | HelpArticlePriceCompare-v2.dc.html | `76cdad420e624ff6695d35cd4e0ac91c5d0d60a1d8e1fa2a8e377d6a7ad854a5` |
| 帮助中心 | HelpDark.dc.html | `fb8a31afc715656ed2a081430f84d244eb723c7a61e039f5d4b16ff1fc9c631c` |
| 帮助中心 | HelpArticleDark.dc.html | `625f39bb22111e61b478d0460c879590f126ad4f148b212f6b6950b539859256` |
| 返利规则 | Rules-v2.dc.html | `d2e113e9883b2f4fb8ee1d8fb3175580e0644630562732f36a4f45d5e7b57a95` |
| 返利规则 | RulesDark.dc.html | `3e73723b35e46ad767558cf759378786e7f72f88af5a4edd45be35eaf372cf9e` |
| 联系客服 | CsOpenFailed-v2.dc.html | `2beaf0e8a7718481ef397ce464c2a5bd81758bc20d7212187c765fe4357c8dc6` |
| 联系客服 | CsWechatMissing-v2.dc.html | `10b1ba303b9ac1dfc84c8c2f7b87fa5d820d0f7ffdcddf88991cc4b79bc41e0a` |
| 联系客服 | CsWechatMissingDark.dc.html | `52572584780a984dd01aaa284ee0009e0e1a08f14008c803c075e9a5b51d3249` |
| 基本模式 | BasicMode-v2.dc.html | `df31418fe202d3877bb631a43d81eaac7a02bdb08150af4c3529aa938a7bb61e` |
| 基本模式 | BasicModeDark.dc.html | `d7770416eca3cebbafc37ba41f9dd3c705b659a2a0dea55186ec9dd783f7c151` |
| 版本更新 | MainUpdatePrompt-v2.dc.html | `b4780f118e85a65107d6408d410573144e88ad1c5de9d1631c553122fe913676` |
| 版本更新 | ForceUpdate-v2.dc.html | `b78478684ed48819148af0c03e48a98814452c78b2a086fc5b3a5de706309277` |
| 版本更新 | ForceUpdateUnavailable-v2.dc.html | `726b568b3a09cf65df1746db8fd77e07b59e2565c0751975feda5fe8643edb45` |
| 版本更新 | ForceUpdateDark.dc.html | `95aa44fd09a7ed224efd43cfaf73eebd3a82f9e795613d224789aca67bde0d0a` |
| 版本更新 | MainUpdatePromptDark.dc.html | `296ecb16144747ae8b6d66ae41e1b5f9b2cb8870e3e01b1cd1046bf3d652ce4f` |
| 可信容器 | WebPage.dc.html | `8462e7f48f77a67e3e20c10c9f5ea1ec2ddbd5f97357cf266ce0f13ddc60f4bf` |
| 可信容器 | WebPageLoading.dc.html | `1be4a2650b6784ef413197f09d5a0473172195f2fdd885c0bb2125a80a85fa0f` |
| 可信容器 | WebPageError.dc.html | `d9be49c55f09007c42a48513f85cad32f0268b73b5fdb60e22a272d43c56b6de` |
| 可信容器 | WebPageMaintenance.dc.html | `d093e9ad2b39f615129ea139ecbf60e020b4a330cac61a478b5258fec4abc3fc` |
| 通用状态 | StateLoadFailed.dc.html | `aea7c5d30a2483fa9c9a18da8bf5ad0a3ae081e0373e29c9edba0fad4b54ae25` |
| 通用状态 | StateNetworkError.dc.html | `022db8798446a37f3d49f83810c7755567a59e6fe69615b5f33cdc4c06a0b89b` |
| 第三方页容器 | ExternalPage.dc.html | `62659243f951344c3b2a9633beb28aef1f58576c8e8f4e33e0ada90b0ebca216` |
| 第三方页容器 | ExternalPageBlocked.dc.html | `49d847862a25b71c34ab2fab19699586a2e005c2d4979045002d7ae8f9365776` |
| 第三方页容器 | ExternalPageDownloadBlocked.dc.html | `1f9899f2b9b1f15dd1bb101da0f7898a2f31c375405e53efd0bafec4cd031977` |
| 第三方页容器 | ExternalPageError.dc.html | `ed710d9cdf8bc0b9a13725f19774e25b75b9fb9d1c828ec37dcc9104bf0dee66` |
| 第三方页容器 | ExternalPageProductUnresolved.dc.html | `349dec8df20a07edc03d49f34af222d5634000b251815ffc9b0938d6438c93ec` |
| 第三方页容器 | ExternalPageDark.dc.html | `a3eb6e6553adf584c0127ec539b94402804080dbe7f047d91f55696873301efe` |
| AI 页面引导 | AgentPageGuide.dc.html | `c994bf2413d3d47d670b960625af7e8038d26e16f3225eba3f850ccfb9974118` |
| AI 页面引导 | AgentPageGuideStates.dc.html | `0b931745ab4744dba20d9fe71f3ac3dddc4bfab7b880d4306b77269f99cf7cf2` |
| AI 页面引导 | AgentPageGuideDark.dc.html | `93a3a98c2464cfb1b9be7a9fc9bf5372ca961a6be1787a62f65a35f344e9bf3f` |

## 本次交付验证

项目接入检查（2026-10-01）：根配置校验通过 80 个令牌、14 个资产、20 个颜色角色，两份生成文件与源一致；70 项生成器正反例检查通过。展示页的 33 组浏览器检查及 14 组补充检查覆盖 HTTP / 直接打开 HTML、资源绑定、色值复制、图标切换、按钮实际按下与状态语义、键盘焦点、重复绑定无资源重载，以及 390px / 320px 和 200% 字号布局，控制台无错误。上述是品牌预览与生成工具检查，正式三端工程和真机验收仍按清单推进。

2026-10-04 设计方向第三轮（[变更记录](../docs/changes/20261004-设计方向第三轮.md) §1）：令牌升到 v0.3.0，根配置校验通过 87 个令牌、14 个资产、29 个颜色角色，两份生成文件与源一致；展示页经本机 HTTP 打开，页面底为新值、返利标签为新配色、控制台无错误。只核对了色块与返利标签两处，没有重跑上面的整套浏览器检查。

完整检查脚本、结果与截图按项目协作约定保存在本机同级运行目录 `../couli-runs/brand-apply-20261001/`，未加入公开仓库；此处只记录本次检查结论。任一检出环境可执行 `python3 scripts/sync-brand.py --check` 重核当前源与生成物，浏览器效果需按 [接入指南](../docs/brand-integration.md) 另行验证。

第一版历史记录见 [初版交付](brand/delivery-20261001.md)，当前修订与复评见 [第二版交付](brand/delivery-v2-20261001.md)。品牌 Logo 的中文字标已转曲；默认 App 图标的 1024 PNG 背景全不透明、未裁圆角，分层前景保留透明。英文名已定为 Couli（2026-10-06）；正式 Slogan、启动页及完整关键页验收保持原待办状态。

## 命名

- 文件名用英文小写和短横线，如 `logo-horizontal.svg`、`icon-1024.png`；不用中文、空格。
- 同一素材有多个版本时加日期后缀，如 `logo-v20261005.svg`；最终版去掉后缀或放在该文件夹根目录，旧版移到 `_archive/`。
