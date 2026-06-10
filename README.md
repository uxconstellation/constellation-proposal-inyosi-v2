# Inyosi — Website Proposal (GitHub Pages)

A self-contained, single-page proposal site for Inyosi, in the Constellation style with an Inyosi honeycomb motif. No build step — it's plain HTML + inline SVG.

## Files

```
inyosi-proposal/
├── index.html              ← the proposal (everything renders from here)
├── .nojekyll               ← tells GitHub Pages to serve files as-is
├── README.md
└── assets/
    ├── favicon.svg         ← browser tab icon
    ├── inyosi-honeycomb.svg← reusable hero background asset
    └── og-image.svg        ← social-share preview card
```

All visuals are crafted as SVG and embedded inline in `index.html`, so the page renders even if asset paths change. The `assets/` files are the same graphics saved standalone for reuse.

## Deploy to GitHub Pages

1. Create a new **public** repo, e.g. `inyosi-proposal` (don't initialise with a README).
2. Push these files to the `main` branch:
   ```bash
   cd inyosi-proposal
   git init
   git add .
   git commit -m "Inyosi proposal"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/inyosi-proposal.git
   git push -u origin main
   ```
3. In the repo: **Settings → Pages → Source → Deploy from a branch**, select `main` / `/ (root)`, save.
4. Live in ~1–2 minutes at:
   `https://YOUR-USERNAME.github.io/inyosi-proposal/`

## Quick local preview

```bash
cd inyosi-proposal
python -m http.server 5173
# visit http://localhost:5173
```

## Editing notes

- **Prices / care plan:** search `index.html` for `R10,000`, `R32,000`, `R58,000`, `R3,000`.
- **Recipient:** the "Begin engagement" button is a pre-filled email to `erin@inyosi.co.za` (cc `aldo@uxconstellation.com`) — search `mailto:`.
- **Fonts:** Clash Display + Satoshi, loaded from the FontShare CDN.
- **Social preview** uses `assets/og-image.svg`. If you need a PNG for platforms that don't render SVG previews, ask and we'll export one.

---
Prepared by Aldo Calitz · Constellation · uxconstellation.com
