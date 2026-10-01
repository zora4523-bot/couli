# 原创方向稿验证证据

**v8 是最新排版抛光证据；v7 保留金额与日期整组排版、v6 保留日期补修、v5 保留完整导航修订证据。** 文件名带 `v4`、`v3` 以及未标版本的第二版图片保留为历史对照，不代表当前返回行为。所有账户、商品与交易数据均为虚构；此目录仅保存凑狸原创界面与本地检查记录，第三方参考 App 图片不入库。

## 最新 v8：关联订单箭头保持同行

[ledger-v8.png](ledger-v8.png) 与 [ledger-200pct-v8.png](ledger-200pct-v8.png) 为最新流水画面。CTA 中「订单 →」整组不换行，按钮完整文字和可访问名称仍为「查看关联订单 →」，未加空格。

[validation-v8.txt](validation-v8.txt) 和 [v8-check.js](v8-check.js) 记录 390px 常规、320px 200% 根字号的针对性检查：金额、日期、订单加箭头三组各只有一个渲染矩形，无横向溢出；两种尺寸下点击关联订单并返回均可用。两张完整截图已经目视检查，未见新的明显孤立符号或裁切。导航逻辑与其他文案未改。

## v7：金额与日期保持完整

[ledger-v7.png](ledger-v7.png) 与 [ledger-200pct-v7.png](ledger-200pct-v7.png) 为最新流水画面。`+¥1.5` 和演示日期 `2026-10-01` 分别复用已有 `.money` 样式保持整组不换行；可见文字、日期规则与导航均未改。

[validation-v7.txt](validation-v7.txt) 和 [v7-check.js](v7-check.js) 记录 390px 常规、320px 200% 根字号两组针对性实测：两个文字组各只有一个渲染矩形，文字内容不变，无横向溢出。此轮未重复导航全套。

## v6：流水日期补修

[ledger-v6.png](ledger-v6.png) 与 [ledger-200pct-v6.png](ledger-200pct-v6.png) 分别为 390px 常规、320px 200% 根字号的新渲染截图。流水日期按 BR-TEXT-11 改为「昨天 14:00」，同时明确演示日期为 2026-10-01；订单列表与详情日期保持不变。

[validation-v6.txt](validation-v6.txt) 和 [v6-check.js](v6-check.js) 记录七个针对性浏览器检查点：从我的／钱包进入流水、关联订单返回、两种字号下的新文案及导航归属。此轮只改一处日期文案，未改导航逻辑，也未重复 v5 全套。历史 v5 脚本与记录保持原样，其中「09-30」旧文案断言不再作为当前日期验收；当前日期以 v6 断言为准。

## v5：完整导航修订

| 文件 | 检查画面或用途 |
| --- | --- |
| [home-v5.png](home-v5.png) | 首页、独立搜索与 AI 入口、三平台商品卡 |
| [ledger-from-me-v5.png](ledger-from-me-v5.png) | 从我的进入流水，返回我的；图中日期为 v5 历史文案 |
| [order-from-ai-v5.png](order-from-ai-v5.png) | 从 AI 进入订单，返回 AI，AI Tab 保持选中 |
| [order-from-ledger-v5.png](order-from-ledger-v5.png) | 从流水进入订单，返回流水，我的 Tab 保持选中 |
| [search-ai-off-v5.png](search-ai-off-v5.png) | AI 关闭后的搜索根页，不出现返回按钮 |
| [order-pending-v5.png](order-pending-v5.png) | 待结算四节点时间线；示例收货 09:30，早于状态栏 9:41 |
| [validation-v5.txt](validation-v5.txt) | 完整入口、前进、返回矩阵及实际浏览器检查记录 |
| [v5-check.js](v5-check.js) | 本次实际执行的 Playwright CLI `run-code` 函数，接收 `page`，不是独立 Node 脚本 |

v5 在一次连续浏览器会话中通过 53 个导航检查点，覆盖商品、普通搜索、AI、订单、流水、提现、找回和说明弹窗；包含多来源长链、两个提现返回入口、跨 Tab 后再次进入以及详情中切换 AI 开关。每个检查点核对当前页与栈、无回环、唯一选中 Tab 和根页无返回。另对五个变更后的页面进行了 320px、200% 根字号布局检查，未发现横向溢出。完整断言与范围以脚本和记录为准。

脚本使用本地预览 `http://127.0.0.1:8765/brand/index.html`，截图输出仍指向 `/tmp/couli-ui-review/`；本目录 PNG 是该次实际新渲染截图的原样副本。

## 其他记录与验证边界

`asset-validation.txt` 记录生产素材和令牌的格式、数值检查；`ui-validation.txt` 为首次界面重写后的检查，`validation-v3.txt`、`validation-v4.txt` 为此前补修回归。旧图仅用于比较，不将其导航状态作为 v5 的证据。

浏览器根字号和强制颜色模拟不代替原生 Dynamic Type、VoiceOver、三端真机或系统图标渲染验证。可点击演示不代表登录、AI、平台授权、交易、订单同步或提现服务已实现。
