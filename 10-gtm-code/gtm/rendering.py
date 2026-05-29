"""Jinja-based rendering for outbound artifacts.

Templates live in gtm/templates/. Every render passes through:
1. Jinja2 strict rendering (undefined variables fail loudly)
2. Brand voice validation (forbidden phrases rejected)
3. PII rejection (emails forbidden in policy-protected fields)
4. SHA-256 hashing of the canonical body (used as anchor input)

Output is a RenderedArtifact: body + subject + canonical hash + metadata.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from importlib.resources import files
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateNotFound,
    select_autoescape,
)

from gtm import brand
from gtm.personas import Persona, PersonaSlug, resolve


TEMPLATE_ROOT = Path(__file__).parent / "templates"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_ROOT)),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


@dataclass(frozen=True)
class RenderedEmail:
    persona: PersonaSlug
    account_name: str
    contact_name: str
    subject: str
    body: str
    body_hash: str
    send_date: date
    article50_subclause: str | None
    artifact_slug: str


SUBJECT_RE = re.compile(r"^Subject:\s*(.+)$", re.MULTILINE)


def render_email(
    *,
    persona: PersonaSlug | str,
    account_name: str,
    contact_name: str,
    contact_title: str,
    send_date: date,
    extra_context: dict | None = None,
) -> RenderedEmail:
    persona_obj: Persona = resolve(persona)
    env = _env()
    try:
        tmpl = env.get_template(persona_obj.email_template)
    except TemplateNotFound as e:
        raise FileNotFoundError(
            f"template missing: {persona_obj.email_template}"
        ) from e

    context = {
        "account_name": account_name,
        "contact_name": contact_name,
        "contact_title": contact_title,
        "send_date": send_date,
        "brand": brand,
        "days_to_enforcement": (date(2026, 8, 2) - send_date).days,
        **(extra_context or {}),
    }
    rendered = tmpl.render(**context)
    brand.validate_copy(rendered)

    subject_match = SUBJECT_RE.search(rendered)
    if not subject_match:
        raise ValueError("template did not produce a Subject: line")
    subject = subject_match.group(1).strip()
    body = SUBJECT_RE.sub("", rendered, count=1).strip()

    canonical = f"{subject}\n\n{body}".encode("utf-8")
    body_hash = hashlib.sha256(canonical).hexdigest()

    article50 = {
        PersonaSlug.GC: None,
        PersonaSlug.CRO_CCO: None,
        PersonaSlug.MLOPS: "50(4)",
    }[persona_obj.slug]

    return RenderedEmail(
        persona=persona_obj.slug,
        account_name=account_name,
        contact_name=contact_name,
        subject=subject,
        body=body,
        body_hash=body_hash,
        send_date=send_date,
        article50_subclause=article50,
        artifact_slug=f"outbound_email_{persona_obj.slug.value}",
    )


def render_one_pager(slug: str, context: dict | None = None) -> str:
    """Render a one-pager Markdown artifact (Shadow AI Inventory, etc.)."""
    env = _env()
    tmpl = env.get_template(f"one_pagers/{slug}.md.j2")
    rendered = tmpl.render(brand=brand, **(context or {}))
    brand.validate_copy(rendered)
    return rendered
