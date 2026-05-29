# TVP — Morning-Of Cheat Sheet
## Wed May 27, 7:30 AM PDT / 9:30 AM CT · 30 min

**Print this. Or one screen. Don't scroll during the call.**

---

## The room
- **Christopher Calicott** — Managing Director, TVP. Bitcoin-native filter, Texas, low patience for blockchain pitches.
- **Aryan Malhotra** — Analyst. He routed you in. He writes the memo. Talk to him too.

## Open with
> "Before I get into specifics — when Aryan forwarded this to you, what was the thing that made you want to take the call?"

Then mirror the answer back in your first 60 seconds.

---

## The pitch in 5 beats (in order)

| # | Beat | One line |
|---|---|---|
| 1 | **Bitcoin-native, not adjacent** | Every receipt is a Bitcoin OP_RETURN tx. No token, no sidechain, no oracle. |
| 2 | **Window is 73 days** | EU AI Act Article 50 enforces Aug 2, 2026. Live anchor since May 18. |
| 3 | **Foundation = moat** | Open protocol + IETF draft + signatory coalition. Private competitors can't catch the spec. |
| 4 | **Revenue is simple** | Per-receipt + membership. Customers don't need to care about Bitcoin. 97% margin at 1M/day. |
| 5 | **The ask** | $5M / $30M post / June 25 close / pro-rata / board observer. |

---

## NEW since deck was written — drop in naturally

- 📜 **IETF draft live yesterday** — `draft-dawkins-scitt-ai-article50-00` on Datatracker
- 📦 **PyPI live this morning** — `pip install ledgerproof` works globally
- 🏦 **Stillmark + Fulgur** — only if asked "who else are you talking to"

---

## Hard Qs — short answers

**OpenTimestamps already does this?**
OTS proves "hash existed before block." LPR is a typed, structured receipt with issuer, jurisdiction, content type, verifier API. Unix timestamp vs ISO 8601 — both tell time, only one is usable in a contract.

**Simple Proof already does Bitcoin doc timestamping?**
Simple Proof is a service. LedgerProof is a protocol. SMTP didn't beat proprietary email by being better email — by being the standard. Simple Proof can become an LPR operator.

**Bitcoin-native or just SaaS on top?**
Protocol = Bitcoin-native (validity from base layer, no intermediary). Business = commercial infra on open protocol. Exactly Voltage's structure on Lightning, or Unchained on Bitcoin.

**OP_RETURN is 80 bytes — where's the doc?**
In the anchor only — Merkle root + "LPR1" prefix = 36 bytes. Full CBOR receipt off-chain in calendar operator network. Identical to RFC 6962 Certificate Transparency.

**What if Bitcoin fees compress?**
Merkle aggregation — 1M receipts/day = 1 tx. Per-receipt fee fractions of a cent at any fee level. Spec also supports multi-substrate fallback profiles by design.

**"Institutional revenue layer" — big claim for seed-stage**
Day 1 claim: working protocol, live verifier, IETF draft, Foundation in formation. Revenue layer is the 5-year build. SWIFT started as messaging, became settlement.

**Why is Article 50 a real catalyst?**
Not new regulation — enforcement of one in force since Aug 2024. Aug 2, 2026 = transparency obligations kick in for AI content. Enterprise legal already asking vendors. Three of nine May 18 symposium contacts asked unprompted.

**Why $30M post?**
Comparables (OTS, Simple Proof, OriginStamp). VeriSign at seed valued on protocol ownership not revenue. Regulatory pull-through changes risk profile. SAFE is ceiling not floor.

**Who else are you talking to?**
Three Bitcoin-native funds reached out same week — TVP, Stillmark, Fulgur. Taking all three. Round can accommodate all three if all three want in. Not running an auction — running parallel evaluations because the signal is genuine. Stop there.

---

## Numbers — say these without hesitating

| What | Number |
|---|---|
| Raise | **$5M** |
| Post-money | **$30M** SAFE |
| Close | **June 25, 2026** |
| Launch | **July 6, 2026** |
| Article 50 enforcement | **Aug 2, 2026** (73 days) |
| Margin at 1M/day | **97%** |
| Per-receipt Bitcoin fee at batched scale | **~$0.0003** |
| LPR1 prefix size in OP_RETURN | **4 bytes** + 32-byte Merkle root |
| Live anchor since | **May 18, 2026** |
| OP_RETURN txid (first anchor) | `5db5c68e…` *(confirm full txid before call)* |

---

## TVP portfolio — name-drop when relevant

| Portfolio co | When to mention |
|---|---|
| **Impervious** | Standards-body work, IETF parallel — closest structural comp |
| **Voltage** | "Infrastructure business on top of Lightning" — same model on top of Bitcoin |
| **Unchained** | Institutional customer segment, custody for the operator key |
| **Galoy** | Foundation + commercial-entity dual structure precedent |
| **Fedi / Fedimint** | Federated operator network model |

---

## Browser tabs to have open

1. https://verify.ledgerproofhq.io/r/founding-declaration
2. https://pypi.org/project/ledgerproof/
3. https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/
4. https://www.npmjs.com/package/@ledgerproof/sdk

## Local files

- LPR 1.0 spec: `04-lpr-spec/`
- SAFE doc: `09-capital/safe-template.pdf`
- Data room link: ready to paste in chat

---

## At minute 25 — closing move

> "Christopher, I'm closing June 25. I have a board observer seat available and pro-rata on the round. If you're a yes, the right next step is I send you the SAFE and data room access today. If you want a week to look at the spec and the IETF draft first, I can do that — but I want to make sure you have what you need to move at the pace the timeline requires."

**Do not say "let me know if you have questions."** Name the next step. Name the date.

---

## After the call

| Within | Action |
|---|---|
| 5 min | Drink water. Write down everything Christopher said you missed. |
| 60 min | Send SAFE + data room link if he's a yes |
| Same day | Thank-you email to Aryan separately |
| 24 hr | 3-paragraph follow-up: (1) what you heard he cared about, (2) concrete next step, (3) timeline |
| 4 PM PDT same day | Stillmark call — different framing, different room, but same shipped reality |

---

## One thing to remember

You shipped. The protocol is live. The IETF draft is in. PyPI is published. Three of the best Bitcoin-native funds in the world reached out the same week without you running a process.

**You are not asking for permission.** You are running the round on your timeline. Christopher either moves at that pace or he doesn't.

Walk in like that's true. Because it is.

---

*Refreshed May 26, 2026 · Print one-page · No scrolling during the call*
