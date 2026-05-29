"""Click-based CLI: `lpr-gtm`."""

from __future__ import annotations

import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from gtm import anchoring, artifacts, rendering, sequences, tracking
from gtm.personas import PersonaSlug, resolve
from gtm.sequences import (
    BRUSSELS,
    INDIVIDUAL_CAP,
    TouchPolicy,
    validate_send_time,
)

console = Console()


@click.group()
def main() -> None:
    """LedgerProof GTM — operationalize the commercial plan."""


# -------- init --------


@main.command()
def init() -> None:
    """Initialize the local tracking database."""
    tracking.init_db()
    console.print("[green]✓[/green] tracking DB initialized")


# -------- accounts --------


@main.group()
def accounts() -> None:
    """Manage target accounts and contacts."""


@accounts.command("import")
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def accounts_import(csv_path: Path) -> None:
    """Import accounts + contacts from a CSV (see examples/seed_accounts.csv)."""
    with tracking.session() as s, csv_path.open() as fh:
        reader = csv.DictReader(fh)
        added_accts = 0
        added_contacts = 0
        for row in reader:
            acct = tracking.find_account(s, row["account"])
            if acct is None:
                acct = tracking.Account(
                    name=row["account"],
                    sector=row["sector"],
                    jurisdiction=row["jurisdiction"],
                    tier=int(row.get("tier") or 1),
                )
                s.add(acct)
                s.commit()
                s.refresh(acct)
                added_accts += 1
            persona = row["persona"]
            existing = tracking.find_contact(s, acct.id, persona)
            if existing is None:
                contact = tracking.Contact(
                    account_id=acct.id,
                    name=row["contact_name"],
                    title=row["contact_title"],
                    persona=persona,
                    email=row["contact_email"],
                    verified=row.get("verified", "false").lower() == "true",
                )
                s.add(contact)
                added_contacts += 1
        s.commit()
    console.print(
        f"[green]✓[/green] imported {added_accts} accounts, {added_contacts} contacts"
    )


@accounts.command("list")
@click.option("--status", default=None, help="filter by status")
def accounts_list(status: str | None) -> None:
    """List tracked accounts."""
    with tracking.session() as s:
        from sqlmodel import select

        q = select(tracking.Account)
        if status:
            q = q.where(tracking.Account.status == status)
        rows = list(s.exec(q).all())

    table = Table(title="Accounts")
    for col in ("Name", "Sector", "Jurisdiction", "Tier", "Status"):
        table.add_column(col)
    for acct in rows:
        table.add_row(acct.name, acct.sector, acct.jurisdiction, str(acct.tier), acct.status)
    console.print(table)


# -------- render --------


@main.command()
@click.option("--account", required=True)
@click.option("--persona", required=True, type=click.Choice([p.value for p in PersonaSlug]))
@click.option("--send-date", required=True, type=click.DateTime(["%Y-%m-%d"]))
@click.option("--output", type=click.Path(path_type=Path), default=None)
def render(
    account: str, persona: str, send_date: datetime, output: Path | None
) -> None:
    """Render a single outbound email for an account + persona."""
    with tracking.session() as s:
        acct = tracking.find_account(s, account)
        if acct is None:
            console.print(f"[red]account not found:[/red] {account}")
            sys.exit(2)
        contact = tracking.find_contact(s, acct.id, persona)
        if contact is None:
            console.print(
                f"[red]no contact for persona {persona} at {account}[/red]"
            )
            sys.exit(2)

    email = rendering.render_email(
        persona=persona,
        account_name=account,
        contact_name=contact.name.split()[0],
        contact_title=contact.title,
        send_date=send_date.date(),
    )

    console.print(f"[bold]Subject:[/bold] {email.subject}")
    console.print(f"[bold]To:[/bold] {contact.name} <{contact.email}>")
    console.print(f"[bold]Send:[/bold] {email.send_date.isoformat()}")
    console.print(f"[bold]Hash:[/bold] {email.body_hash[:16]}…\n")
    console.print(email.body)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            f"To: {contact.email}\nSubject: {email.subject}\n\n{email.body}\n",
            encoding="utf-8",
        )
        console.print(f"[green]✓[/green] wrote {output}")


# -------- wave --------


@main.group()
def wave() -> None:
    """Plan and execute outbound waves."""


@wave.command("plan")
@click.option(
    "--milestone",
    required=True,
    type=click.Choice(["day-30", "day-60", "day-90", "day-120", "day-180"]),
)
@click.option("--output", type=click.Path(path_type=Path), required=True)
@click.option("--asof", type=click.DateTime(["%Y-%m-%d"]), default=None)
def wave_plan(milestone: str, output: Path, asof: datetime | None) -> None:
    """Plan the outbound wave for a milestone. Writes per-touch .eml files."""
    today = (asof.date() if asof else date.today())
    persona_order = [PersonaSlug.GC, PersonaSlug.CRO_CCO, PersonaSlug.MLOPS]

    output.mkdir(parents=True, exist_ok=True)
    planned = 0
    skipped_at_cap = 0
    skipped_window = 0

    with tracking.session() as s:
        from sqlmodel import select

        for acct in s.exec(select(tracking.Account).where(
            tracking.Account.status == tracking.AccountStatus.PROSPECT
        )).all():
            last = tracking.last_touch_to_account(s, acct.id)
            policy = TouchPolicy(
                last_touch=last.when.date() if last else None,
                touches_to_individual=0,
                today=today,
            )

            # Pick persona: GC first; rotate if last touch was within switch window.
            if last is not None and policy.needs_persona_switch():
                used = PersonaSlug(last.persona)
                remaining = [p for p in persona_order if p != used]
                persona = remaining[0]
            else:
                persona = persona_order[0]

            contact = tracking.find_contact(s, acct.id, persona.value)
            if contact is None:
                # try the next persona
                fallback = next(
                    (
                        c
                        for p in persona_order
                        for c in [tracking.find_contact(s, acct.id, p.value)]
                        if c is not None
                    ),
                    None,
                )
                if fallback is None:
                    continue
                contact = fallback
                persona = PersonaSlug(contact.persona)

            # Cap check
            prior = [
                t
                for t in tracking.touches_for_contact(s, contact.id)
            ]
            if len(prior) >= INDIVIDUAL_CAP:
                skipped_at_cap += 1
                continue

            # Schedule into the next send slot from today.
            try:
                slot = sequences.next_send_slot(
                    after=BRUSSELS.localize(datetime.combine(today, datetime.min.time()))
                )
            except sequences.SendWindowError:
                skipped_window += 1
                continue

            email = rendering.render_email(
                persona=persona,
                account_name=acct.name,
                contact_name=contact.name.split()[0],
                contact_title=contact.title,
                send_date=slot.date(),
            )
            eml_path = output / f"{slot.date().isoformat()}_{acct.id:04d}_{persona.value}.eml"
            eml_path.write_text(
                f"To: {contact.email}\n"
                f"Subject: {email.subject}\n"
                f"X-LPR-Milestone: {milestone}\n"
                f"X-LPR-Account: {acct.name}\n"
                f"X-LPR-Persona: {persona.value}\n"
                f"X-LPR-BodyHash: {email.body_hash}\n"
                f"X-LPR-SendAt: {slot.isoformat()}\n\n"
                f"{email.body}\n",
                encoding="utf-8",
            )
            planned += 1

    console.print(
        f"[green]✓[/green] planned {planned}, "
        f"[yellow]capped[/yellow] {skipped_at_cap}, "
        f"[yellow]no slot[/yellow] {skipped_window}"
    )
    console.print(f"   output: {output}")


@wave.command("send")
@click.option("--execute", is_flag=True, help="actually record sends; default is dry-run")
@click.option("--force-send", is_flag=True, help="override send-window policy")
@click.option("--input", "input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
def wave_send(execute: bool, force_send: bool, input_dir: Path) -> None:
    """Send (or dry-run) the planned .eml files in --input."""
    backend = anchoring.default_backend()
    if backend.__class__.__name__ == "MockBackend":
        console.print("[yellow]using MockBackend — no real anchoring[/yellow]")

    sent = 0
    anchored = 0
    now = datetime.now(tz=BRUSSELS)

    with tracking.session() as s:
        for eml in sorted(input_dir.glob("*.eml")):
            headers, _, body = eml.read_text(encoding="utf-8").partition("\n\n")
            meta = dict(
                line.split(": ", 1)
                for line in headers.splitlines()
                if ": " in line
            )
            send_at_str = meta.get("X-LPR-SendAt", "")
            try:
                send_at = datetime.fromisoformat(send_at_str)
            except ValueError:
                console.print(f"[red]bad SendAt header in {eml.name}[/red]")
                continue

            if send_at.tzinfo is None:
                send_at = BRUSSELS.localize(send_at)

            # Only send if the slot is in the past (or now).
            if send_at > now and not force_send:
                continue

            try:
                validate_send_time(send_at, force=force_send)
            except sequences.SendWindowError as e:
                console.print(f"[red]policy violation:[/red] {eml.name}: {e}")
                continue

            account_name = meta["X-LPR-Account"]
            persona = meta["X-LPR-Persona"]
            subject = meta["X-LPR-Subject"] if "X-LPR-Subject" in meta else meta.get("Subject", "")
            body_hash = meta["X-LPR-BodyHash"]

            acct = tracking.find_account(s, account_name)
            contact = tracking.find_contact(s, acct.id, persona)

            handle = backend.issue(
                artifact_slug=f"outbound_email_{persona}",
                body=body,
                article50_subclause=None,
                profile="lpr.v1.2.baseline",
            )
            anchored += 1

            if execute:
                touch = tracking.Touch(
                    account_id=acct.id,
                    contact_id=contact.id,
                    when=send_at,
                    kind=tracking.TouchKind.EMAIL,
                    persona=persona,
                    artifact_slug=f"outbound_email_{persona}",
                    subject=subject,
                    body_hash=body_hash,
                    receipt_id=handle.receipt_id,
                    bitcoin_block=handle.bitcoin_block,
                    outcome=tracking.TouchOutcome.SENT,
                )
                s.add(touch)
                s.commit()
                sent += 1

    console.print(
        f"[green]✓[/green] anchored {anchored}; "
        f"{'recorded ' + str(sent) if execute else 'dry-run only'}"
    )


# -------- artifacts --------


@main.command("build-artifact")
@click.argument(
    "slug",
    type=click.Choice(["shadow_ai_inventory"]),
)
@click.option("--output", type=click.Path(path_type=Path), required=True)
def build_artifact(slug: str, output: Path) -> None:
    """Build a shippable one-pager (HTML + PDF if WeasyPrint is available)."""
    backend = anchoring.default_backend()
    # Render markdown first so the anchored hash covers the canonical content.
    md = rendering.render_one_pager(slug)
    handle = backend.issue(
        artifact_slug=slug,
        body=md,
        article50_subclause=None,
        profile="lpr.v1.2.baseline",
    )
    built = artifacts.build_one_pager(
        slug=slug,
        title="Shadow AI Inventory" if slug == "shadow_ai_inventory" else slug,
        receipt_id=handle.receipt_id,
        output_dir=output,
    )
    console.print(f"[green]✓[/green] HTML: {built.html_path}")
    if built.pdf_path:
        console.print(f"[green]✓[/green] PDF:  {built.pdf_path}")
    else:
        console.print(
            "[yellow]PDF skipped[/yellow] (install WeasyPrint system deps for PDF)"
        )
    console.print(f"[green]✓[/green] anchored: {handle.receipt_id} ({handle.backend})")


# -------- status --------


@main.command("status")
def status() -> None:
    """Print the trailing-30-day outbound status."""
    today = date.today()
    start = today - timedelta(days=30)
    with tracking.session() as s:
        from sqlmodel import select

        touches = list(
            s.exec(
                select(tracking.Touch).where(tracking.Touch.when >= datetime.combine(start, datetime.min.time()))
            ).all()
        )
    table = Table(title=f"Outbound — trailing 30 days from {today.isoformat()}")
    for col in ("Persona", "Sent", "Replied", "Booked", "Declined"):
        table.add_column(col)
    by_persona: dict[str, dict[str, int]] = {}
    for t in touches:
        bucket = by_persona.setdefault(t.persona, {})
        bucket[t.outcome] = bucket.get(t.outcome, 0) + 1
    for persona, buckets in sorted(by_persona.items()):
        table.add_row(
            persona,
            str(buckets.get("sent", 0)),
            str(buckets.get("replied", 0)),
            str(buckets.get("booked", 0)),
            str(buckets.get("declined", 0)),
        )
    console.print(table)


if __name__ == "__main__":
    main()
