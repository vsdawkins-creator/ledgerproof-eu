"""Persona definitions aligned to the buyer skills in ~/.claude/skills/.

Each persona has:
- a slug used in CLI + templates
- a target inbox archetype + voice cues
- the skill file it should be pressure-tested against
- the artifacts it expects to receive
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class PersonaSlug(StrEnum):
    GC = "gc"
    CRO_CCO = "cro_cco"
    MLOPS = "mlops"


class Persona(BaseModel):
    slug: PersonaSlug
    title: str
    summary: str
    skill_path: str = Field(description="Filesystem path to the buyer skill markdown")
    email_template: str
    expected_artifacts: tuple[str, ...]
    cap_per_individual: int = 2
    sequence_gap_business_days: int = 7

    def voice_cue(self) -> str:
        return {
            PersonaSlug.GC: "no marketing register; offer a forwardable artifact in paragraph 1",
            PersonaSlug.CRO_CCO: "named exposure + concrete Day-30 deliverable",
            PersonaSlug.MLOPS: "integration shape and SLO numbers before pitch",
        }[self.slug]


PERSONAS: dict[PersonaSlug, Persona] = {
    PersonaSlug.GC: Persona(
        slug=PersonaSlug.GC,
        title="General Counsel",
        summary="Inventory owner; inside lobbyist; upward broker to CEO and Board.",
        skill_path="~/.claude/skills/fortune-500-general-counsel-buyer/SKILL.md",
        email_template="emails/gc.md.j2",
        expected_artifacts=(
            "shadow_ai_inventory_one_pager",
            "compliance_stamp_pdf_design_spec",
            "iso_42001_mapping",
        ),
    ),
    PersonaSlug.CRO_CCO: Persona(
        slug=PersonaSlug.CRO_CCO,
        title="Chief Risk / Compliance Officer",
        summary="Risk posture owner; budget owner; Board-pack producer.",
        skill_path="~/.claude/skills/fortune-500-cro-cco-buyer/SKILL.md",
        email_template="emails/cro_cco.md.j2",
        expected_artifacts=(
            "iso_42001_mapping",
            "fsi_sector_whitepaper",
            "compliance_stamp_pdf_design_spec",
        ),
    ),
    PersonaSlug.MLOPS: Persona(
        slug=PersonaSlug.MLOPS,
        title="Head of MLOps / AI Infrastructure",
        summary="Deployment gatekeeper; SDK integrator; SLO defender.",
        skill_path="~/.claude/skills/fortune-500-mlops-buyer/SKILL.md",
        email_template="emails/mlops.md.j2",
        expected_artifacts=(
            "sdk_quickstart",
            "operator_load_test_summary",
            "cloud_connector_spec",
        ),
    ),
}


def resolve(slug: str | PersonaSlug) -> Persona:
    if isinstance(slug, str):
        slug = PersonaSlug(slug)
    return PERSONAS[slug]
