# LedgerProof Browser Extension

Cross-browser (Chrome, Firefox, Safari) verifier for EU AI Act Article 50 receipts.

## What it does

- Visits any HTTPS page.
- Finds elements with `data-lpr-receipt="{sequence}"`.
- Asks the api-eu.ledgerproofhq.io public verifier whether the receipt exists.
- Decorates the element with a small green ✓ badge if verified, an erased
  marker if soft-deleted, or a neutral `?` if unknown.
- Click the toolbar icon to verify any sequence number manually.

## Privacy

- `activeTab` only — does NOT have permission on every page.
- Only network destination: `api-eu.ledgerproofhq.io`.
- No telemetry, no analytics, no history.
- No remote-code execution (CSP `script-src 'self'`).

## Build

```bash
pnpm install
pnpm build         # outputs to dist/ ready for Chrome/Firefox/Safari
```

Load `dist/` as an unpacked extension in Chrome via `chrome://extensions`.

## License

Apache-2.0.
