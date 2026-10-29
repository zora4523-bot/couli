# 设置 Settings（App 原生，含修改昵称子页）

- 核对版本：规划提交 32a9765；代码主干 f1cd662c（rebate-platform 远端 main，2026-10-21 核对；派发前再核对一次，对不上的写进第 7 节）
- 定稿：负责人 2026-10-21「全部定稿吧 先开发 后面在微调」（[变更记录](../../docs/changes/20261021-App内高保真第3批定稿.md)）；画板在 `couli-runs/design-hifi/project/<文件名>`（1 倍 PNG 在 `review-me/v1/png/`），不入公开仓库，完整 sha256 见 [design/README.md](../README.md)「App 内高保真第 3 批定稿」；逐张改动与依据见 `review-me/v1/README.md` §3
- 路由：`Settings`（auth none，游客与基本模式可达，入口 in_app / push）；从哪来：「我的」、基本模式首页；去哪：修改昵称（本页子页）、`PhoneChange` / `BindPhone`、`AuthManage`、`DeleteAccount`（公开版）、`PrivacyCenter`、`Agreement`、通知设置、`Help`、`About`、`Login`
- 需求：01 §4.2 `Settings` 行；F-ACC-05、F-ACC-13、F-CFG-09、F-PRIV-04；规则只引编号：BR-ID-02 细则「未登录时的隐私入口」、BR-ID-11、BR-ID-16（2026-10-17 改版，细则「首次用途说明弹层」）、BR-ID-27 细则（注销入口只在公开版）、BR-ID-39、BR-ATTR-21；验收：AC-S1-61、AC-S1-77、AC-S1-137、AC-S1-03、AC-S1-158、AC-S1-185；任务：APP-12、HM-08
- 可参考的已合并页面：原生三端仓库派发前核对
- 是否资金或归属页面：否

## 1. 画板与状态

| 状态 | 画板文件（sha256 前 12 位） | 什么时候出现 | 数据来源 |
| --- | --- | --- | --- |
| 已登录（公开版） | Settings-v2.dc.html（d076d94490d7） | 已登录；内测包去掉「注销账号」行 | getMe · 200（nickname、手机号脱敏）；本地缓存大小、剪贴板开关 |
| 游客 | SettingsGuest-v2.dc.html（7663f3b8db53） | 未登录、已同意隐私政策 | 本地；只显示非账号条目 |
| 基本模式 | SettingsBasic.dc.html（dca586aae4d5） | 未同意隐私政策 | 本地；不显示剪贴板与清除缓存，只发 BR-ID-11 允许的匿名请求 |
| 剪贴板用途说明（2026-10-30 停用，不实现） | SettingsClipboardConsent.dc.html（668e9c73da58） | 首次打开剪贴板开关 | 【开启】调 recordConsent（type=clipboard_auto_import，version=`config.clipboard.consent_version`）后开关打开 |
| 协议选择半屏 | SettingsAgreementSheet-v2.dc.html（7a2f9deca056） | 点「用户协议与隐私政策」 | 本地；选中后开 `Agreement` |
| 清除缓存确认 / 已清除 | SettingsClearCache-v2.dc.html（2aff1c58b7b3）、SettingsCacheCleared-v2.dc.html（b8697ade4555） | 点「清除缓存」/ 确认后 | 本地（只清图片与 WebView HTTP 缓存，F-CFG-09）；清除后该行为 0 KB |
| 退出登录确认 | SettingsLogoutConfirm-v2.dc.html（fbdb33920e19） | 点【退出登录】 | 确认后调 logout，回「我的」游客态 |
| 已撤回注销申请 | SettingsDeletionWithdrawn-v2.dc.html（e1997e11d790） | 从 `DeleteAccount` 撤回成功返回 | cancelDeletion · 200 后重取 getMe |
| 修改昵称 / 已修改 | SettingsNickname.dc.html（18c611dc0ba7）、SettingsNicknameSaved-v2.dc.html（0703e0b867ee） | 点「昵称」/ updateMe · 200 | 本地校验长度（BR-ID-39），空值时【保存】置灰；成功回设置页轻提示 |
| 昵称：次数用完 / 未通过检查 | SettingsNicknameLimit.dc.html（75c51720903e）、SettingsNicknameSensitive.dc.html（12cbff837626） | updateMe · 30415 / 20001 reason=nickname_sensitive | 30415、20001 |
| 深色 | SettingsDark.dc.html（a7f7f53b5d4a） | 系统深色 | 同已登录；关闭态开关滑块保持白色 |

## 2. 组件

| 区域 | 组件（03 §10.2） | 数据 | 交互 |
| --- | --- | --- | --- |
| 分组列表 | 账号与安全 / 隐私 / 通用三组，行高随副标题；「重新显示下单须知」是动作行（无 ›） | — | 游客与已登录同一分组顺序；动作行调 resetTip 后轻提示、不跳页（BR-ATTR-21）；「注销账号」行只在公开版（BR-ID-27 细则） |
| 剪贴板开关 | 开关行（2026-10-30 起默认开启，品牌色轨道） | 本机设置 | 三端都显示；不再出用途说明弹层；用户关闭后保持关闭；基本模式不显示（BR-ID-16） |
| 基本模式 | 提示条 + 通栏【开启完整功能】 | — | 重新展示首启隐私弹窗（[app-launch.md](app-launch.md)） |

## 3. 文案键

| 位置 | 字典键 |
| --- | --- |
| 剪贴板开关 | BR-TEXT-14 表 C `settings.clipboard_auto` / `.desc`；用途弹层表 D `clipboard.consent.title` / `.body` / `.enable` / `.not_now` |
| 清除缓存、退出登录 | 表 C `settings.clear_cache` / `.size` / `.confirm` / `.confirm_ok` / `.confirm_cancel` / `.done`；`settings.logout` / `.confirm` / `.confirm_ok` / `.confirm_cancel` |
| 基本模式 | 表 D `privacy.basic_mode.notice` / `.enable` |
| 昵称错误 | 表 A `error.30415`；表 B `error.20001.nickname_sensitive` |
| 分组名与行名、「已重新显示下单须知」「未绑定」、游客提示与【去登录】、协议半屏标题、「昵称已修改」与昵称说明句、撤回注销轻提示 | 08 无键，用画板文案，待回写 |

## 4. 接口

| operationId | 什么时候调 | 本页会遇到的错误码 |
| --- | --- | --- |
| getMe / logout | 进页（已登录）/ 退出登录确认 | 10001 |
| updateMe | 修改昵称【保存】 | 20001（nickname_sensitive）、30415、10405 |
| recordConsent | 剪贴板用途弹层【开启】 | 20001、10401、10402、10405 |
| resetTip | 「重新显示下单须知」 | 20001、10405 |

## 6. 稿上没画、实现要做的

弹层焦点进入与关闭后回到触发行，确认框按钮按动作命名；剪贴板用途说明与系统许可分离（BR-ID-16）；画板上的昵称、号码与缓存大小为样例，按实际值显示；退出后推送解绑（F-ACC-05）；「账号与安全 → 登录方式」（F-ACC-14）为 P1，本期不做。

## 7. 待定与不一致

- 撤回注销后的轻提示借用站内信 DELETION_PROGRESS cancelled 原句，08 无轻提示键，待上游（BR-TEXT-14 补键）。
- 契约 `texts.default.json` 尚无 `settings.clipboard_auto*`、`clipboard.consent.*`、`settings.logout.*`，待契约线同步。
