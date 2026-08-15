# Cloudflare checklist for Delixio SEO / AI crawl access

Manual verification in Cloudflare (DNS/proxy in front of GitHub Pages). Do **not** weaken general website security beyond what is needed for legitimate crawlers.

## Crawler access

- [ ] Confirm **OAI-SearchBot** is not blocked by WAF custom rules, IP deny lists, or Bot Fight Mode
- [ ] Confirm published [OpenAI crawler IP ranges](https://openai.com/chatgpt-gptbot) (and any OAI-SearchBot documentation OpenAI publishes) are allowed where you use IP allowlists
- [ ] Confirm **GPTBot** and **ChatGPT-User** are not unintentionally blocked if you want model/training or browsing access per your policy
- [ ] Confirm Googlebot and Bingbot remain allowed

## Challenges and bots

- [ ] No JavaScript challenge / interstitial for legitimate crawler user-agents on public HTML routes
- [ ] Bot Fight Mode (or Super Bot Fight Mode) is not blocking OAI-SearchBot responses with challenges
- [ ] Rate limits are reasonable for crawl bursts (allow normal sitemap and page fetches)

## Public SEO files

Verify these respond **200** without cookies or JavaScript:

- [ ] `https://delixioapp.com/robots.txt`
- [ ] `https://delixioapp.com/sitemap.xml`
- [ ] `https://delixioapp.com/llms.txt` (optional metadata)
- [ ] `https://delixioapp.com/`
- [ ] `https://delixioapp.com/about/`
- [ ] `https://delixioapp.com/how-it-works/`
- [ ] `https://delixioapp.com/download/`

## Redirects (recommended)

- [ ] `http://` → `https://delixioapp.com/`
- [ ] `www` → apex `delixioapp.com`
- [ ] `/index.html` and `/*/index.html` → clean trailing-slash directory URLs

See also `docs/SEO_CANONICALIZATION.md`.
