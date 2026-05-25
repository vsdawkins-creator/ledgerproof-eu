# LPR MCP Interceptor — Reference Implementation of SEP-1763 Receipts

> Open-source reference implementation of an MCP interceptor that emits **LedgerProof Receipts (LPR v1.0)** for every Model Context Protocol tool call. Fills the reserved `signature` field on SEP-1763 validation results that the SEP itself declares as `unimplemented`.
>
> **License:** MIT
> **Status:** Reference implementation, working but not production-hardened. Intended for community comment on SEP-1763.

---

## What this does

When an MCP-enabled agent (Claude Desktop, OpenAI Assistants over MCP, LangGraph + MCP, or any MCP host) makes a `tools/call` request, this interceptor:

1. Captures the canonical request payload (per MCP JSON-RPC 2.0 schema).
2. Captures the corresponding response.
3. Signs both with an Ed25519 key under the operator's control.
4. Produces an **LPR v1.0 receipt** with `authorship.actor_type = AI_MODEL` (or `HYBRID` if a human gated the call).
5. Aggregates receipts in a Merkle tree.
6. Anchors the daily root on Bitcoin via the `api.ledgerproofhq.io/v1/anchor` endpoint.
7. Returns a verifier link for each tool call.

The interceptor runs as a **sidecar HTTP service** that the MCP host invokes as an SEP-1763-compatible interceptor. It does not require any modification to the MCP host or the underlying agent framework.

## Architecture

```
+-----------------+       +-------------------+       +------------------------+
| MCP Host        | ====> | LPR Interceptor   | ====> | LedgerProof Anchor API |
| (Claude Desktop |  HTTP | (this codebase,   |  HTTP | (api.ledgerproofhq.io) |
|  / LangGraph /  |       |  sidecar service) |       +------------------------+
|  Assistants)    |                                                |
+-----------------+                                                v
                                                       +------------------------+
                                                       | Bitcoin mainnet        |
                                                       | (daily OP_RETURN)      |
                                                       +------------------------+
```

## Quick start

```bash
# Install
pip install -r requirements.txt

# Generate an interceptor signing key (one-time)
python -m lpr_interceptor.keygen --output ~/.lpr/interceptor.key

# Run as a sidecar
export LPR_INTERCEPTOR_KEY=~/.lpr/interceptor.key
export LPR_ANCHOR_API=https://api.ledgerproofhq.io
export LPR_ANCHOR_API_KEY=<your LedgerProof API key>
python -m lpr_interceptor.server --port 9090

# Verify a receipt
python -m lpr_interceptor.verify <receipt_id>
```

Then point your MCP host at `http://localhost:9090` as a SEP-1763 interceptor for validation and observability operations on the `tools/call` feature.

## What is in this folder

| File | Role |
|---|---|
| `interceptor.py` | The sidecar HTTP service that implements the SEP-1763 interface |
| `receipt.py` | LPR v1.0 receipt construction (CBOR canonical, Ed25519 signing) |
| `anchor_client.py` | Client for the LedgerProof Anchor API |
| `merkle.py` | RFC 6962 Merkle tree construction (domain-separated) |
| `keygen.py` | Ed25519 key generation utility |
| `verify.py` | Standalone receipt verifier |
| `example_usage.py` | End-to-end demonstration |
| `requirements.txt` | Python dependencies |
| `LICENSE` | MIT |

## How this maps to SEP-1763

SEP-1763 ("Interceptors for Model Context Protocol", draft opened 2025-11-04) defines three operations: validation, mutation, observability. The implementation here implements all three for the `tools/call` feature:

- **Validation.** The interceptor returns `{valid: true, signature: <ed25519>}` populating the SEP-1763-reserved-but-unimplemented `signature` field on the validation result.
- **Mutation.** None. This interceptor does not modify request or response payloads. Mutation is intentionally not exercised to preserve the operator's trust posture.
- **Observability.** Every tool call generates an LPR receipt logged to the configured backend (local SQLite + remote anchor service). The audit log mandated by SEP-1763 §3.4 is satisfied by the LPR receipt chain itself.

This is a **reference** implementation. Productionization for a specific MCP host environment would add: configurable redaction rules (GDPR PII), rate limiting, batch anchoring policies for high-throughput hosts, and pluggable storage backends.

## Why we shipped this

SEP-1763 has been open as a draft proposal since November 4, 2025 with no labeled sponsor. The proposal reserves a `signature` field on the validation result type for "cryptographic verification of validation results at trust boundaries" but explicitly defers implementation to future work. This reference implementation populates that field as a community contribution.

Comments and pull requests on the SEP-1763 thread at `github.com/modelcontextprotocol/modelcontextprotocol/issues/1763` are welcome.

— LedgerProof Foundation (in formation), July 2026
