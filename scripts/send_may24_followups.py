#!/usr/bin/env python3
"""
May 24 follow-up blast — scheduled 9AM PT Sunday May 24, 2026
Sends follow-ups to every contact emailed on May 21.
Recipients in the same language(s) as their original email.
Runs via launchd: ~/Library/LaunchAgents/io.ledgerproofhq.may24followups.plist
"""
import subprocess
import os

DECK = "/Users/veronicadawkins/Documents/LedgerProof-Launch-July6/09-capital/LedgerProof-Ten31-Seed-Deck-v2.pptx"
PROOF = "https://verify.ledgerproofhq.io/r/founding-declaration"
CLOSE = "June 25"
RAISE = "$5M at a $30M post-money SAFE"
SIG = "Veronica S. Dawkins\nFounder & CEO, LedgerProof, Inc.\nveronica@ledgerproofhq.io"
SIG_FR = "Veronica S. Dawkins\nFondatrice & PDG, LedgerProof, Inc.\nveronica@ledgerproofhq.io"
SIG_DE = "Veronica S. Dawkins\nGruenderin & CEO, LedgerProof, Inc.\nveronica@ledgerproofhq.io"

def investor_en(first, days=74):
    return (
        first + ",\n\n"
        "Following up on my email from Thursday.\n\n"
        "EU AI Act Article 50 enforcement is August 2 -- " + str(days) + " days from today. "
        "The banks, insurers, and law firms that need compliant provenance infrastructure are generating "
        "AI-assisted documents right now, without a permanent record of what was produced.\n\n"
        "LedgerProof is that record: a cryptographic receipt anchored to Bitcoin's base layer at creation, "
        "proving exact content and timestamp, permanently. "
        "Live proof from our May 18 launch: " + PROOF + "\n\n"
        "We are closing our " + RAISE + " on " + CLOSE + ". "
        "Deck re-attached. Would 20 minutes work this week?\n\n" + SIG
    )

def strategic_en(first, angle):
    return (
        first + ",\n\n"
        "Following up on my email from Thursday.\n\n"
        + angle + "\n\n"
        "Live proof from our May 18 launch: " + PROOF + "\n\n"
        "Would 30 minutes work this week?\n\n" + SIG
    )

def symposium_en(first, angle):
    return (
        first + ",\n\n"
        "Following up on my email from earlier this week.\n\n"
        + angle + "\n\n"
        "Live proof from our May 18 launch: " + PROOF + "\n\n"
        "Would 20 minutes work this week?\n\n" + SIG
    )

def investor_followup_fr(first):
    return (
        "\n\n--- Version française ci-dessous ---\n\n"
        + first + ",\n\n"
        "Suite à mon email de jeudi.\n\n"
        "L'article 50 de l'IA Act européen entre en vigueur le 2 août -- dans 74 jours. "
        "Les banques, assureurs et cabinets juridiques qui ont besoin d'une infrastructure de provenance "
        "conforme génèrent déjà ces documents aujourd'hui, sans enregistrement permanent de ce qui a été produit.\n\n"
        "LedgerProof est cet enregistrement : un reçu cryptographique ancré sur la base Bitcoin à la création, "
        "prouvant le contenu exact et l'horodatage, de façon permanente. "
        "Preuve en direct : " + PROOF + "\n\n"
        "Levée de 5M$ sur un SAFE post-money de 30M$, clôture le 25 juin. "
        "Deck joint. Trente minutes à votre convenance cette semaine ?\n\n" + SIG_FR
    )

def investor_followup_de(first):
    return (
        "\n\n--- Deutsche Version unten ---\n\n"
        + first + ",\n\n"
        "Nachfolgend zu meiner E-Mail von Donnerstag.\n\n"
        "EU-KI-Gesetz Artikel 50 tritt am 2. August in Kraft -- in 74 Tagen. "
        "Die Banken, Versicherer und Anwaltskanzleien, die eine konforme Provenienz-Infrastruktur benoetigen, "
        "erstellen diese KI-gestuetzten Dokumente bereits heute, ohne permanente Aufzeichnung des Erzeugten.\n\n"
        "LedgerProof ist diese Aufzeichnung: ein kryptografisches Belegdokument, verankert auf der Bitcoin-Basisschicht "
        "bei der Erstellung, das genauen Inhalt und Zeitstempel dauerhaft beweist. "
        "Live-Beweis: " + PROOF + "\n\n"
        "Aufnahme von 5M$ auf einem 30M$ post-money SAFE, Abschluss 25. Juni. "
        "Deck beigefuegt. Waere diese Woche zwanzig Minuten moeglich?\n\n" + SIG_DE
    )

# ── FULL EMAIL LIST ────────────────────────────────────────────────────────────
# Format: (to, subject, body, attach_deck)

EMAILS = []

# ─── BITCOIN / LIGHTNING VCs ──────────────────────────────────────────────────
EMAILS += [
    ("grant@ten31.xyz",
     "Re: LedgerProof -- $5M seed, Bitcoin-anchored provenance for the AI documentary economy",
     investor_en("Grant"), True),

    ("odell@ten31.xyz",
     "Re: LedgerProof Foundation -- open Bitcoin protocol for AI document provenance",
     investor_en("Matt"), True),

    ("lyn@egodeath.capital",
     "Re: LedgerProof -- Bitcoin as documentary trust infrastructure, EU enforcement in 74 days",
     investor_en("Lyn"), True),

    ("preston@theinvestorspodcast.com",
     "Re: LedgerProof -- Bitcoin-anchored provenance, EU enforcement August 2",
     investor_en("Preston"), True),

    ("tyler@utxo.management",
     "Re: LedgerProof -- Bitcoin provenance infrastructure, EU enforcement in 74 days",
     investor_en("Tyler"), True),

    ("alexander@concentric.vc",
     "Re: LedgerProof -- Bitcoin-native documentary provenance, EU enforcement August 2",
     investor_en("Alexander"), True),

    ("hello@btcfrontier.fund",
     "Re: LedgerProof -- Bitcoin-anchored provenance receipts, EU enforcement in 74 days",
     investor_en("Dr. Hsu"), True),

    ("alyse@stillmark.com",
     "Re: LedgerProof -- Bitcoin provenance infrastructure for AI-generated documents",
     investor_en("Alyse"), True),

    ("christopher@tvp.fund",
     "Re: LedgerProof -- Bitcoin-native proof-of-existence for the documentary economy",
     investor_en("Christopher"), True),

    ("contact@fulgur.ventures",
     "Re: LedgerProof -- Bitcoin-anchored provenance for the Lightning economy",
     investor_en("Vitaly"), True),

    ("nic@castleisland.vc",
     "Re: LedgerProof -- Bitcoin-native proof-of-existence for the documentary economy",
     investor_en("Nic"), True),
]

# ─── CYBERSECURITY VCs ────────────────────────────────────────────────────────
EMAILS += [
    ("rob@datatribe.com",
     "Re: LedgerProof -- cryptographic provenance for AI-generated documents",
     investor_en("Rob"), True),

    ("nadav@team8.vc",
     "Re: LedgerProof -- provenance infrastructure for the AI document economy",
     investor_en("Nadav"), True),

    ("ayepez@forgepointcap.com",
     "Re: LedgerProof -- document provenance as a cybersecurity primitive",
     investor_en("Alberto"), True),

    ("raj@shieldcap.com",
     "Re: LedgerProof -- AI document provenance for defense and government workflows",
     investor_en("Raj"), True),

    ("mark@1011.vc",
     "Re: LedgerProof -- document provenance as the next cybersecurity primitive",
     investor_en("Mark"), True),

    ("jay@synventures.com",
     "Re: LedgerProof -- AI document provenance for enterprise security buyers",
     investor_en("Jay"), True),

    ("jake@ballisticventures.com",
     "Re: LedgerProof -- cryptographic provenance as a cybersecurity primitive",
     investor_en("Jake"), True),

    ("dave@nightdragon.com",
     "Re: LedgerProof -- trust infrastructure for the AI-generated documentary economy",
     investor_en("Dave"), True),

    ("greg@crosspointcapital.com",
     "Re: LedgerProof -- trust infrastructure for the AI-generated documentary economy",
     investor_en("Greg"), True),
]

# ─── FINTECH / INSURTECH VCs ─────────────────────────────────────────────────
EMAILS += [
    ("walker@canapi.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated financial documents",
     investor_en("Walker"), True),

    ("nick@qedinvestors.com",
     "Re: LedgerProof -- AI document provenance infrastructure, EU enforcement August 2",
     investor_en("Nick"), True),

    ("hmorris@nyca.com",
     "Re: LedgerProof -- AI document provenance for financial services",
     investor_en("Hans"), True),

    ("djegen@fprimecapital.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated financial documents",
     investor_en("David"), True),

    ("afelesky@p3vc.com",
     "Re: LedgerProof -- AI document provenance infrastructure for financial services",
     investor_en("Adam"), True),

    ("dmiles@manchesterstory.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated insurance documents",
     investor_en("David"), True),

    ("mark.beeston@illuminatefinancial.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated capital markets documents",
     investor_en("Mark"), True),

    ("ruth@foxecapital.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated insurance documents",
     investor_en("Ruth"), True),

    ("brittany@amfamventures.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated insurance documents",
     investor_en("Brittany"), True),

    ("zach@legaltech.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated legal documents",
     investor_en("Zach"), True),

    ("tamara.steffens@thomsonreuters.com",
     "Re: LedgerProof -- provenance infrastructure for AI-generated legal and compliance documents",
     investor_en("Tamara"), True),
]

# ─── EUROPEAN VCs — bilingual ─────────────────────────────────────────────────
EMAILS += [
    ("will@frontline.vc",
     "Re: LedgerProof -- transatlantic B2B infrastructure, EU enforcement in ten weeks",
     investor_en("William"), True),

    ("jan@indexventures.com",
     "Re: LedgerProof -- EU AI Act compliance infrastructure, 73 days to enforcement",
     investor_en("Jan"), True),

    # AXA VP — English + French
    ("francois@axavp.com",
     "Re: LedgerProof -- triple levier pour AVP : investissement, pilotage et distribution",
     investor_en("Francois") + investor_followup_fr("Francois"), True),

    # Earlybird — English + German
    ("andre@earlybird.com",
     "Re: LedgerProof -- EU-KI-Gesetz Compliance-Infrastruktur, bevor der 2. August kommt",
     investor_en("Andre") + investor_followup_de("Andre"), True),

    # Speedinvest — German (their English was already Wave 2; German was the companion follow-up)
    ("stefan.klestil@speedinvest.com",
     "Re: LedgerProof -- zur Ergaenzung meiner gestrigen E-Mail (auf Deutsch)",
     investor_en("Stefan") + investor_followup_de("Stefan"), True),
]

# ─── DEFENSE / GOV ────────────────────────────────────────────────────────────
EMAILS += [
    ("kgray@iqt.org",
     "Re: LedgerProof -- cryptographic provenance for AI-generated national security documents",
     investor_en("Katie"), True),
]

# ─── STRATEGIC PARTNERS (no deck) ─────────────────────────────────────────────
EMAILS += [
    ("mgablenz@munichre.com",
     "Re: LedgerProof provenance receipts + aiSure = the AI content liability underwriting stack",
     strategic_en("Michael",
        "The integration thesis stands: institutions using aiSure coverage anchor their AI-generated "
        "outputs through LedgerProof at issuance. EU AI Act Article 50 enforcement is August 2 -- "
        "74 days. The provenance receipt that enables compliant underwriting needs to be in the stack now."), False),

    ("yang.chen@verisk.com",
     "Re: LedgerProof -- AI document provenance for Verisk's analytics and compliance ecosystem",
     strategic_en("Yang",
        "EU AI Act Article 50 enforcement is August 2 -- 74 days. The AI-assisted reports and "
        "analytics that Verisk's institutional clients produce today will require compliant provenance "
        "records before that date. LedgerProof is the infrastructure layer that makes those records permanent."), False),

    ("christina.kosmowski@moodys.com",
     "Re: LedgerProof -- AI document provenance for Moody's ratings and analytics workflows",
     strategic_en("Christina",
        "EU AI Act Article 50 enforcement is August 2 -- 74 days. The AI-assisted ratings methodologies, "
        "research reports, and compliance documentation that Moody's Analytics produces today will need "
        "compliant provenance records before that date. LedgerProof is that record."), False),

    ("tom.hutton@xlinnovate.com",
     "Re: LedgerProof -- AI document provenance for the XL Catlin insurtech ecosystem",
     strategic_en("Tom",
        "EU AI Act Article 50 enforcement is August 2 -- 74 days. The AI-assisted underwriting decisions "
        "and compliance documentation that XL's portfolio companies and AXA XL itself produce today will "
        "require compliant provenance records before that date."), False),
]

# ─── SYMPOSIUM CONTACTS (no deck) ─────────────────────────────────────────────
EMAILS += [
    ("aaronp@intouchis.com",
     "Re: LedgerProof follow-up -- thank you for intouch|Live",
     symposium_en("Aaron",
        "Thank you again for hosting intouch|Live on May 18. I would welcome a conversation "
        "about how LedgerProof's provenance infrastructure could be relevant to intouch's "
        "insurance carrier and employer clients."), False),

    ("smangioglu@crcgroup.com",
     "Re: LedgerProof follow-up -- AI document provenance for specialty insurance",
     symposium_en("Shaunt",
        "AI-assisted specialty insurance documents -- policy endorsements, coverage analyses, "
        "claims decisions -- are exactly the category where permanent provenance records matter. "
        "When coverage is disputed, the receipt proves what was produced and when."), False),

    ("dominik.cvitanovic@wilsonelser.com",
     "Re: LedgerProof follow-up -- cryptographic provenance for AI-assisted legal documents",
     symposium_en("Dominik",
        "The AI-assisted legal documents your team produces -- briefs, risk analyses, coverage opinions -- "
        "are increasingly subject to authenticity challenges. LedgerProof anchors those documents at creation "
        "with a permanent, court-admissible provenance record."), False),

    ("ross.molina@lewisbrisbois.com",
     "Re: LedgerProof follow-up -- AI document provenance for data privacy practice",
     symposium_en("Ross",
        "Data privacy litigation and regulatory response increasingly turns on AI-generated documentation. "
        "LedgerProof provides the permanent provenance record that makes those documents defensible -- "
        "from the moment they are produced, not after the dispute arises."), False),

    ("paul.kartsonis@bakersman.com",
     "Re: LedgerProof -- qualifying call",
     symposium_en("Paul",
        "I wanted to follow up on my email from Thursday. I would welcome 20 minutes to understand "
        "Bakers Man's current AI document workflow and whether LedgerProof's provenance receipts "
        "address a problem you are already seeing."), False),

    ("jesse.weinstein@threatlocker.com",
     "Re: LedgerProof -- ThreatLocker integration / channel conversation",
     symposium_en("Jesse",
        "ThreatLocker controls what runs. LedgerProof proves what was produced by AI systems and when. "
        "Together, the combination gives enterprise security buyers both execution control and document "
        "provenance in a single workflow. I would welcome a conversation about whether a channel "
        "or integration relationship makes sense."), False),

    ("nahidf@microsoft.com",
     "Re: LedgerProof -- composing with Microsoft AI governance (MSAGT)",
     symposium_en("Nahid",
        "Microsoft Agent Governance Toolkit launched April 2 with a strong story on agent behavior "
        "and policy compliance. The gap in the current stack is permanent, verifiable provenance for "
        "the documents those agents produce. LedgerProof fills that gap. "
        "The two systems compose, not compete."), False),

    ("mbonner@c-wlaw.com",
     "Re: LedgerProof follow-up -- AI document provenance for litigation and insurance defense",
     symposium_en("Michael",
        "The AI-assisted litigation documents and coverage analyses your practice produces "
        "are increasingly subject to authenticity challenges in discovery. LedgerProof anchors "
        "those documents at creation -- permanent, verifiable, and admissible without calling us."), False),

    ("chris.olmsted@ogletreedeakins.com",
     "Re: LedgerProof follow-up -- AI document provenance for employment law practice",
     symposium_en("Christopher",
        "Employment litigation increasingly involves AI-assisted HR and compliance documentation. "
        "LedgerProof anchors those documents at creation with a permanent provenance record -- "
        "proving what the AI produced, when, and that it has not been altered."), False),

    ("debra@bluecapstudio.com",
     "Re: LedgerProof follow-up",
     symposium_en("Debra",
        "I would welcome the chance to understand bluecap studio's current AI content workflow and "
        "whether LedgerProof's provenance receipts address a problem you are already seeing "
        "with clients who need to authenticate AI-generated creative work."), False),

    ("anthony.miller@bbsihq.com",
     "Re: LedgerProof follow-up -- AI document provenance for BBSI and your employer clients",
     symposium_en("Anthony",
        "BBSI's employer clients are generating AI-assisted HR documentation at scale. "
        "The employment disputes that will follow need a permanent record of what was produced and when. "
        "LedgerProof provides that record at per-receipt cost -- no SaaS contract."), False),

    ("Raouia.Makhoul@bbsi.com",
     "Re: LedgerProof follow-up -- permanent provenance for AI-generated HR documents",
     symposium_en("Raouia",
        "AI-generated offer letters, performance documentation, and termination records are the "
        "highest-liability category in HR. LedgerProof anchors each one at creation -- "
        "a permanent, tamper-evident record that proves what the AI actually produced."), False),

    ("pwoo@maryman.com",
     "Re: LedgerProof follow-up -- chain of custody for AI-generated evidence",
     symposium_en("Perry",
        "Chain of custody for AI-generated documents is the gap no current tool closes. "
        "LedgerProof applies the same principle you know from digital forensics: "
        "permanent, unbroken custody from the moment of creation. "
        "I would value your assessment -- and the advisory conversation."), False),

    ("matt@executiveadvisorsgroup.com",
     "Re: LedgerProof follow-up -- two asks, one conversation",
     symposium_en("Matt",
        "The advisory and product conversations I outlined Thursday both stand. "
        "CISOs and GCs at regulated institutions are the buyers we are targeting -- "
        "and EAG's own AI-assisted deliverables are a natural first deployment."), False),

    ("eblack@transunion.com",
     "Re: LedgerProof follow-up -- provenance for incident response documentation",
     symposium_en("Elliot",
        "Breach notifications, IR reports, and regulatory filings are exactly the documents "
        "that end up in litigation and regulatory proceedings. LedgerProof anchors each one "
        "at creation -- permanent proof of what was produced and when, for any regulator or counsel."), False),

    ("mike.b.silverman@gmail.com",
     "Re: LedgerProof follow-up -- financial sector provenance infrastructure",
     symposium_en("Mike",
        "The provenance gap for FS-ISAC member communications and AI-assisted threat intelligence "
        "is exactly the kind of systemic infrastructure problem you spent years working on. "
        "I would value your assessment -- and the advisory conversation."), False),

    ("nicholas.cramer@idx.us",
     "Re: LedgerProof follow-up -- provenance receipts for breach response documentation",
     symposium_en("Nicholas",
        "Breach response documentation -- notification letters, forensic timelines, remediation reports -- "
        "is always subject to later scrutiny. LedgerProof anchors those documents at creation, "
        "giving IDX clients a permanent chain of custody through any regulatory or litigation phase."), False),

    ("christopher.christians@idx.us",
     "Re: LedgerProof + IDX -- a bundled provenance offering for breach response clients",
     symposium_en("Christopher",
        "The bundled offer I described Thursday -- IDX response services plus LedgerProof document provenance "
        "as a service tier -- is a genuine differentiator in procurement. "
        "I would welcome a conversation with your BD team about the structure."), False),

    ("dominique@concentric.ai",
     "Re: LedgerProof x Concentric AI -- a joint story for enterprise AI governance buyers",
     symposium_en("Dominique",
        "Concentric discovers what is sensitive. LedgerProof proves what was produced and when. "
        "The joint story -- discovery plus proof -- is a complete answer to two of the top three "
        "AI governance questions enterprise buyers are hearing from their boards right now. "
        "EU AI Act Article 50 enforcement is August 2."), False),
]

# ── SEND FUNCTION ──────────────────────────────────────────────────────────────
def send(to_addr, subject, body, attach_deck):
    body_file = "/tmp/lp_followup_body.txt"
    with open(body_file, "w", encoding="utf-8") as f:
        f.write(body)
    safe_subj = subject.replace("\\", "\\\\").replace('"', '\\"')
    al = ('make new attachment with properties {file name:(POSIX file "' + DECK + '") as alias}') if attach_deck else ""
    script = (
        'tell application "Mail"\n'
        '  set bodyText to (read POSIX file "' + body_file + '" as text)\n'
        '  set m to make new outgoing message with properties {'
        'subject:"' + safe_subj + '", '
        'content:bodyText, '
        'visible:false}\n'
        '  tell m\n'
        '    make new to recipient with properties {address:"' + to_addr + '"}\n'
        '    set sender to "veronica@ledgerproofhq.io"\n'
        + ('    ' + al + '\n' if al else '') +
        '  end tell\n'
        '  send m\n'
        'end tell'
    )
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    status = "SENT" if result.returncode == 0 else "ERROR"
    print(status + ": " + to_addr + (" -- " + result.stderr.strip() if result.returncode != 0 else ""))
    return result.returncode == 0

# ── RUN ────────────────────────────────────────────────────────────────────────
sent = 0
failed = 0
for to, subj, body, deck in EMAILS:
    if send(to, subj, body, deck):
        sent += 1
    else:
        failed += 1

print("\nMay 24 follow-up blast complete: " + str(sent) + " sent, " + str(failed) + " failed.")
