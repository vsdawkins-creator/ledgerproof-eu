#!/usr/bin/env bash
# LedgerProof — bulk PyPI publish for all 29 adapters.
#
# PREREQUISITES (V handles these manually first — see PUBLISH-CHECKLIST.md):
#   1. PyPI account at https://pypi.org under foundation@ledgerproof.org (or vsdawkins+pypi@gmail.com if needed)
#   2. API token created (PyPI > Account Settings > API tokens > Add token > Scope: Entire account)
#   3. Token saved to ~/.pypirc:
#        [pypi]
#        username = __token__
#        password = pypi-AgENdGVzdC5weXBpLm9yZ...  (your actual token)
#   4. Foundation org/namespace verification on PyPI (optional but recommended pre-publish)
#   5. Each package name verified-available via: pip index versions <name>
#
# DRY RUN: $ ./publish-all.sh --dry-run  (builds wheels but does NOT upload)
# REAL PUBLISH: $ ./publish-all.sh
# SINGLE: $ ./publish-all.sh ledgerproof-langchain

set -euo pipefail

ADAPTERS_DIR="/Users/veronicadawkins/Documents/LedgerProof-Launch-July6/15-protocol-distribution/adapters"
DIST_DIR="/Users/veronicadawkins/Documents/LedgerProof-Launch-July6/tools/pypi-publish/dist"
LOG="/Users/veronicadawkins/Documents/LedgerProof-Launch-July6/tools/pypi-publish/publish.log"

DRY_RUN=false
SINGLE=""
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then DRY_RUN=true; fi
  if [[ "$arg" != --* ]]; then SINGLE="$arg"; fi
done

ALL_ADAPTERS=(
  "langchain-python:ledgerproof-langchain"
  "llamaindex-python:ledgerproof-llamaindex"
  "openai-python:ledgerproof-openai"
  "anthropic-python:ledgerproof-anthropic"
  "mistral-python:ledgerproof-mistral"
  "aleph-alpha-python:ledgerproof-aleph-alpha"
  "cohere-python:ledgerproof-cohere"
  "haystack-python:ledgerproof-haystack"
  "semantic-kernel-python:ledgerproof-semantic-kernel"
  "google-ai-python:ledgerproof-google-ai"
  "vertexai-python:ledgerproof-vertexai"
  "bedrock-python:ledgerproof-bedrock"
  "azure-openai-python:ledgerproof-azure-openai"
  "together-python:ledgerproof-together"
  "groq-python:ledgerproof-groq"
  "huggingface-python:ledgerproof-huggingface"
  "ai21-python:ledgerproof-ai21"
  "replicate-python:ledgerproof-replicate"
  "xai-python:ledgerproof-xai"
  "deepseek-python:ledgerproof-deepseek"
  "qwen-python:ledgerproof-qwen"
  "reka-python:ledgerproof-reka"
  "voyage-python:ledgerproof-voyage"
  "cerebras-python:ledgerproof-cerebras"
  "watsonx-python:ledgerproof-watsonx"
  "snowflake-cortex-python:ledgerproof-snowflake-cortex"
  "perplexity-python:ledgerproof-perplexity"
  "fireworks-python:ledgerproof-fireworks"
  "mistral-codestral-python:ledgerproof-mistral-codestral"
)

mkdir -p "$DIST_DIR"
> "$LOG"

echo "=== LedgerProof Foundation — PyPI Publish ===" | tee -a "$LOG"
echo "Mode: $([ "$DRY_RUN" = true ] && echo DRY-RUN || echo PUBLISH)" | tee -a "$LOG"
echo "Single: ${SINGLE:-ALL}" | tee -a "$LOG"
echo "" | tee -a "$LOG"

failed=()
succeeded=()
skipped=()

for entry in "${ALL_ADAPTERS[@]}"; do
  dir_name="${entry%%:*}"
  pkg_name="${entry##*:}"

  if [[ -n "$SINGLE" && "$SINGLE" != "$pkg_name" && "$SINGLE" != "$dir_name" ]]; then
    continue
  fi

  echo "--- $pkg_name ($dir_name) ---" | tee -a "$LOG"
  ADAPTER_PATH="$ADAPTERS_DIR/$dir_name"

  if [[ ! -d "$ADAPTER_PATH" ]]; then
    echo "  SKIP: directory missing" | tee -a "$LOG"
    skipped+=("$pkg_name (missing)")
    continue
  fi

  # Build sdist + wheel
  echo "  Building..." | tee -a "$LOG"
  if uvx --from build pyproject-build --outdir "$DIST_DIR/$pkg_name" "$ADAPTER_PATH" >> "$LOG" 2>&1; then
    echo "  ✓ Built OK" | tee -a "$LOG"
  else
    echo "  ✗ Build FAILED — see $LOG" | tee -a "$LOG"
    failed+=("$pkg_name (build)")
    continue
  fi

  if [[ "$DRY_RUN" == true ]]; then
    echo "  (dry-run, not uploading)" | tee -a "$LOG"
    succeeded+=("$pkg_name (built)")
  else
    echo "  Uploading to PyPI..." | tee -a "$LOG"
    if uvx --from twine twine upload "$DIST_DIR/$pkg_name"/* >> "$LOG" 2>&1; then
      echo "  ✓ Published to PyPI" | tee -a "$LOG"
      succeeded+=("$pkg_name")
    else
      echo "  ✗ Upload FAILED — see $LOG" | tee -a "$LOG"
      failed+=("$pkg_name (upload)")
    fi
  fi
done

echo "" | tee -a "$LOG"
echo "=== Summary ===" | tee -a "$LOG"
echo "Succeeded: ${#succeeded[@]}" | tee -a "$LOG"
printf '  %s\n' "${succeeded[@]}" | tee -a "$LOG"
echo "Failed: ${#failed[@]:-0}" | tee -a "$LOG"
[[ ${#failed[@]:-0} -gt 0 ]] && printf '  %s\n' "${failed[@]}" | tee -a "$LOG"
[[ ${#skipped[@]:-0} -gt 0 ]] && { echo "Skipped: ${#skipped[@]}" | tee -a "$LOG"; printf '  %s\n' "${skipped[@]}" | tee -a "$LOG"; }
echo "" | tee -a "$LOG"
echo "Full log: $LOG" | tee -a "$LOG"
