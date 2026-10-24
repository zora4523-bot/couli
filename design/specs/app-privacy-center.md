# 隐私中心 PrivacyCenter（App 原生 + 清单正文 H5）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`PrivacyCenter`（auth none，游客与基本模式可达，入口 in_app / push）；从哪来：设置、基本模式设置、强更页「隐私政策」；去哪：两份清单正文（H5）、`Agreement`（隐私政策、用户协议）、系统设置（系统权限一节）、`BasicMode`（撤回同意后）、`Launch`（基本模式【开启完整功能】）
- 需求：01 §4.2 `PrivacyCenter` 行；F-PRIV-04、F-PRIV-06；规则只引编号：BR-ID-02 细则、BR-ID-11、BR-ID-12、BR-ID-13（细则「隐私中心的系统权限一节」）、BR-ID-16、BR-ID-01 细则「受限会话」、03 §3.5（SDK 清单）、03 §4.1；验收：AC-PRIV-04（同号规则）、AC-S1-77、AC-S1-135、AC-S1-158、AC-S1-185；任务：APP-12、HM-08
- 可参考的已合并页面：`apps/h5/src/entries/app/pages/agreements/**`（清单正文的 H5 承载）
- 是否资金或归属页面：否（撤回同意会退出登录）

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 主态 | PrivacyCenter.dc.html（4d60cd5f4c7c） | 已同意隐私政策（游客或已登录） | 本地：个性化开关、各系统权限状态（只列本端实际会申请的权限） |
| 基本模式（只读） | PrivacyCenterBasic-v2.dc.html（a7745af326cc） | 未同意隐私政策 | 本地；【撤回同意】处改为【开启完整功能】 |
| 撤回同意确认 | PrivacyCenterWithdraw.dc.html（903bc26faeb6） | 点【撤回同意】 | 确认后 recordConsent（type=privacy，accepted=false，设备级）→ 退出登录进基本模式 |
| 从强更页进入 | PrivacyCenterForceUpdate.dc.html（2def87c570a3） | `ForceUpdate` 点「隐私政策」 | 本地；只留隐私政策、用户协议、两份清单与【撤回同意】，返回回强更页 |
| 个人信息收集清单 | PrivacyCollectList-v2.dc.html（01468077a062） | 点「个人信息收集清单」 | H5 正文（版式稿，正文待法务定稿） |
| 第三方共享清单 | PrivacyShareList-v2.dc.html（6a1059851bad） | 点「第三方共享清单」 | `Agreement` type=sdk_list（版式稿，正文待法务定稿） |
| 深色 | PrivacyCenterDark.dc.html（64049c0d2da3） | 系统深色 | 同主态 |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 清单与协议 | 列表行 | — | 打开 H5 正文 / `Agreement` |
| 个性化推荐 | 开关行 | 游客存本地；已登录每次切换写 recordConsent（type=personalization，BR-ID-13 细则） | 只作用于首页信息流（BR-ID-13） |
| 系统权限 | 权限行（用途 + 状态词） | 系统权限状态 | 点击跳系统设置 |
| 撤回同意 | 危险按钮 + 确认框（【取消】为主） | — | 确认后本机退出登录、进基本模式 |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 系统权限一节 | BR-TEXT-14 表 D `privacy.system_permissions.title` / `.hint` / `.status.granted` / `.denied` / `.not_asked`；`perm.photos.purpose` |
| 撤回同意确认 | 表 D `privacy.withdraw.confirm.title` / `.body` 与按钮 |
| 基本模式 | 表 D `privacy.basic_mode.notice` / `.enable` |
| 强更入口 | 表 C `app_update.privacy_policy` |
| 个性化说明、通知用途（现为 `perm.push.card_hint` 截短）、两份清单正式名称 | 08 无键或待法务，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| recordConsent | 撤回同意、切换个性化 | 20001、10401、10402、10405 |
| getAgreementVersion / listArticles（清单正文 H5） | 打开清单 | 30701 |

## 5. 权限点与开关

强更状态下 Router 只放行从强更页进入的 `PrivacyCenter`、`Agreement`、`Login`、`DeleteAccount`（03 §4.1）。

## 6. 稿上没画、实现要做的

撤回同意后的退出登录、SDK 停用与基本模式切换（BR-ID-13）；权限状态回前台刷新；清单长文的目录跳转与读屏标题层级。清单里的 SDK、收集项与用途是版式样例，以 03 §3.5 与法务定稿为准。

## 7. 待定与不一致

- 个人信息收集清单的正文承载：`routes.json` `Agreement.type` 只有 `agreement`、`privacy`、`sdk_list`、`labor_agreement`，没有收集清单，待上游（契约线 / 04）。
- 清单待法务定稿时补：阿里云号码认证 SDK（仅 iOS、Android）、支付宝支付 SDK（收款开启后）、服务端向联盟共享的归因标识、推送令牌与「浏览、搜索、点击记录用于个性化推荐」（03 §3.5），待上游。
- 第三方共享清单另补**阿里云短信服务**（2026-10-24，编排）：服务端经阿里云短信接口发送验证码（主通道，00 供应商选型 9-30），提供给阿里云的是手机号与短信正文（含验证码）；客户端不集成任何短信 SDK，所以写在「服务端共享」一类、不进 SDK 清单。启用备用通道时同样补该服务商。
