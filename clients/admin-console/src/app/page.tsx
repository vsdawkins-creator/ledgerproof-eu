"use client";

import { useEffect, useState } from "react";

interface Entry {
  sequence: number;
  publisher_id: string;
  content_type: string;
  entry_hash: string;
  entry_timestamp: string;
  deleted_at?: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_LEDGERPROOF_API_BASE ?? "https://api-eu.ledgerproofhq.io";

export default function HomePage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/v1/entries?limit=100`);
        if (!res.ok) throw new Error(`API ${res.status}`);
        const data = (await res.json()) as { entries: Entry[] };
        if (!cancelled) setEntries(data.entries ?? []);
      } catch (exc) {
        if (!cancelled) setError((exc as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = entries.filter((e) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      e.publisher_id.toLowerCase().includes(q) ||
      e.entry_hash.toLowerCase().includes(q) ||
      e.content_type.toLowerCase().includes(q)
    );
  });

  return (
    <div>
      <h1 style={{ margin: "0 0 8px", fontSize: "24px" }}>Recent receipts</h1>
      <p style={{ color: "#6b7280", margin: "0 0 16px" }}>
        Live from <code>{API_BASE}</code>. Article 50 compliance records issued by your publisher account.
      </p>

      <input
        type="text"
        placeholder="Filter by publisher, hash, or content type…"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        style={{
          width: "100%",
          padding: "8px 12px",
          border: "1px solid #d1d5db",
          borderRadius: "6px",
          marginBottom: "16px",
          boxSizing: "border-box",
        }}
      />

      {loading && <p>Loading…</p>}
      {error && (
        <p style={{ color: "#dc2626" }}>Error: {error}</p>
      )}

      {!loading && !error && (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ background: "#f9fafb", textAlign: "left" }}>
              <th style={th}>Seq</th>
              <th style={th}>Publisher</th>
              <th style={th}>Content type</th>
              <th style={th}>Hash</th>
              <th style={th}>Issued</th>
              <th style={th}>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((e) => (
              <tr key={e.sequence} style={{ borderBottom: "1px solid #f3f4f6" }}>
                <td style={td}>
                  <a
                    href={`${API_BASE}/v1/verify/${e.sequence}`}
                    target="_blank"
                    rel="noopener"
                    style={{ color: "#1d4ed8" }}
                  >
                    #{e.sequence}
                  </a>
                </td>
                <td style={td}>{e.publisher_id}</td>
                <td style={td}>
                  <code style={{ fontSize: "11px" }}>{e.content_type}</code>
                </td>
                <td style={td}>
                  <code style={{ fontSize: "11px" }}>{e.entry_hash.slice(0, 12)}…</code>
                </td>
                <td style={td}>{new Date(e.entry_timestamp).toLocaleString()}</td>
                <td style={td}>
                  {e.deleted_at ? (
                    <span style={badge("erased")}>Erased</span>
                  ) : (
                    <span style={badge("ok")}>Active</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && filtered.length === 0 && (
        <p style={{ color: "#6b7280", textAlign: "center", padding: "24px" }}>
          No receipts yet. Issue your first one via the SDK or API.
        </p>
      )}
    </div>
  );
}

const th: React.CSSProperties = { padding: "8px 12px", fontWeight: 600, fontSize: "12px" };
const td: React.CSSProperties = { padding: "8px 12px" };
function badge(kind: "ok" | "erased"): React.CSSProperties {
  if (kind === "ok") {
    return {
      display: "inline-block",
      padding: "2px 6px",
      borderRadius: "4px",
      background: "#dcfce7",
      color: "#166534",
      fontSize: "11px",
      fontWeight: 600,
    };
  }
  return {
    display: "inline-block",
    padding: "2px 6px",
    borderRadius: "4px",
    background: "#fef3c7",
    color: "#854d0e",
    fontSize: "11px",
    fontWeight: 600,
  };
}
