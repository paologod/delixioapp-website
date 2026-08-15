# Identifying ChatGPT referral traffic in Google Analytics

Delixio uses Google Analytics 4 with measurement ID `G-89YMNXP5XF`. Do not change analytics providers.

## UTM parameter

When ChatGPT Search (or ChatGPT browsing) sends users with campaign parameters, look for:

```text
utm_source=chatgpt.com
```

Optional related values you may also see over time:

- `utm_medium=...` (varies by integration)
- Referrer host containing `chatgpt.com` (when present)

## How to find it in GA4

1. Open GA4 property for Delixio.
2. Go to **Reports → Acquisition → Traffic acquisition** (or **Explore**).
3. Add a filter or dimension for **Session source** / **Session source/medium**.
4. Filter where source contains `chatgpt.com`, or create a comparison:
   - Dimension: `Session source`
   - Filter: `chatgpt.com`
5. Optionally build an **Exploration** with:
   - Rows: Session source, Landing page, Page path
   - Metrics: Sessions, Engaged sessions, Conversions (if configured)

## Optional: custom audience or report

Create a saved exploration named **ChatGPT referrals** with:

- Filter: `Session source` exactly matches or contains `chatgpt.com`
- Breakdown: Landing page + Device category

## Notes

- Not all ChatGPT-originated visits include UTMs; some may appear only as referral or direct.
- Do not invent fake UTM links in on-site copy.
- Keep existing gtag configuration; no provider migration is required for this check.
