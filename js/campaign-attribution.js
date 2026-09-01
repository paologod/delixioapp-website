/**
 * Capture ad campaign query params for landing-page attribution.
 * Does not modify the browser URL. Params are read on load and on each CTA click.
 */
(function () {
  var CAMPAIGN_KEYS = [
    'utm_source',
    'utm_medium',
    'utm_campaign',
    'utm_content',
    'utm_term',
    'openai_campaign_id',
    'openai_ad_group_id',
    'openai_ad_id',
  ];

  function readCampaignParams() {
    var params = new URLSearchParams(window.location.search);
    var out = {};
    CAMPAIGN_KEYS.forEach(function (key) {
      var val = params.get(key);
      if (val) out[key] = val;
    });
    return out;
  }

  function persistCampaignContext() {
    var params = readCampaignParams();
    if (Object.keys(params).length === 0) return;
    try {
      sessionStorage.setItem('delixio_campaign', JSON.stringify(params));
    } catch (_) {
      /* ignore */
    }
  }

  function getStoredCampaignContext() {
    try {
      var raw = sessionStorage.getItem('delixio_campaign');
      if (raw) return JSON.parse(raw);
    } catch (_) {
      /* ignore */
    }
    return {};
  }

  function getCampaignContext() {
    var live = readCampaignParams();
    if (Object.keys(live).length > 0) return live;
    return getStoredCampaignContext();
  }

  function campaignAnalyticsProps() {
    var ctx = getCampaignContext();
    return {
      source: ctx.utm_source || undefined,
      medium: ctx.utm_medium || undefined,
      campaign: ctx.utm_campaign || undefined,
      content: ctx.utm_content || undefined,
      term: ctx.utm_term || undefined,
      openai_campaign_id: ctx.openai_campaign_id || undefined,
      openai_ad_group_id: ctx.openai_ad_group_id || undefined,
      openai_ad_id: ctx.openai_ad_id || undefined,
    };
  }

  function appendCampaignQuery(url) {
    try {
      var target = new URL(url, window.location.origin);
      if (target.origin !== window.location.origin) return url;
      var ctx = getCampaignContext();
      Object.keys(ctx).forEach(function (key) {
        if (!target.searchParams.has(key)) {
          target.searchParams.set(key, ctx[key]);
        }
      });
      return target.pathname + target.search + target.hash;
    } catch (_) {
      return url;
    }
  }

  function detectPrimaryStore() {
    var ua = navigator.userAgent || '';
    var isIos =
      /iPhone|iPad|iPod/i.test(ua) ||
      (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    var isAndroid = /Android/i.test(ua);
    if (isIos) return 'ios';
    if (isAndroid) return 'android';
    return null;
  }

  window.DelixioCampaign = {
    keys: CAMPAIGN_KEYS,
    readCampaignParams: readCampaignParams,
    getCampaignContext: getCampaignContext,
    campaignAnalyticsProps: campaignAnalyticsProps,
    appendCampaignQuery: appendCampaignQuery,
    detectPrimaryStore: detectPrimaryStore,
    persist: persistCampaignContext,
  };

  persistCampaignContext();

  document.addEventListener('DOMContentLoaded', function () {
    if (!document.body.classList.contains('page-it-ads')) return;
    var primary = detectPrimaryStore();
    if (!primary) return;
    document.querySelectorAll('[data-store-badge]').forEach(function (el) {
      if (el.getAttribute('data-store-badge') === primary) {
        el.classList.add('store-badge--primary');
      }
    });
    document.querySelectorAll('.it-ads-store-row').forEach(function (row) {
      row.setAttribute('data-primary-store', primary);
    });
  });
})();
