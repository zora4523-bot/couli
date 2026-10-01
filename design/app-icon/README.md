# 凑狸 · App 图标

设计记录：2026-10-01 第二版。品牌 Logo 是可用于页面、印刷与传播的透明底标志；App 图标是在系统启动器中使用的方形构图，需要背景、留白及系统外观适配。两者共享同一主体，不直接把横版字标塞进图标。

## 已准备的素材

| 文件 | 规格与用途 |
| --- | --- |
| `icon-default.svg` | 默认构图：主色 `#C44820` 背景、白色主体 |
| `icon-dark.svg` | 深色构图：`#28251F` 背景、`#F3A881` 主体 |
| `icon-tinted.svg` | 单色构图测试稿；不是系统 tinted 渲染结果 |
| `icon-1024.png` | 1024×1024、不透明、未裁圆角的默认图标 |
| `icon-foreground.png` | 1024×1024、透明底自适应前景；供 Android / 鸿蒙使用较大的安全留白 |
| `icon-background.png` | 1024×1024、不透明满画布背景 |
| `icon-monochrome.png` | 1024×1024、透明底单色主体；供主题图标适配使用 |
| `layers/background.svg` | 1024 方形纯色背景源文件，色值 `#C44820` |
| `layers/foreground.svg` | 1024 方形透明底、白色前景；一个 path、两个闭合子路径，供 iOS 构图 |
| `layers/foreground-body.svg`、`layers/foreground-tail.svg` | 相同画布下拆分的主体与尾尖，可在 Icon Composer 独立调节；不与合成 foreground 层重复叠加 |
| `layers/adaptive-foreground.svg` | Android / 鸿蒙安全区前景，对应 `icon-foreground.png` |
| `layers/monochrome.svg` | 自适应单色前景，对应 `icon-monochrome.png` |

当前交付是 SVG、PNG 与分层源文件，已在本机 Icon Composer 成功导入 body / tail 两个 SVG（工具显示 2 layers in 1 group，原画布位置与 100% 比例）；颜色面板与保存窗口的自动化读取随后失效，因此未完成外观验收，也未生成 `.icon` 文件。此次导入验证不能视为材质或真机验收。Android、鸿蒙的密度资源及平台接入需在相应工程阶段完成。

## Apple 指南与本方案的对应

Apple 建议图标简洁、主体居中、边缘清楚；重要特征在各外观中保持一致。iPhone、iPad、Mac 源画布为 1024×1024 方形，圆角由系统施加；导入背景时应满画布且不透明。SVG 等矢量图优先，文字需转为轮廓。[Apple HIG · App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons/)

凑狸采用单一实色轮廓，图标内不加小字、照片或 UI 截图。前景保留透明底，素材不烘焙投影、高光、毛边或玻璃效果。此类效果留到 Icon Composer 中调节，避免与系统光照重复；Apple 同样建议导出前移除效果与背景设置，并不要导出画布遮罩。[Creating your app icon using Icon Composer](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer)

本项目为不同用途分别设置留白：iOS 构图将 `256×256` 主体放大 `3.6` 倍、平移 `(51.2, 51.2)`；自适应前景放大 `3.05` 倍、平移 `(121.6, 121.6)`。iOS 版相较第一版放大主体，自适应版将所有非透明像素保留在中央直径 `66/108 × 1024 ≈ 625.78 px` 的保守安全圆内（这里是 66/108，约 61.1%，不是 66%）。Android 官方要求 108 dp 图层与中央 66 dp 安全范围；此处采用内接圆作保守检查，不把其等同于每个启动器的实际遮罩。[Android adaptive icons](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive) 上述参数都是凑狸自定，**不是 Apple 规定的固定缩放比例或安全区数值**；后续仍须按官方模板和实际遮罩检查。背景色与深色配色也属于品牌自定规范。

## Icon Composer 接入与验收

1. 新建 iOS 图标文档，使用官方最新网格或 1024 方形画布。优先在 Composer 内设置 `#C44820` 纯色背景；`layers/background.svg` 保留作交付参考或自定义背景来源。
2. 导入 `layers/foreground.svg`，保持原始 1024 画布与居中位置，命名为 `01-couli-mark`；也可替换为拆分的 body 与 tail 两层，但不能同时叠加合成层。背景和前景独立，不把整个平面图当作单个前景层。
3. 用同一轮廓配置 Default、Dark、Mono。Icon Composer 支持在同一文件中调整这些模式以及高光、折射、半透明和阴影；从低强度开始，以轮廓清晰为准。[Icon Composer 官方介绍](https://developer.apple.com/icon-composer/)
4. 在工具预览及支持的系统中检查 default、dark、clear light/dark、tinted light/dark；`icon-tinted.svg` 仅帮助检查单色识别，clear 与 tinted 的最终效果须由系统生成并验收。不要将平面 SVG 预览标成 Liquid Glass 效果。
5. 在真机主屏、搜索、设置和通知的小尺寸入口检查辨识度、边缘与背景对比，并换浅色、深色及复杂壁纸复查。通过后保存 `.icon`、接入 Xcode，再检查实际构建输出。

最低支持版本保持 **iOS 16**。若采用 `.icon`，需验证当前 Xcode 为旧系统生成的兼容图标；Apple 文档说明 `.icon` 会替代已有 AppIcon 资产，并为旧版本生成图像，若希望旧系统继续显示已有旧图标，应继续使用资产目录，而不是假设加入 `.icon` 后仍保留原图标。[Xcode 图标兼容说明 · Overview / Important](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer)。2026-10-01 已核对同一官方文档的[可读取 JSON](https://developer.apple.com/tutorials/data/documentation/xcode/creating-your-app-icon-using-icon-composer.json)，其中明确说明旧系统保留已有图标时继续使用资产目录。

深色 App 图标用于系统外观适配，不表示产品 MVP 启用深色界面。完成素材检查也不等于完成真机验收或获得 Apple 审核通过。
