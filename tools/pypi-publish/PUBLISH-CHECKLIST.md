# LedgerProof — PyPI Bulk Publish Checklist

**Drafted**: Tue Jun 2, 2026
**Scope**: Publish all 29 adapter packages to PyPI under the LedgerProof Foundation account
**Estimated wall-clock**: 90-120 min (first publish takes longer; subsequent updates are minutes)
**Cost**: Free (PyPI is free hosting for open-source packages)

---

## Why this matters

Until these adapters are on PyPI, `pip install ledgerproof-langchain` returns "package not found." That means:
- The /developers/adapters/ site page lies
- The Harrison Chase outreach pitch fails ("here's working code" requires `pip install` to actually work)
- The first developer who hears about LedgerProof and tries to use it bounces immediately
- Every README quickstart is broken from day one

**Distribution converts inventory into reach.** This is the single highest-leverage publishing action available right now.

---

## Step 1 — PyPI account setup (V, ~15 min, one-time)

### 1a. Create PyPI account

If you don't already have one:
1. Go to https://pypi.org/account/register/
2. Email: `foundation@ledgerproof.org` (preferred — Foundation ownership; if that's not yet wired, use `vsdawkins+pypi@gmail.com` and transfer later)
3. Username suggestion: `ledgerproof-foundation` (this becomes visible as the publisher on every package page)
4. Enable 2FA immediately (TOTP via 1Password or Authy)

### 1b. Verify the package names are available

Run this check before doing anything else. If any name is taken, we have to negotiate or rename:

```bash
for pkg in ledgerproof-langchain ledgerproof-llamaindex ledgerproof-openai \
           ledgerproof-anthropic ledgerproof-mistral ledgerproof-aleph-alpha \
           ledgerproof-cohere ledgerproof-haystack ledgerproof-semantic-kernel \
           ledgerproof-google-ai ledgerproof-vertexai ledgerproof-bedrock \
           ledgerproof-azure-openai ledgerproof-together ledgerproof-groq \
           ledgerproof-huggingface ledgerproof-ai21 ledgerproof-replicate \
           ledgerproof-xai ledgerproof-deepseek ledgerproof-qwen \
           ledgerproof-reka ledgerproof-voyage ledgerproof-cerebras \
           ledgerproof-watsonx ledgerproof-snowflake-cortex \
           ledgerproof-perplexity ledgerproof-fireworks \
           ledgerproof-mistral-codestral; do
  echo -n "$pkg: "
  curl -sf "https://pypi.org/pypi/$pkg/json" >/dev/null && echo "TAKEN" || echo "available"
done
```

Expected result: all 29 should be "available." If any are "TAKEN" — flag immediately, V decides whether to rename.

### 1c. Create PyPI API token

1. PyPI > Account Settings > API tokens > Add token
2. Token name: `ledgerproof-foundation-bulk-publish-jun-2026`
3. Scope: **Entire account** (covers all 29 packages without needing one token per package)
4. Copy the token (starts with `pypi-`) — only shown once
5. Save to `~/.pypirc` (chmod 600):

```ini
[pypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZ...   # YOUR ACTUAL TOKEN
```

**The token grants publish access to your entire PyPI account. Treat it like a Foundation root key — never commit, never paste in chat, never put in a Slack message.**

---

## Step 2 — Dry-run build (~10 min)

Run the dry-run first. This builds all 29 wheels + sdists locally without uploading to PyPI:

```bash
cd /Users/veronicadawkins/Documents/LedgerProof-Launch-July6
./tools/pypi-publish/publish-all.sh --dry-run
```

What this does:
- For each adapter, runs `uvx pyproject-build` to produce a wheel (`.whl`) and source distribution (`.tar.gz`)
- Output goes to `tools/pypi-publish/dist/<package-name>/`
- Each build takes ~30-60s; total dry-run is ~15-25 min for all 29
- Full log at `tools/pypi-publish/publish.log`

**Expected outcome**: 29 packages built successfully. If any FAIL, the script reports the failed packages at the end — those need fixing before real publish.

Common build failures and fixes:
| Error | Cause | Fix |
|-------|-------|-----|
| `error: Multiple top-level packages discovered` | setuptools auto-discovery picking up `tests/` | Add `[tool.setuptools.packages.find]` to pyproject.toml limiting to package dir |
| `ModuleNotFoundError: No module named '...'` | Import error in source | Check the file the agent generated, fix import |
| `License file not found` | LICENSE not at expected path | Ensure LICENSE is at adapter root |

---

## Step 3 — Single-package real publish (test the path) (~5 min)

Pick ONE non-critical adapter to publish first as a real-publish test (so we don't burn the LangChain name on a broken upload):

```bash
./tools/pypi-publish/publish-all.sh ledgerproof-voyage
```

After successful publish, verify in a fresh venv:

```bash
python3.11 -m venv /tmp/lpr-pypi-test && \
  /tmp/lpr-pypi-test/bin/pip install ledgerproof-voyage && \
  /tmp/lpr-pypi-test/bin/python -c "import ledgerproof_voyage; print(ledgerproof_voyage.__version__)"
```

Expected: `0.1.0` printed without error.

Also check the PyPI page renders correctly: https://pypi.org/project/ledgerproof-voyage/

Look for:
- README rendered correctly (markdown → HTML)
- License showing as Apache 2.0
- Publisher shows as your Foundation account
- Dependencies listed correctly

If anything looks wrong, fix the pyproject.toml in that adapter, increment to `0.1.1`, and re-publish (PyPI doesn't allow re-uploading the same version).

---

## Step 4 — Bulk real publish (~30-45 min)

When the single-package test confirms the pipeline works:

```bash
./tools/pypi-publish/publish-all.sh
```

This publishes all 29 packages sequentially. Estimated time: 30-45 min (each upload is fast, but build + upload + verify takes ~1-2 min per package).

The script logs successes and failures separately. If any fail, re-run with the specific package name:

```bash
./tools/pypi-publish/publish-all.sh ledgerproof-watsonx
```

---

## Step 5 — Post-publish verification (~10 min)

For each published package, the public page should be live at:
```
https://pypi.org/project/ledgerproof-<name>/
```

Sanity check 5 random adapters by:
1. Open the PyPI page in a browser — confirm README renders
2. Try `pip install <name>` in a fresh venv — confirm it installs
3. Try the import — confirm it works

Also confirm `pip search` finds them (or use https://pypi.org/search/?q=ledgerproof which is the modern equivalent):

```bash
curl -s "https://pypi.org/search/?q=ledgerproof" | grep -o 'ledgerproof-[a-z\-]*' | sort -u
```

Expected: 29 results.

---

## Step 6 — Update site to point at real PyPI URLs (~10 min)

The `/developers/adapters/` page currently has install commands as text. Update those to link to the live PyPI pages:

In `ledgerproof-site/developers/adapters/index.html`, each adapter card should have:
- The install command: `pip install ledgerproof-langchain` (already there)
- A "View on PyPI" link: `https://pypi.org/project/ledgerproof-langchain/`
- A "View on GitHub" link (still pending — see Step 7)

Commit + push the site update. Vercel auto-deploys.

---

## Step 7 — GitHub repo creation (separate but parallel, ~30-60 min)

Each adapter SHOULD eventually live in its own GitHub repo under the Foundation org (`github.com/ledgerproof/<adapter-name>`). The current monorepo structure at `15-protocol-distribution/adapters/<adapter-name>/` works for development but doesn't give the "this is an open-source project" signal a developer expects.

**Two approaches:**

**Option A — Monorepo for now** (faster, easier, defer split):
- Keep all 29 adapters in the `vsdawkins-creator/ledgerproof-eu` monorepo
- Site links go to `https://github.com/vsdawkins-creator/ledgerproof-eu/tree/main/15-protocol-distribution/adapters/<name>`
- Migrate to separate repos in Q3 when there's bandwidth

**Option B — Split now** (more work, signals professionalism):
- Create `github.com/ledgerproof` organization
- For each adapter, `git subtree split` it into its own repo
- Site links go to `https://github.com/ledgerproof/<adapter-name>`
- Each repo gets its own README + LICENSE + CI

**Recommendation**: A for today. B post-launch when DevRel hire onboards (Aug 15 target).

---

## Step 8 — Announce in launch channels (post-launch, Jul 6+)

After Jul 6 public launch:
- LinkedIn post from Veronica's account announcing PyPI availability
- LangChain Discord soft-intro (per the user-outreach plan W1)
- HN submission ("Show HN: LedgerProof Foundation — open Article 50 evidence adapters for LangChain, OpenAI, Anthropic + 26 others")

Do NOT pre-announce before Jul 6. The press kit + Foundation governance need to land together.

---

## Failure modes + recovery

**"All 29 names taken" → unrealistic but possible.** Mitigation: rename to `lpr-langchain`, `lpr-openai`, etc. Or `ledgerproof-foundation-langchain` etc. (longer but unambiguously Foundation-namespaced).

**Token revoked mid-publish.** Run the script again with the same token, only un-published packages re-publish (PyPI rejects re-upload of same version).

**Wheel build fails for some adapter.** Check `tools/pypi-publish/publish.log` for the specific error. Most likely culprit: setuptools package-discovery picking up `tests/` or `egg-info/`. Fix the pyproject.toml `[tool.setuptools.packages.find]` block.

**Account suspended / rate-limited.** PyPI has anti-abuse limits. Spacing publishes 30-60s apart (which the script does naturally) usually avoids triggers. If suspended, contact PyPI support — Foundation governance documents help.

---

## Cost estimate

- PyPI: $0/mo (free open-source hosting)
- V's time today: ~15 min (account setup + token + dry-run watch)
- V's time tomorrow: ~30-45 min (real publish + verify)
- Total budget: ~1 hour Veronica time

**Return: every "pip install" command on the site becomes real. Every README quickstart becomes runnable. The 29 adapters convert from inventory to reach.**

---

## Decision points for V before running

1. **Foundation account email**: `foundation@ledgerproof.org` (if Google Workspace receiving works) or `vsdawkins+pypi@gmail.com` (personal fallback)?
2. **Username on PyPI**: `ledgerproof-foundation` (Foundation-named) or `ledgerproof` (shorter, brand-named)?
3. **Monorepo (A) or split repos (B)** for GitHub layer?
4. **Dry-run today or tomorrow morning?** (Recommend: dry-run today before sleep so any build failures surface; real publish tomorrow morning when fresh.)

Confirm those 4 and I can drive the rest.
