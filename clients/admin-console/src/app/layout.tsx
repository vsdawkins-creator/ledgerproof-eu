import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "LedgerProof Admin Console",
  description: "Manage your LedgerProof receipts. Article 50 compliance dashboard.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "ui-sans-serif, system-ui, sans-serif" }}>
        <nav
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "12px 24px",
            borderBottom: "1px solid #e5e7eb",
            background: "#fff",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <strong>LedgerProof</strong>
            <span style={{ color: "#6b7280", fontSize: "13px" }}>Admin Console</span>
          </div>
          <a
            href="https://docs.ledgerproofhq.io"
            target="_blank"
            rel="noopener"
            style={{ color: "#1d4ed8", textDecoration: "none", fontSize: "13px" }}
          >
            Docs →
          </a>
        </nav>
        <main style={{ maxWidth: "1024px", margin: "0 auto", padding: "24px" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
