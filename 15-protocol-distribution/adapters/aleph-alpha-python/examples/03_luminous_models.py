"""03 — Iterate Luminous models with the @lpr_track decorator.

Shows how to track a thin business function that calls Aleph Alpha's Luminous
family of models. Receipts are written to an in-memory emitter so the example
is fully self-contained and offline-safe.
"""

from __future__ import annotations

import os

from aleph_alpha_client import Client, CompletionRequest, Prompt

from ledgerproof_aleph_alpha import InMemoryEmitter, lpr_track, verify_receipt


SINK = InMemoryEmitter()


def _client() -> Client:
    return Client(
        token=os.environ.get("AA_TOKEN", "dev-token"),
        host=os.environ.get("AA_HOST", "https://api.aleph-alpha.com"),
    )


@lpr_track(
    article="50(2)",
    schema="generated_content/v1",
    model="luminous-base",
    emitter=SINK,
)
def summarise_base(prompt: str) -> str:
    upstream = _client()
    req = CompletionRequest(prompt=Prompt.from_text(prompt), maximum_tokens=64)
    return upstream.complete(req, model="luminous-base").completions[0].completion


@lpr_track(
    article="50(2)",
    schema="generated_content/v1",
    model="luminous-extended",
    emitter=SINK,
)
def summarise_extended(prompt: str) -> str:
    upstream = _client()
    req = CompletionRequest(prompt=Prompt.from_text(prompt), maximum_tokens=96)
    return upstream.complete(req, model="luminous-extended").completions[0].completion


@lpr_track(
    article="50(2)",
    schema="generated_content/v1",
    model="luminous-supreme",
    emitter=SINK,
)
def summarise_supreme(prompt: str) -> str:
    upstream = _client()
    req = CompletionRequest(prompt=Prompt.from_text(prompt), maximum_tokens=128)
    return upstream.complete(req, model="luminous-supreme").completions[0].completion


def main() -> None:
    if not os.environ.get("AA_TOKEN"):
        raise SystemExit("Set AA_TOKEN to run this example.")
    prompt = "Summarise the EU AI Act in one paragraph."
    for fn in (summarise_base, summarise_extended, summarise_supreme):
        print(fn.__name__, "->", fn(prompt))
    print(f"\nEmitted {len(SINK)} receipts:")
    for r in SINK.receipts:
        ok = verify_receipt(r)
        print(f"  model={r['payload']['model']:<24}  verified={ok}")


if __name__ == "__main__":
    main()
