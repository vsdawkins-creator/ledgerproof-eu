# LedgerProof Brand System

**Source of truth:** the live site at `https://ledgerproofhq.io` (extracted from CSS variables in the inline `<style>` block).

**Editorial mood:** Serif-headed, navy + mint + warm cream. Feels more like a financial publication or premium institutional brand than a tech startup. NOT generic Tailwind blue. NOT orange. NOT white-background SaaS.

## Color tokens (the canonical palette)

### Surface (warm cream, not white)
| Token | Hex | Use |
|---|---|---|
| `--bg` | `#FAF7F0` | **Page background** — signature warm cream |
| `--bg-alt` | `#F2EEE2` | Alternate section background |
| `--surface` | `#FFFFFF` | True white surfaces (cards, etc.) |
| `--line` | `#E8E2D5` | Subtle borders, dividers |
| `--line-strong` | `#D7CFB8` | Stronger borders |

### Brand — Navy (primary)
| Token | Hex | Use |
|---|---|---|
| `--navy` | `#081424` | **Primary brand — deep, near-black navy.** Headings, logos, primary buttons |
| `--navy-2` | `#0F1E36` | Body ink, navy variant |
| `--navy-3` | `#16294A` | Lighter navy, hover states |

### Brand — Mint (signature accent)
| Token | Hex | Use |
|---|---|---|
| `--mint` | `#20E898` | **Signature accent** — bright mint green |
| `--mint-2` | `#4DEFAB` | Light mint, hover, gradients |
| `--mint-deep` | `#15B380` | Deeper mint, links, success states |
| `--mint-tint` | `rgba(32, 232, 152, 0.10)` | Mint highlight overlay |

### Type colors
| Token | Hex | Use |
|---|---|---|
| `--ink` | `#0F1E36` | Body text (navy) |
| `--ink-soft` | `#2C394D` | Softer text |
| `--muted` | `#5C6B76` | Muted text, captions |
| `--muted-2` | `#8898A4` | Very muted, footer |
| `--bone` | `#F0EFEC` | Bone-colored text on dark |

### State colors (functional, not decorative)
| Token | Hex | Use |
|---|---|---|
| `--amber` | `#B45309` | Warning text |
| `--amber-bg` | `#FFFBEB` | Warning background |
| `--amber-line` | `#FDE68A` | Warning border |
| (error) | `#B91C1C` | Error states |

## Typography

### Display font (headings, marquee text)
```
--display: "Iowan Old Style", "Palatino Linotype", Palatino,
           "Book Antiqua", Georgia, serif;
```
**This is the signature element.** SERIF, not sans. Iowan Old Style is a refined book-publishing typeface. Headings use letter-spacing: -0.02em.

### Body font
```
--sans: -apple-system, BlinkMacSystemFont, "Inter", "Söhne",
        "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```
Inter / Söhne fallback chain — clean, neutral, modern.

### Code/mono
```
--mono: "SF Mono", "JetBrains Mono", "Fira Code", Menlo, Consolas, monospace;
```

## Signature design patterns

### The "btn-primary" look (most iconic)
- Navy background (`#081424`) + mint text (`#20E898`)
- Pill-shaped (`border-radius: 999px`)
- 16pt × 28pt padding
- Bold 600 weight
- Hover: slight upward translation + box-shadow with navy tint

### Card / surface patterns
- White card on cream background (NOT cream on cream)
- Subtle 1pt `--line` border, no shadows
- 4pt mint top-border for emphasis (the "mint card")

### Selection style
`::selection { background: var(--mint); color: var(--navy); }`

### Underlined links
Underline with 1pt thickness, 4pt offset. Hover changes color to `--mint-deep`, NOT navy.

## What NOT to use

- ❌ Generic Tailwind blue (`#1d4ed8`) — that's the internal admin tools, not the brand
- ❌ Orange accents — not in the brand
- ❌ Pure white page background (`#FFFFFF`) — use `#FAF7F0` warm cream
- ❌ Sans-serif headings — use the serif `--display` font for marquee headlines
- ❌ Heavy gradients, shadows, or "tech glow" — the brand is editorial, not Web3-bro

## Rules of thumb

1. **Pages live on cream (`#FAF7F0`)**, not white. White is reserved for cards/surfaces.
2. **Headings are serif (`--display`)**, body is sans (`--sans`). Mixed type system.
3. **Navy + mint is the only color combination that matters.** Everything else is neutral or functional state.
4. **Mint is the punch — use it sparingly.** Underlines, accents, button text on navy, eyebrow labels, success states. Never a wash of mint as background.
5. **The pill is the signature shape.** `border-radius: 999px` on buttons.

## Files using this brand
- Live marketing site: `https://ledgerproofhq.io` (canonical reference)
- Investor deck: `~/Desktop/LedgerProof-PDFs/LedgerProof-Seed-Deck-Stillmark.pdf`
- Article 50 summary: `~/Desktop/LedgerProof-PDFs/LedgerProof-Summary-Article-50.pdf`
- Competitive landscape: `~/Desktop/LedgerProof-PDFs/Article-50-Competitive-Landscape.pdf` *(needs rebuild — current uses wrong palette)*

## Internal admin tools (do NOT match this brand)
The browser extension popup and admin console use Tailwind defaults (`#1d4ed8` blue). Those are utility surfaces, not brand expressions. Don't reverse-engineer the brand from them.
