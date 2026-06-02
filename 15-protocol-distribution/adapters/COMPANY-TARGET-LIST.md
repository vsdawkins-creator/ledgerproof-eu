# LedgerProof Adapter — 100+ Company Target List

**Drafted**: Tue Jun 2, 2026 — 15:30 PDT
**Goal**: Ship adapter packages for 100+ companies that V wants covered
**Sprint mode**: Phase 1 + Phase 2 already shipped (9 adapters). Batches 1-9 below ship the remaining ~95.

## Shipped (9 adapters, Python)

| # | Package | Company / Framework | Status |
|---|---------|---------------------|--------|
| 1 | ledgerproof-langchain | LangChain Inc. (US, ~$25M Series A) | ✅ shipped |
| 2 | ledgerproof-llamaindex | LlamaIndex Inc. (US) | ✅ shipped |
| 3 | ledgerproof-openai | OpenAI (US) | ✅ shipped |
| 4 | ledgerproof-anthropic | Anthropic (US) | ✅ shipped |
| 5 | ledgerproof-mistral | Mistral AI (French — EU sovereignty) | ✅ shipped |
| 6 | ledgerproof-aleph-alpha | Aleph Alpha (German — EU sovereignty, BaFin-credible) | ✅ shipped |
| 7 | ledgerproof-cohere | Cohere (Canadian — EU-aligned multilingual) | ✅ shipped |
| 8 | ledgerproof-haystack | deepset GmbH (German — enterprise RAG) | ✅ shipped |
| 9 | ledgerproof-semantic-kernel | Microsoft (US — enterprise .NET + Python) | ✅ shipped |

## Batch 1 — LLM Provider SDKs (10 adapters)

| # | Package | Company | Origin |
|---|---------|---------|--------|
| 10 | ledgerproof-google-ai | Google AI / Gemini Python SDK | US (Google) |
| 11 | ledgerproof-vertexai | Google Vertex AI Python SDK | US (Google Cloud) |
| 12 | ledgerproof-bedrock | AWS Bedrock Runtime (boto3) | US (Amazon) |
| 13 | ledgerproof-azure-openai | Azure OpenAI Python SDK | US (Microsoft) |
| 14 | ledgerproof-together | Together.ai Python SDK | US |
| 15 | ledgerproof-groq | Groq Python SDK | US |
| 16 | ledgerproof-huggingface | Hugging Face Inference API + Transformers | French/US |
| 17 | ledgerproof-ai21 | AI21 Studio Python SDK | Israeli |
| 18 | ledgerproof-replicate | Replicate Python SDK | US |
| 19 | ledgerproof-xai | xAI / Grok Python SDK | US |

## Batch 2 — LLM Provider SDKs (10 adapters)

| # | Package | Company | Origin |
|---|---------|---------|--------|
| 20 | ledgerproof-deepseek | DeepSeek Python (OpenAI-compatible API) | Chinese |
| 21 | ledgerproof-qwen | Alibaba Cloud Qwen / Dashscope SDK | Chinese |
| 22 | ledgerproof-reka | Reka AI Python SDK | US |
| 23 | ledgerproof-voyage | Voyage AI Python SDK (embeddings) | US |
| 24 | ledgerproof-cerebras | Cerebras Python SDK | US |
| 25 | ledgerproof-watsonx | IBM watsonx.ai Python SDK | US (IBM) |
| 26 | ledgerproof-snowflake-cortex | Snowflake Cortex (snowflake-snowpark-python) | US |
| 27 | ledgerproof-perplexity | Perplexity AI API (OpenAI-compatible) | US |
| 28 | ledgerproof-fireworks | Fireworks AI Python SDK | US |
| 29 | ledgerproof-mistral-codestral | Mistral Codestral (specialized code endpoint) | French |

## Batch 3 — Orchestration / Agent Frameworks (10 adapters)

| # | Package | Framework | Origin |
|---|---------|-----------|--------|
| 30 | ledgerproof-crewai | CrewAI (multi-agent) | US |
| 31 | ledgerproof-autogen | Microsoft AutoGen (multi-agent) | US (Microsoft Research) |
| 32 | ledgerproof-dspy | Stanford DSPy (prompt programming) | US (Stanford) |
| 33 | ledgerproof-pydantic-ai | Pydantic AI | UK |
| 34 | ledgerproof-mirascope | Mirascope | US |
| 35 | ledgerproof-litellm | LiteLLM (100+ provider proxy) | US |
| 36 | ledgerproof-guidance | Guidance | US |
| 37 | ledgerproof-outlines | Outlines (structured generation) | French |
| 38 | ledgerproof-instructor | Instructor (structured outputs) | US |
| 39 | ledgerproof-marvin | Marvin (PrefectHQ) | US |

## Batch 4 — Orchestration + Dev Tooling (10 adapters)

| # | Package | Framework | Origin |
|---|---------|-----------|--------|
| 40 | ledgerproof-magentic | Magentic | UK |
| 41 | ledgerproof-smolagents | Hugging Face SmolAgents | French/US |
| 42 | ledgerproof-strands | AWS Strands Agents | US |
| 43 | ledgerproof-atomic-agents | Atomic Agents | NL |
| 44 | ledgerproof-agno | Agno (formerly phidata) | US |
| 45 | ledgerproof-claude-agent-sdk | Anthropic Claude Agent SDK | US |
| 46 | ledgerproof-aider | Aider (cli coding agent) | US |
| 47 | ledgerproof-continue | Continue.dev | US |
| 48 | ledgerproof-cody | Sourcegraph Cody | US |
| 49 | ledgerproof-codeium | Codeium / Windsurf | US |

## Batch 5 — Vector DBs / RAG Infrastructure (10 adapters)

| # | Package | DB / Platform | Origin |
|---|---------|---------------|--------|
| 50 | ledgerproof-pinecone | Pinecone | US |
| 51 | ledgerproof-weaviate | Weaviate | NL — EU strategic |
| 52 | ledgerproof-qdrant | Qdrant | German — EU strategic |
| 53 | ledgerproof-chromadb | Chroma | US |
| 54 | ledgerproof-milvus | Milvus / Zilliz | US/Chinese |
| 55 | ledgerproof-lancedb | LanceDB | US |
| 56 | ledgerproof-marqo | Marqo | UK/AU |
| 57 | ledgerproof-elasticsearch | Elastic / Elasticsearch | Dutch (Elastic NV) — EU strategic |
| 58 | ledgerproof-algolia | Algolia | French — EU strategic |
| 59 | ledgerproof-pgvector | pgvector / Postgres | Open-source |

## Batch 6 — AI/ML Platforms (10 adapters)

| # | Package | Platform | Origin |
|---|---------|----------|--------|
| 60 | ledgerproof-databricks | Databricks Mosaic AI / Vector Search | US |
| 61 | ledgerproof-sagemaker | AWS SageMaker | US (AWS) |
| 62 | ledgerproof-azureml | Azure Machine Learning | US (Microsoft) |
| 63 | ledgerproof-mlflow | MLflow (Databricks-stewarded OSS) | US |
| 64 | ledgerproof-wandb | Weights & Biases | US |
| 65 | ledgerproof-comet | Comet ML | US/Israeli |
| 66 | ledgerproof-neptune | Neptune.ai | Polish — EU strategic |
| 67 | ledgerproof-clearml | ClearML | Israeli |
| 68 | ledgerproof-h2o | H2O.ai | US (with strong EU presence) |
| 69 | ledgerproof-anyscale-ray | Anyscale / Ray | US |

## Batch 7 — Inference / Specialized AI Tooling (10 adapters)

| # | Package | Platform | Origin |
|---|---------|----------|--------|
| 70 | ledgerproof-modal | Modal Labs | US |
| 71 | ledgerproof-runpod | Runpod | US |
| 72 | ledgerproof-banana | Banana / Bento | US |
| 73 | ledgerproof-vllm | vLLM (UC Berkeley) | US |
| 74 | ledgerproof-ollama | Ollama (local model server) | US (popular EU dev tool) |
| 75 | ledgerproof-llamacpp-python | llama.cpp Python bindings | OSS |
| 76 | ledgerproof-tabby | Tabby (self-hosted coding) | US |
| 77 | ledgerproof-bolt | StackBlitz Bolt | US |
| 78 | ledgerproof-v0 | Vercel v0 | US |
| 79 | ledgerproof-lovable | Lovable | Swedish — EU strategic |

## Batch 8 — Generative Content / Synthetic Media (10 adapters)

| # | Package | Vendor | Article 50 Surface |
|---|---------|--------|----|
| 80 | ledgerproof-synthesia | Synthesia (UK) — synthetic video | 50(2), 50(4) deepfake |
| 81 | ledgerproof-runway | Runway ML (US) — video generation | 50(2), 50(4) deepfake |
| 82 | ledgerproof-pika | Pika Labs (US) — video generation | 50(2), 50(4) deepfake |
| 83 | ledgerproof-elevenlabs | ElevenLabs (UK/Polish) — voice synthesis | 50(2), 50(4) audio deepfake |
| 84 | ledgerproof-resemble | Resemble AI (Canadian) — voice cloning | 50(2), 50(4) audio deepfake |
| 85 | ledgerproof-playht | PlayHT (US) — voice synthesis | 50(2) synthetic audio |
| 86 | ledgerproof-stability | Stability AI (UK) — image generation | 50(2) synthetic image |
| 87 | ledgerproof-adobe-firefly | Adobe Firefly (US) — multimodal generation | 50(2) synthetic image/video |
| 88 | ledgerproof-leonardo | Leonardo.AI (Australian) — image generation | 50(2) synthetic image |
| 89 | ledgerproof-suno | Suno (US) — music generation | 50(2) synthetic audio |

## Batch 9 — Specialized + Remaining (~10+)

| # | Package | Vendor | Notes |
|---|---------|--------|----|
| 90 | ledgerproof-heygen | HeyGen — synthetic video avatars | 50(2), 50(4) deepfake |
| 91 | ledgerproof-d-id | D-ID — synthetic talking heads | 50(2), 50(4) deepfake |
| 92 | ledgerproof-luma | Luma AI — 3D + video generation | 50(2) |
| 93 | ledgerproof-udio | Udio — music generation | 50(2) synthetic audio |
| 94 | ledgerproof-perplexity-search | Perplexity Search API (with citation) | 50(1) |
| 95 | ledgerproof-you-com | You.com AI search API | 50(1) |
| 96 | ledgerproof-replit-agent | Replit Agent | 50(1) code-gen attribution |
| 97 | ledgerproof-zhipu | Zhipu AI / GLM (Chinese) | 50(1) |
| 98 | ledgerproof-bytedance-doubao | ByteDance Doubao | 50(1) |
| 99 | ledgerproof-naver-hyperclova | Naver HyperCLOVA X (Korean) | 50(1) |
| 100 | ledgerproof-sap-ai-core | SAP AI Core (German — strategic for EU enterprise) | 50(1) |
| 101 | ledgerproof-mistral-le-chat | Mistral Le Chat / Plateforme features | 50(1) |
| 102 | ledgerproof-jasper | Jasper.ai (marketing AI) | 50(2) generated content |
| 103 | ledgerproof-writer | Writer.com (enterprise writing AI) | 50(2) generated content |
| 104 | ledgerproof-copy-ai | Copy.ai (marketing AI) | 50(2) generated content |

## Total at full coverage

**~104 adapter packages**: 9 shipped + 95 batched. Includes the LLM-provider, orchestration, vector-DB, ML-platform, generative-content, and specialized-tool categories.

## Categories with strongest EU strategic alignment

- **EU-native AI providers**: Mistral, Aleph Alpha, SAP AI Core, Mistral Le Chat
- **EU enterprise infrastructure**: Haystack (deepset GmbH), Qdrant (German), Weaviate (NL), Elasticsearch (Elastic NV NL), Algolia (French)
- **EU-aligned dev tools**: Outlines (French), Neptune (Polish), Atomic Agents (NL), Lovable (Swedish)
- **EU customer-facing (UK-based, EU-touch)**: Synthesia, ElevenLabs, Stability

## Discipline for every adapter in this list

- Apache 2.0 license
- Python 3.10+ (TypeScript ports follow in Phase 3 per Full Stack Plan)
- C1/C4/C6/C7 baked in
- ~18-21 file structure (matches existing 9 adapters)
- pip-installable + pytest passing
- README with explicit C1 disclaimer
- Three or more receipt schemas appropriate to the SDK
- Five+ side-channel emitters (Log, Stderr, Webhook, Queue, Multi)
- Ephemeral signer (HSM stubs commented for Phase 4)
- Vendor disclaimer in README: "not endorsed by [vendor]"
