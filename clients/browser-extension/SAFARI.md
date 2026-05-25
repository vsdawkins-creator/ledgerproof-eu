# Safari port

Safari Web Extensions ship as a macOS or iOS app bundle (.app/.ipa) wrapping
the same web extension assets. The conversion is a one-time setup via Xcode's
`safari-web-extension-converter` tool.

## Convert the Chrome extension to Safari

```bash
# From the repo root, after running the Chrome build:
xcrun safari-web-extension-converter clients/browser-extension/dist \
  --project-location clients/browser-extension/safari-app \
  --app-name "LedgerProof Verifier" \
  --bundle-identifier io.ledgerproofhq.verifier \
  --copy-resources
```

Open the generated Xcode project, build, and submit to the App Store.

## Caveats

- Safari requires macOS native code signing + notarization.
- The Safari extension permissions UI is more conservative than Chrome's.
  Users must explicitly enable the extension per-site after install.
- `chrome.*` namespace is provided via `webextension-polyfill`, which is
  already a dependency.

## Distribution

- iOS: requires an App Store paid developer account.
- macOS: same.
- Open-source distribution: notarize and distribute the .app or .pkg outside
  the App Store. Requires Developer ID Application certificate.

## Status

Phase 1: Chrome + Firefox shipped (this repo).
Phase 2: Safari .app via Xcode (this document).
