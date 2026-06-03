import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://docs.ledgerproofhq.io",
  integrations: [
    starlight({
      title: "LedgerProof",
      description: "EU AI Act Article 50 cryptographic transparency receipts.",
      social: {
        github: "https://github.com/vsdawkins-creator/ledgerproof-eu",
      },
      sidebar: [
        {
          label: "Start",
          items: [
            { label: "Your first receipt (5 min)", link: "/start/your-first-receipt/" },
            { label: "Article 50 compliance in 15 min", link: "/start/article-50-in-15-min/" },
            { label: "Verify someone else's receipt", link: "/start/verify-a-receipt/" },
          ],
        },
        {
          label: "How-to",
          items: [
            { label: "Add LPR to LangChain", link: "/how-to/langchain/" },
            { label: "Add LPR to a Next.js app", link: "/how-to/nextjs/" },
            { label: "Add LPR to Cloudflare Workers", link: "/how-to/cloudflare-workers/" },
            { label: "Add LPR to WordPress", link: "/how-to/wordpress/" },
            { label: "Handle GDPR erasure requests", link: "/how-to/gdpr-erasure/" },
            { label: "Rotate your signing key", link: "/how-to/key-rotation/" },
          ],
        },
        {
          label: "Explain",
          items: [
            { label: "What is an LPR receipt?", link: "/explain/what-is-an-lpr-receipt/" },
            { label: "Why Bitcoin anchoring?", link: "/explain/why-bitcoin/" },
            { label: "How EU AI Act Article 50 works", link: "/explain/article-50/" },
            { label: "GDPR and LedgerProof", link: "/explain/gdpr/" },
          ],
        },
        {
          label: "Reference",
          items: [
            { label: "Python SDK", link: "/reference/sdk-python/" },
            { label: "TypeScript SDK", link: "/reference/sdk-typescript/" },
            { label: "REST API", link: "/reference/api/" },
            { label: "LPR v1.1 specification", link: "/reference/lpr-spec/" },
          ],
        },
        {
          label: "For regulators",
          items: [
            { label: "Verify a receipt", link: "/for-regulators/verify-a-receipt/" },
            { label: "Bulk verification API", link: "/for-regulators/bulk-verification/" },
            { label: "Enforcement evidence bundle", link: "/for-regulators/evidence-bundle/" },
          ],
        },
        {
          label: "For lawyers",
          items: [
            { label: "Article 50 overview", link: "/for-lawyers/article-50-overview/" },
            { label: "LPR as evidence", link: "/for-lawyers/lpr-as-evidence/" },
            { label: "GDPR compliance posture", link: "/for-lawyers/gdpr-compliance/" },
          ],
        },
        {
          label: "Security",
          items: [
            { label: "Disclosure policy", link: "/security/disclosure/" },
          ],
        },
      ],
    }),
  ],
});
