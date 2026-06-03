"""
Multilingual Chinese inference example: emit a receipt that records the
zh-CN end-user disclosure (Article 50(1)) alongside the regional endpoint
choice.

Article 50(1) requires deployers to inform natural persons that they are
interacting with an AI system. When the interaction is in Chinese, the
disclosure must also be in Chinese (or in a language the end user
understands). The `multilingual_chinese_inference/v1` schema records the
SHA-256 hash of the disclosure text actually shown to the end user, so that
the deployer can later prove the disclosure was made and what it said.

The attestation block is descriptive deployer-asserted metadata — see the
C1 disclaimer in the README.
"""

from __future__ import annotations

import hashlib
import os

from ledgerproof_qwen import (
    ChineseInferenceAttestation,
    LedgerProofQwen,
    RegulatoryContext,
    StderrEmitter,
)


DISCLOSURE_TEXT_ZH = "此对话由人工智能(AI)系统生成。您正在与一个 AI 系统互动。"


def main() -> None:
    disclosure_hash = hashlib.sha256(DISCLOSURE_TEXT_ZH.encode("utf-8")).hexdigest()

    attestation = ChineseInferenceAttestation(
        chinese_disclosure_shown=True,
        chinese_disclosure_text_hash_sha256_hex=disclosure_hash,
        endpoint_region="singapore",
        avoids_mainland_residency=True,
        provider_legal_entity="Alibaba Cloud (Singapore) Private Limited",
    )

    client = LedgerProofQwen(
        deployer_id="acme-eu-zh-support",
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url="https://dashscope-intl.aliyuncs.com",
        emitter=StderrEmitter(),
        schema="multilingual_chinese_inference/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="zh-CN UI banner shown above chat input on each session.",
        ),
        chinese_inference=attestation,
    )

    response = client.generation.call(
        model="qwen-max",
        messages=[
            {"role": "user", "content": "请用一句话介绍欧盟人工智能法案。"},
        ],
    )

    print("---- Assistant reply ----")
    if response.output.choices:
        print(response.output.choices[0].message.content)
    else:
        print(response.output.text)
    print("---- (Signed receipt with multilingual-Chinese-inference attestation emitted on stderr) ----")


if __name__ == "__main__":
    main()
