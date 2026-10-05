'use strict';

// Local, generated configuration keeps both file:// and the preview server usable.
// Asset URLs are relative to this HTML document; no root-level fetch is needed.
(() => {
  const brand = window.COULI_BRAND;
  if (!brand) return;

  const aliases = {
    brandPrimary: '--orange', brandEmphasis: '--brand-text',
    canvas: '--paper', surface: '--white',
    textPrimary: '--ink', textSecondary: '--muted', link: '--link-color',
    price: '--price', rebateText: '--rebate', rebateBackground: '--rebate-bg', pendingText: '--pending', pendingBackground: '--pending-bg',
    successText: '--settled-text', successBackground: '--settled-bg',
    errorText: '--error-text', errorBackground: '--error-bg',
    primaryAction: '--primary-action-background', primaryActionText: '--primary-action-text',
    controlBorder: '--control-border', focusRing: '--focus-ring'
  };
  for (const [role, alias] of Object.entries(aliases)) {
    document.documentElement.style.setProperty(alias, `var(${brand.semantics[role].cssVariable})`);
  }

  function applyAssets(root = document) {
    root.querySelectorAll('[data-brand-asset]').forEach(element => {
      const url = brand.assets[element.dataset.brandAsset];
      const attribute = element.tagName === 'IMG' ? 'src' : 'href';
      if (url && element.getAttribute(attribute) !== url) element.setAttribute(attribute, url);
    });
  }
  applyAssets();
  document.querySelectorAll('[data-brand-token]').forEach(element => {
    const url = brand.tokens[element.dataset.brandToken];
    if (element.getAttribute('href') !== url) element.setAttribute('href', url);
  });
  document.querySelector('[data-brand-theme]').content = brand.semantics.primaryAction.value;

  document.querySelectorAll('[data-icon]').forEach(button => {
    button.addEventListener('click', () => {
      const variant = document.querySelector('#variant-icon');
      const role = {default: 'iconDefault', dark: 'iconDark', tinted: 'iconTinted'}[button.dataset.icon];
      document.querySelectorAll('[data-icon]').forEach(control => {
        control.setAttribute('aria-pressed', String(control === button));
      });
      variant.dataset.brandAsset = role;
      if (variant.getAttribute('src') !== brand.assets[role]) variant.src = brand.assets[role];
      variant.alt = button.textContent + '图标构图预览';
    });
  });

  document.querySelectorAll('[data-brand-swatch]').forEach(button => {
    const color = brand.semantics[button.dataset.brandSwatch];
    const value = color.value;
    button.querySelector('.swatch-color').style.backgroundColor = `var(${color.cssVariable})`;
    button.querySelector('[data-brand-hex]').textContent = `${value} / ${button.dataset.brandLabel}`;
    button.setAttribute('aria-label', `复制${button.querySelector('b').textContent}色值 ${value}`);
    button.addEventListener('click', async () => {
      const feedback = document.querySelector('#copy-feedback');
      try {
        await navigator.clipboard.writeText(value);
        feedback.textContent = '已复制 ' + value;
      } catch {
        feedback.textContent = '当前环境不支持自动复制，请手动复制：' + value;
      }
    });
  });
  document.querySelectorAll('[data-brand-value]').forEach(element => {
    element.textContent = brand.semantics[element.dataset.brandValue].value;
  });

  function luminance(hex) {
    const channels = hex.slice(1).match(/.{2}/g).map(channel => {
      const s = parseInt(channel, 16) / 255;
      return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
    });
    return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
  }
  const background = luminance(brand.semantics.primaryAction.value);
  const foreground = luminance(brand.semantics.primaryActionText.value);
  const contrast = (Math.max(background, foreground) + 0.05) / (Math.min(background, foreground) + 0.05);
  document.querySelector('[data-brand-contrast]').textContent = contrast.toFixed(2);

  // The App preview calls this after rendering dynamic brand marks.
  window.CouliBrand = Object.freeze({applyAssets});
})();
