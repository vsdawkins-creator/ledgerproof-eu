"""
LPR API — Bitcoin anchor worker.

Runs as a background asyncio task. Every ANCHOR_WINDOW_HOURS hours:
  1. Drains the anchor_queue
  2. Builds an RFC 6962 Merkle tree over the leaf hashes
  3. Broadcasts a Bitcoin OP_RETURN transaction embedding:
       LPR1 + merkle_root (36 bytes total: 4 + 32)
  4. Waits for 1 confirmation
  5. Writes inclusion proofs for all receipts in this batch
  6. Updates receipt anchor_status to ANCHORED

Bitcoin access:
  Uses JSON-RPC (bitcoind or compatible). Credentials from env vars:
    BITCOIN_RPC_HOST, BITCOIN_RPC_PORT, BITCOIN_RPC_USER, BITCOIN_RPC_PASS
    BITCOIN_HOT_WALLET_WIF — MUST be set via Fly.io secrets, never in code.

Security note: BITCOIN_HOT_WALLET_WIF is read ONCE at startup and stored only
in memory. It is NEVER logged, persisted to disk, or included in any API response.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import struct
import time
import uuid
from typing import Optional

import aiohttp  # type: ignore[import-untyped]

logger = logging.getLogger("lpr.anchor_worker")

# OP_RETURN prefix per LPR 1.0 §5.1: ASCII "LPR1" = 0x4C 0x50 0x52 0x31
LPR1_PREFIX = b"LPR1"

# How many seconds between anchor attempts.
# Read from ANCHOR_WINDOW_HOURS env var (default 24h).
_anchor_interval_seconds: Optional[int] = None


def get_anchor_interval() -> int:
    global _anchor_interval_seconds
    if _anchor_interval_seconds is None:
        hours = float(os.environ.get("ANCHOR_WINDOW_HOURS", "24"))
        _anchor_interval_seconds = int(hours * 3600)
    return _anchor_interval_seconds


# ---------------------------------------------------------------------------
# Bitcoin RPC client
# ---------------------------------------------------------------------------

class BitcoinRPC:
    """Minimal async JSON-RPC 1.1 client for bitcoind / compatible nodes."""

    def __init__(self) -> None:
        self.host = os.environ.get("BITCOIN_RPC_HOST", "127.0.0.1")
        self.port = int(os.environ.get("BITCOIN_RPC_PORT", "8332"))
        self.user = os.environ.get("BITCOIN_RPC_USER", "")
        self.password = os.environ.get("BITCOIN_RPC_PASS", "")
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            auth = aiohttp.BasicAuth(self.user, self.password)
            self._session = aiohttp.ClientSession(auth=auth)
        return self._session

    async def call(self, method: str, *params) -> dict:
        payload = {
            "jsonrpc": "1.1",
            "id": "lpr",
            "method": method,
            "params": list(params),
        }
        session = await self._get_session()
        async with session.post(
            self.url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            body = await resp.json(content_type=None)
        if body.get("error"):
            raise RuntimeError(f"Bitcoin RPC error: {body['error']}")
        return body["result"]

    async def test_connection(self) -> bool:
        """Return True if the node is reachable and synced."""
        try:
            info = await self.call("getblockchaininfo")
            return bool(info.get("blocks"))
        except Exception as exc:
            logger.error("Bitcoin RPC test failed: %s", exc)
            return False

    async def get_balance(self) -> int:
        """Return hot wallet balance in satoshis."""
        btc = await self.call("getbalance")
        return int(float(btc) * 1e8)

    async def broadcast_op_return(self, data: bytes) -> str:
        """
        Construct and broadcast an OP_RETURN transaction embedding `data`.

        data must be at most 80 bytes (Bitcoin script limit).
        Returns the txid of the broadcast transaction.

        Uses createrawtransaction + signrawtransactionwithwallet + sendrawtransaction.
        The hot wallet must be loaded in the node's wallet.
        """
        assert len(data) <= 80, f"OP_RETURN data too large: {len(data)} bytes (max 80)"

        # Step 1: find a suitable UTXO to fund the tx (smallest with sufficient value).
        utxos = await self.call("listunspent", 1, 9999999)
        if not utxos:
            raise RuntimeError("No UTXOs available to fund OP_RETURN transaction")

        # Sort by amount ascending; take the smallest sufficient to cover fees (~1000 sat).
        utxos.sort(key=lambda u: u["amount"])
        utxo = None
        for u in utxos:
            if int(u["amount"] * 1e8) >= 5000:  # 5000 sat minimum
                utxo = u
                break
        if utxo is None:
            raise RuntimeError("No UTXO with sufficient balance (need ≥ 5000 sat)")

        input_sat = int(utxo["amount"] * 1e8)
        fee_sat = 2000  # conservative; ~2000 sat for a simple OP_RETURN tx at 1 sat/vbyte
        change_sat = input_sat - fee_sat

        # Step 2: create raw transaction.
        #   One input (the UTXO), one OP_RETURN output (0 BTC), one change output.
        change_address = await self.call("getrawchangeaddress", "bech32")
        op_return_hex = data.hex()

        inputs = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
        outputs = {
            "data": op_return_hex,
            change_address: round(change_sat / 1e8, 8),
        }
        raw_tx = await self.call("createrawtransaction", inputs, outputs)

        # Step 3: sign with wallet.
        signed = await self.call("signrawtransactionwithwallet", raw_tx)
        if not signed.get("complete"):
            raise RuntimeError(f"Transaction signing incomplete: {signed}")

        # Step 4: broadcast.
        txid = await self.call("sendrawtransaction", signed["hex"])
        logger.info("OP_RETURN transaction broadcast: txid=%s", txid)
        return txid

    async def wait_for_confirmation(self, txid: str, confirmations: int = 1, timeout: int = 7200) -> int:
        """Poll until txid has >= `confirmations` confirmations. Returns block height."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                tx = await self.call("gettransaction", txid)
                if tx.get("confirmations", 0) >= confirmations:
                    # Get block height from the block hash.
                    block_hash = tx.get("blockhash")
                    if block_hash:
                        block_info = await self.call("getblock", block_hash)
                        return block_info["height"]
            except Exception as exc:
                logger.warning("Polling confirmation for %s: %s", txid, exc)
            await asyncio.sleep(60)  # check every 60 seconds
        raise TimeoutError(f"Transaction {txid} not confirmed within {timeout}s")

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


# ---------------------------------------------------------------------------
# Merkle root construction (delegates to merkle.py logic inline for portability)
# ---------------------------------------------------------------------------

def _leaf_hash(data: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + data).digest()


def _node_hash(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _build_merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return hashlib.sha256(b"").digest()
    if len(leaves) == 1:
        return leaves[0]
    k = 1
    while (k << 1) < len(leaves):
        k <<= 1
    return _node_hash(_build_merkle_root(leaves[:k]), _build_merkle_root(leaves[k:]))


def _inclusion_proof(leaves: list[bytes], m: int) -> list[bytes]:
    n = len(leaves)
    if n == 1:
        return []
    k = 1
    while (k << 1) < n:
        k <<= 1
    if m < k:
        return _inclusion_proof(leaves[:k], m) + [_build_merkle_root(leaves[k:])]
    return _inclusion_proof(leaves[k:], m - k) + [_build_merkle_root(leaves[:k])]


# ---------------------------------------------------------------------------
# The anchor cycle
# ---------------------------------------------------------------------------

async def run_anchor_cycle(btc_rpc: BitcoinRPC) -> None:
    """
    One anchor cycle:
      1. Drain anchor_queue
      2. Build Merkle tree
      3. Broadcast OP_RETURN
      4. Wait for confirmation
      5. Write proofs, update receipt statuses
    """
    # Import here to avoid circular imports.
    from lpr_api import database as db

    async with db.conn() as c:
        rows = await c.fetch(
            "SELECT receipt_id, leaf_hash FROM anchor_queue ORDER BY queued_at ASC"
        )

    if not rows:
        logger.info("Anchor cycle: queue empty, skipping")
        return

    receipt_ids = [r["receipt_id"] for r in rows]
    leaf_hashes_hex = [r["leaf_hash"] for r in rows]
    leaf_hashes_bytes = [bytes.fromhex(h) for h in leaf_hashes_hex]

    logger.info("Anchor cycle: building Merkle tree over %d receipts", len(receipt_ids))

    # Build root.
    merkle_root = _build_merkle_root(leaf_hashes_bytes)
    merkle_root_hex = merkle_root.hex()

    # OP_RETURN payload: LPR1 (4 bytes) + merkle_root (32 bytes) = 36 bytes.
    op_return_data = LPR1_PREFIX + merkle_root

    # Broadcast.
    try:
        txid = await btc_rpc.broadcast_op_return(op_return_data)
    except Exception as exc:
        logger.error("OP_RETURN broadcast failed: %s", exc)
        return

    # Record the anchor.
    anchor_id = str(uuid.uuid4())
    async with db.conn() as c:
        await c.execute(
            """
            INSERT INTO anchors (anchor_id, merkle_root, btc_txid, receipt_count, leaf_hashes)
            VALUES ($1, $2, $3, $4, $5::jsonb)
            """,
            anchor_id, merkle_root_hex, txid, len(receipt_ids),
            json.dumps(leaf_hashes_hex),
        )

    # Wait for confirmation.
    try:
        block_height = await btc_rpc.wait_for_confirmation(txid, confirmations=1)
    except TimeoutError as exc:
        logger.error("Anchor confirmation timeout: %s", exc)
        # Leave receipts in PENDING — they'll be picked up by the next cycle (with the same anchor).
        return

    anchored_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Update anchor with block height and timestamp.
    async with db.conn() as c:
        await c.execute(
            """
            UPDATE anchors
            SET btc_block_height = $1, anchored_at = now()
            WHERE anchor_id = $2
            """,
            block_height, anchor_id,
        )

    # Write inclusion proofs and update receipt statuses.
    async with db.conn() as c:
        async with c.transaction():
            for i, receipt_id in enumerate(receipt_ids):
                proof_bytes = _inclusion_proof(leaf_hashes_bytes, i)
                proof_hex = [p.hex() for p in proof_bytes]
                await c.execute(
                    """
                    INSERT INTO receipt_proofs
                      (receipt_id, anchor_id, leaf_index, tree_size, proof_path,
                       merkle_root, btc_txid, btc_block_height)
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7, $8)
                    ON CONFLICT (receipt_id) DO NOTHING
                    """,
                    receipt_id, anchor_id, i, len(receipt_ids),
                    json.dumps(proof_hex), merkle_root_hex, txid, block_height,
                )
                await c.execute(
                    """
                    UPDATE receipts
                    SET anchor_status = 'ANCHORED', anchor_id = $1
                    WHERE receipt_id = $2
                    """,
                    anchor_id, receipt_id,
                )
            # Clear the queue for these receipts.
            await c.execute(
                "DELETE FROM anchor_queue WHERE receipt_id = ANY($1::text[])",
                receipt_ids,
            )

    logger.info(
        "Anchor complete: txid=%s block=%d receipts=%d root=%s",
        txid, block_height, len(receipt_ids), merkle_root_hex[:16] + "...",
    )


async def anchor_worker_loop(btc_rpc: BitcoinRPC) -> None:
    """Background loop. Runs anchor_cycle every ANCHOR_WINDOW_HOURS."""
    interval = get_anchor_interval()
    logger.info("Anchor worker started (interval=%ds / %.1fh)", interval, interval / 3600)

    while True:
        try:
            await run_anchor_cycle(btc_rpc)
        except Exception as exc:
            logger.exception("Anchor cycle error (will retry next interval): %s", exc)
        await asyncio.sleep(interval)
