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
| 4 | App 图标 | `app-icon/` | W1（10-11） | 1024 SVG/PNG 与分层源已交付；`.icon`、三端工程资源与真机验收待后续 |
| 5 | 启动页 | `splash/` | W1（10-11） | 待办 |
| 6 | 品牌主色、辅色、功能色 | `colors/colors.md` | **10-06** | 第二版作为当前基线；数值唯一源在 `tokens/design-tokens.json`，此文档维护语义与对比度记录 |
| 7 | 参考 App UI/UX 3–5 个 | `references/` | **10-06** | 已交付 5 个官方参考及实看画面记录；包含一淘、返利网，详见参考证据索引 |
| 8 | 设计令牌 | `tokens/` | 10-07 | 当前基线 JSON 已接入本仓库展示页；CSS / 浏览器配置可生成与查漂移，三端工程接入按[品牌接入](../docs/brand-integration.md)后续执行 |
| 9 | 7 个关键页确认 | `wireframes/`（原安排：代理出线框，你确认） | — | 2026-10-04 起不再逐页确认线框，页面改在高保真稿上确认，见第 15 项与[变更记录](../docs/changes/20261005-出图范围补登.md)；7 页线框已出稿，在分支 `design/key-page-wireframes`（未合并），只作高保真稿的内容来源 |
| 10 | Tab 与金刚区图标 | `icons/tab/`、`icons/grid/` | 随第 15 项 | 待办 |
| 11 | 平台标识素材（来源、授权、支付 / 收款、分享去向） | `icons/platform/`（要求见该目录 README） | W1 | 负责人准备中（2026-10-05，负责人统一准备；规划/06 Q-E7、Q-F8；2026-10-06 改为本目录作内置兜底、上线后在后台替换，BR-TEXT-24） |
| 12 | 空态、错误态插画 | `illustrations/` | W3（10-25） | 待办 |
| 13 | 分享海报、邀请海报 | `posters/` | W3（10-25） | 待办 |
| 14 | 商店上架素材 | `store/` | W7 提审前（11-22） | 待办 |
| 15 | 定稿的高保真稿 | App 与 H5 页面放 `hifi/`，**关键页定稿稿含深色版**（规划/00 D35，2026-10-18：登录 4 张先出；首页、详情、订单、钱包、我的在各自定稿批次加深色版；其余页面由实现按令牌推导、评审抽查深色截图）；管理后台稿入库前先逐张核对样例数据与风控规则标识，核对前不放进本公开仓库（代理默认，你可以改） | 随各页定稿 | 部分已交付：管理后台第 1 批（工作台、一框搜、用户查询与详情、订单查询与详情、找回审核）负责人 2026-10-18 定稿「全部按推荐」，画板清单与 sha256 见下方「管理后台第 1 批定稿」；管理后台第 2 批（财务：提现审核与打款、月结账单与对账差错、调账与核销、余额流水与导出、资金看板）负责人 2026-10-18 定稿「全部按推荐」，画板清单与 sha256 见下方「管理后台第 2 批定稿」，规格 `specs/admin-{withdrawals,withdrawal-detail,payouts,settle-bills,recon,adjustments,ledger,fund-dashboard}.md`（2026-10-18）；两批规格都在 `specs/admin-*.md`，画板文件本身留在本机运行目录不入库；App / H5 页面仍待你定稿，草稿在 claude.ai 画布与本机运行目录，未入库。稿件版本以页面规格里记的文件名与 sha256 为准 |
| 16 | 页面规格（一页一份，给实现者照做） | `specs/` | 各页定稿后 | 进行中：已有 16 份——首份 [specs/admins.md](specs/admins.md)（F1-06i 后台账号列表，2026-10-10，规划/11 §2.6）、管理后台第 1 批 7 份 `specs/admin-{dashboard,search,users,user-detail,orders,order-detail,claims}.md`（2026-10-18）与第 2 批 8 份 `specs/admin-{withdrawals,withdrawal-detail,payouts,settle-bills,recon,adjustments,ledger,fund-dashboard}.md`（2026-10-18）；模板 [page-spec.md](../docs/templates/page-spec.md)；格式仍在试行，其他页面等试行后再定 |

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

## 本次交付验证

项目接入检查（2026-10-01）：根配置校验通过 80 个令牌、14 个资产、20 个颜色角色，两份生成文件与源一致；70 项生成器正反例检查通过。展示页的 33 组浏览器检查及 14 组补充检查覆盖 HTTP / 直接打开 HTML、资源绑定、色值复制、图标切换、按钮实际按下与状态语义、键盘焦点、重复绑定无资源重载，以及 390px / 320px 和 200% 字号布局，控制台无错误。上述是品牌预览与生成工具检查，正式三端工程和真机验收仍按清单推进。

2026-10-04 设计方向第三轮（[变更记录](../docs/changes/20261004-设计方向第三轮.md) §1）：令牌升到 v0.3.0，根配置校验通过 87 个令牌、14 个资产、29 个颜色角色，两份生成文件与源一致；展示页经本机 HTTP 打开，页面底为新值、返利标签为新配色、控制台无错误。只核对了色块与返利标签两处，没有重跑上面的整套浏览器检查。

完整检查脚本、结果与截图按项目协作约定保存在本机同级运行目录 `../couli-runs/brand-apply-20261001/`，未加入公开仓库；此处只记录本次检查结论。任一检出环境可执行 `python3 scripts/sync-brand.py --check` 重核当前源与生成物，浏览器效果需按 [接入指南](../docs/brand-integration.md) 另行验证。

第一版历史记录见 [初版交付](brand/delivery-20261001.md)，当前修订与复评见 [第二版交付](brand/delivery-v2-20261001.md)。品牌 Logo 的中文字标已转曲；默认 App 图标的 1024 PNG 背景全不透明、未裁圆角，分层前景保留透明。英文名已定为 Couli（2026-10-06）；正式 Slogan、启动页及完整关键页验收保持原待办状态。

## 命名

- 文件名用英文小写和短横线，如 `logo-horizontal.svg`、`icon-1024.png`；不用中文、空格。
- 同一素材有多个版本时加日期后缀，如 `logo-v20261005.svg`；最终版去掉后缀或放在该文件夹根目录，旧版移到 `_archive/`。
