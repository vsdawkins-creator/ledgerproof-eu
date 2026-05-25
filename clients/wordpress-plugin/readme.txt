=== LedgerProof ===
Contributors: ledgerproofhq
Tags: ai, eu-ai-act, article-50, compliance, provenance
Requires at least: 6.0
Tested up to: 6.5
Requires PHP: 7.4
Stable tag: 1.0.0
License: Apache-2.0
License URI: https://www.apache.org/licenses/LICENSE-2.0

EU AI Act Article 50 compliance for WordPress. Auto-issues an LPR receipt when you publish AI-assisted content.

== Description ==

When the EU AI Act takes effect on August 2, 2026, Article 50 will require disclosure for AI-generated text published "for matters of public interest." This plugin makes compliance one click — flag a post as AI-assisted (via category or custom field), publish, and a cryptographic receipt anchored to Bitcoin is automatically issued via api-eu.ledgerproofhq.io.

== Installation ==

1. Upload `ledgerproof/` to `/wp-content/plugins/`.
2. Activate via the Plugins menu.
3. Settings → LedgerProof: enter your API key, publisher ID, deployer country, and deployer name.
4. Flag posts as AI-assisted via the "AI-Generated" category or the `ledgerproof_ai_assisted` post meta.

== Frequently Asked Questions ==

= How is my content protected? =
Only the SHA-256 hash of your content is sent to LedgerProof — the content itself stays on your server.

= What happens if LedgerProof is unreachable? =
The plugin fails open: your post publishes normally, the error is logged, no receipt is issued.

== Changelog ==

= 1.0.0 =
Initial release. Article 50(4) compliance for AI-assisted posts.
