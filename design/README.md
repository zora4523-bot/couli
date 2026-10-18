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
| 15 | 定稿的高保真稿 | App 与 H5 页面放 `hifi/`，**关键页定稿稿含深色版**（规划/00 D35，2026-10-18：登录 4 张先出；首页、详情、订单、钱包、我的在各自定稿批次加深色版；其余页面由实现按令牌推导、评审抽查深色截图）；管理后台稿入库前先逐张核对样例数据与风控规则标识，核对前不放进本公开仓库（代理默认，你可以改） | 随各页定稿 | 部分已交付：管理后台第 1 批（工作台、一框搜、用户查询与详情、订单查询与详情、找回审核）负责人 2026-10-18 定稿「全部按推荐」，画板清单与 sha256 见下方「管理后台第 1 批定稿」，规格在 `specs/admin-*.md`，画板文件本身留在本机运行目录不入库；App / H5 页面仍待你定稿，草稿在 claude.ai 画布与本机运行目录，未入库。稿件版本以页面规格里记的文件名与 sha256 为准 |
| 16 | 页面规格（一页一份，给实现者照做） | `specs/` | 各页定稿后 | 进行中：已有 8 份——首份 [specs/admins.md](specs/admins.md)（F1-06i 后台账号列表，2026-10-10，规划/11 §2.6）与管理后台第 1 批 7 份 `specs/admin-{dashboard,search,users,user-detail,orders,order-detail,claims}.md`（2026-10-18）；模板 [page-spec.md](../docs/templates/page-spec.md)；格式仍在试行，其他页面等试行后再定 |

完成一项后，把「状态」改为「已交付」，或者直接告诉 Claude。

## 管理后台第 1 批定稿（2026-10-18）

负责人 2026-10-18 21:3x 定稿：「第 1 批定稿，全部按推荐」。第 1 批 = 管理后台每天用的 7 页：工作台 / 待办中心、顶栏一框搜、用户查询、用户详情、订单查询、订单详情、找回审核。三条按推荐的决定（工作台「未关闭告警」卡本期不做、位置保留；一框搜无命中不区分「没有」与「没权限」；找回通过后归属锁定、误判只能驳回让用户重提）的落点见 [变更记录](../docs/changes/20261018-后台第1批定稿.md)。

- 规格：[admin-dashboard.md](specs/admin-dashboard.md)、[admin-search.md](specs/admin-search.md)、[admin-users.md](specs/admin-users.md)、[admin-user-detail.md](specs/admin-user-detail.md)、[admin-orders.md](specs/admin-orders.md)、[admin-order-detail.md](specs/admin-order-detail.md)、[admin-claims.md](specs/admin-claims.md)。
- 画板存放：本机运行目录 `couli-runs/design-hifi/project/<文件名>.dc.html`，1 倍 PNG 在 `couli-runs/design-hifi/review-admin/png/`；Codex 对抗审查 3 轮的记录在 `couli-runs/design-hifi/review-admin/review-log.md`。画板与 PNG **不入本公开仓库**，版本以下表 sha256 为准。
- 入库前核对（2026-10-18，逐张）：样例数据不含真实手机号、证件号与真实个人信息（手机号、身份证只以脱敏样式出现）；风控规则编号、处置与阈值为样例（规格里已标）；平台只以文字标识来源，无平台商标图形。

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

## 本次交付验证

项目接入检查（2026-10-01）：根配置校验通过 80 个令牌、14 个资产、20 个颜色角色，两份生成文件与源一致；70 项生成器正反例检查通过。展示页的 33 组浏览器检查及 14 组补充检查覆盖 HTTP / 直接打开 HTML、资源绑定、色值复制、图标切换、按钮实际按下与状态语义、键盘焦点、重复绑定无资源重载，以及 390px / 320px 和 200% 字号布局，控制台无错误。上述是品牌预览与生成工具检查，正式三端工程和真机验收仍按清单推进。

2026-10-04 设计方向第三轮（[变更记录](../docs/changes/20261004-设计方向第三轮.md) §1）：令牌升到 v0.3.0，根配置校验通过 87 个令牌、14 个资产、29 个颜色角色，两份生成文件与源一致；展示页经本机 HTTP 打开，页面底为新值、返利标签为新配色、控制台无错误。只核对了色块与返利标签两处，没有重跑上面的整套浏览器检查。

完整检查脚本、结果与截图按项目协作约定保存在本机同级运行目录 `../couli-runs/brand-apply-20261001/`，未加入公开仓库；此处只记录本次检查结论。任一检出环境可执行 `python3 scripts/sync-brand.py --check` 重核当前源与生成物，浏览器效果需按 [接入指南](../docs/brand-integration.md) 另行验证。

第一版历史记录见 [初版交付](brand/delivery-20261001.md)，当前修订与复评见 [第二版交付](brand/delivery-v2-20261001.md)。品牌 Logo 的中文字标已转曲；默认 App 图标的 1024 PNG 背景全不透明、未裁圆角，分层前景保留透明。英文名已定为 Couli（2026-10-06）；正式 Slogan、启动页及完整关键页验收保持原待办状态。

## 命名

- 文件名用英文小写和短横线，如 `logo-horizontal.svg`、`icon-1024.png`；不用中文、空格。
- 同一素材有多个版本时加日期后缀，如 `logo-v20261005.svg`；最终版去掉后缀或放在该文件夹根目录，旧版移到 `_archive/`。
