document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.main-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(isOpen));
      toggle.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
    });

    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Open menu');
      });
    });
  }

  const pageType = document.querySelector('main.guide-page')
    ? 'guide'
    : document.querySelector('main.landing-page')
      ? 'landing'
      : 'site';
  const pagePath = window.location.pathname;

  const ctaLocation = (link) => {
    if (link.closest('.site-header')) return 'header';
    if (link.closest('.landing-download')) return 'landing_download';
    if (link.closest('.site-footer')) return 'footer';
    return 'content';
  };

  const sendEvent = (name, params) => {
    if (typeof window.gtag === 'function') {
      window.gtag('event', name, params);
    }
  };

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href]');
    if (!link) return;

    let destination;
    try {
      destination = new URL(link.href, window.location.origin);
    } catch {
      return;
    }

    const shared = {
      page_type: pageType,
      page_path: pagePath,
      cta_location: ctaLocation(link),
    };
    const isAppStore = destination.hostname === 'apps.apple.com';
    const isPlayStore = destination.hostname === 'play.google.com';
    const isDownloadPath = destination.origin === window.location.origin
      && (destination.pathname === '/go/' || destination.pathname === '/download/');

    if (isAppStore || isPlayStore) {
      sendEvent('store_click', {
        ...shared,
        store: isAppStore ? 'app_store' : 'google_play',
      });
    } else if (isDownloadPath) {
      sendEvent('cta_click', {
        ...shared,
        destination: destination.pathname,
      });
    } else {
      return;
    }

    if (pageType === 'landing') {
      sendEvent('landing_to_download_click', {
        ...shared,
        landing_slug: pagePath.replace(/^\/+|\/+$/g, ''),
        destination: isAppStore ? 'app_store' : isPlayStore ? 'google_play' : destination.pathname,
      });
    }
  });
});
