"""Product Owner digital twin — persona, knowledge base, and response engine."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# Persona profile (grounded in Shrirang's CV & certifications)
# ---------------------------------------------------------------------------

PERSONA = {
    "name": "Shrirang Deshpande",
    "title": "Product Owner",
    "tagline": "Telecom BSS · Digital Transformation · 16+ years",
    "linkedin": "https://www.linkedin.com/in/shrirang-deshpande-14870034/",
    "email": "shrirang09@gmail.com",
    "location": "Reading, UK",
    "certifications": [
        "Certified Scrum Product Owner (CSPO)",
        "Certified SAFe 6 POPM",
        "AWS Cloud Practitioner",
    ],
    "domains": [
        "Product Catalog & CPQ",
        "Order Management",
        "Billing & Convergent Charging",
        "TMF620 / TMF671 APIs",
        "Kafka event-driven integration",
        "BSS digital transformations",
    ],
    "operators": ["Major telco clients in North America & Europe"],
}

SAMPLE_QUESTIONS = [
    "How do you prioritise a backlog when stakeholders disagree?",
    "What is a digital twin in telecom OSS?",
    "How would you handle vague requirements from business?",
    "Explain DWDM from a Product Owner perspective.",
    "How do you write good user stories for integration work?",
    "What's your approach to legacy-to-digital migration?",
]

# ---------------------------------------------------------------------------
# Knowledge topics — keyword triggers + PO-style answers
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeTopic:
    id: str
    keywords: list[str]
    weight: int
    response: str


KNOWLEDGE_TOPICS: list[KnowledgeTopic] = [
    KnowledgeTopic(
        id="priority",
        keywords=["priorit", "backlog", "rank", "must have", "mvp", "trade-off", "trade off", "wsjf", "roadmap"],
        weight=3,
        response="""**Recommendation:** Prioritise by **business value × risk reduction**, not loudest voice or easiest build.

**Approach:**
- Score on impact (revenue, customer experience, regulatory, operational risk)
- Categorise: Must / Should / Could — be explicit about what is *out*
- Map dependencies early; a "small" story blocked by integration is not small
- Run a short alignment session with stakeholders — show the trade-offs visually

**Trade-off:** Saying "no" or "later" to good ideas protects delivery of what matters most.

**Next step:** Facilitate a 90-minute prioritisation workshop with a ranked backlog and agreed MVP scope.

*From my experience on global BSS programmes: backlog clarity and stakeholder alignment upfront reduced clarification cycles by ~20%.*""",
    ),
    KnowledgeTopic(
        id="requirements",
        keywords=["requirement", "vague", "unclear", "user story", "acceptance criteria", "elicitation", "discovery"],
        weight=3,
        response="""**Recommendation:** Do not build on vague requirements — the cost shows up in rework, not in workshops.

**Approach:**
- Start with the **problem statement**: who is affected, what breaks today, what success looks like
- Break into scenarios (happy path, exceptions, edge cases)
- Write user stories with testable acceptance criteria — "done" must be unambiguous
- Validate with stakeholders *before* sprint commitment; use prototypes or walkthroughs if needed

**Trade-off:** A few days of discovery saves weeks of rework.

**Next step:** Schedule a discovery session; output = clarified problem + draft stories in Jira with AC.

*I typically achieve ~95% alignment with business objectives before build through structured As-Is / To-Be workshops.*""",
    ),
    KnowledgeTopic(
        id="stakeholder",
        keywords=["stakeholder", "alignment", "conflict", "c-level", "executive", "buy-in", "workshop"],
        weight=3,
        response="""**Recommendation:** Align expectations early — misalignment discovered in UAT is the most expensive kind.

**Approach:**
- Map stakeholders: who decides, who influences, who executes
- Understand each group's priorities and constraints before proposing solutions
- Communicate trade-offs in business language, backed by data where possible
- Present working demos and process designs — visuals beat documents for C-level buy-in

**Trade-off:** More upfront communication slows the start but accelerates delivery.

**Next step:** Schedule a stakeholder alignment session with a one-page decision log.

*I've presented solution designs to C-level stakeholders and acted as liaison across business, engineering, DevOps, QA, and vendors throughout release cycles.*""",
    ),
    KnowledgeTopic(
        id="digital_twin",
        keywords=["digital twin", "inventory", "network model", "topology", "graph", "single source of truth"],
        weight=4,
        response="""**Recommendation:** A telecom digital twin is the **live, connected software model** of the network — not Visio, not Excel.

**Approach:**
- Model objects and **relationships**: Customer → Service → Circuit → Optical Channel → Fibre → Site/Device
- Keep state current (free/used capacity, status, routes) so planning, provisioning, and fault apps trust one source
- Prioritise high-value workflows first: circuit trace, capacity validation, impact analysis
- Design for AI readiness — clean topology and accurate relationships enable automation later

**Trade-off:** Incremental migration via high-value workflows beats big-bang replacement.

**Next step:** Identify the top 3 operational pain points (e.g. failed activations, slow provisioning) and map them to twin capabilities.

*PO lens: I design the **software representation** of the network — translating engineer workflows into data models and features.*""",
    ),
    KnowledgeTopic(
        id="dwdm",
        keywords=["dwdm", "wavelength", "lambda", "optical channel", "multiplex"],
        weight=4,
        response="""**Simple explanation:** DWDM sends multiple data streams over one fibre using different wavelengths (colours of light) — each acts like its own virtual channel without laying new cable.

**Product / OSS relevance:** The inventory system must model optical channels with route, capacity, free/used status, and ROADM dependencies so planners can provision without overbooking.

**PO approach:** I don't configure DWDM hardware — I work with engineers to define how optical channels, wavelength allocation, and capacity appear in the inventory model and provisioning workflows.

**Next step:** Define user stories for "view available optical channels between node A and B" and "validate capacity before design."

*One-liner for interviews: DWDM multiplies fibre capacity cost-efficiently; the twin must track every λ as a manageable inventory object.*""",
    ),
    KnowledgeTopic(
        id="roadm",
        keywords=["roadm", "add drop", "reroute", "optical routing", "dynamic routing"],
        weight=4,
        response="""**Simple explanation:** ROADM lets operators add, drop, or reroute DWDM wavelengths at network nodes **remotely** — without manual fibre patching.

**Product / OSS relevance:** The twin must model ROADM nodes, pass-through vs drop behaviour, routing options, and constraints — enabling questions like *"If link A–B fails, can we reroute via C?"*

**PO approach:** Define requirements for dynamic optical routing in the inventory model; validate with network engineers using real fault scenarios.

**Trade-off:** Modelling routing flexibility is complex upfront but unlocks faster recovery and better fibre utilisation.

**Next step:** Workshop with engineers on top 5 reroute scenarios to drive acceptance criteria.""",
    ),
    KnowledgeTopic(
        id="provisioning",
        keywords=["provision", "activation", "fulfilment", "order to activate", "service design"],
        weight=3,
        response="""**Recommendation:** Provisioning is **design + allocate + validate + activate** — not just "click configure."

**Approach:**
- Trace the E2E flow: BSS order → OSS design → resource allocation (fibre, channels, ports) → network activation → assurance
- The digital twin validates capacity and topology **before** activation — catch overbooking early
- Define stories around auto-validation, consistent channel assignment, and end-to-end resource trace

**Trade-off:** Upfront validation adds latency to design but prevents failed activations in production.

**Next step:** Map your current failure modes (stuck orders, bad inventory) to twin validation rules.

*Common failure chain: Customer service → Circuit → Optical channel → DWDM → ROADM → Fibre — any layer wrong blocks activation.*""",
    ),
    KnowledgeTopic(
        id="bss_oss",
        keywords=["bss", "oss", "tmf", "tmf620", "tmf671", "catalog", "ordering", "billing", "charging", "cpq"],
        weight=3,
        response="""**Recommendation:** BSS and OSS answer different questions — product success requires tracing the **full E2E flow**.

**Approach:**
| Layer | Question | Examples |
|-------|----------|----------|
| **BSS** | What did the customer buy? | Orders, catalog, pricing, billing |
| **OSS** | How is the service delivered? | Inventory, provisioning, fault |
| **Digital Twin** | What is deployed right now? | Live graph of network + relationships |
| **AI** | What should we do next? | Route optimisation, failure prediction |

- Use TMF620 (Product Catalog) and TMF671 (Promotions) as integration anchors where applicable
- Bridge legacy and digital with backward-compatible migration specs — never big-bang without rollback

**Next step:** Draw one order-to-activate swimlane across BSS → OSS → twin → network and identify the weakest handoff.

*14+ years across catalog, ordering, billing, and charging on operator programmes including Vodafone Germany and Comcast.*""",
    ),
    KnowledgeTopic(
        id="integration",
        keywords=["kafka", "api", "rest", "integration", "microservice", "sync", "migration", "legacy"],
        weight=3,
        response="""**Recommendation:** Integration stories need **data contracts, error handling, and idempotency** — not just "system A talks to B."

**Approach:**
- Define entity mapping and transformation rules before build; document in Confluence
- Specify Kafka topics, schemas, and **error-handling protocols** for failed syncs
- Design backward-compatible extensions so legacy and digital can coexist during migration
- Validate with PoC on performance KPIs before committing to production cutover

**Trade-off:** Detailed mapping specs slow initial sprints but prevent production data incidents.

**Next step:** Produce a data mapping spec with field-level rules and a PoC scope for the riskiest integration path.

*I've specified Kafka-based real-time catalog sync and managed phased legacy-to-digital roadmaps with UAT/production cutover criteria.*""",
    ),
    KnowledgeTopic(
        id="agile",
        keywords=["scrum", "safe", "sprint", "agile", "ceremony", "retro", "grooming", "refinement"],
        weight=2,
        response="""**Recommendation:** Agile ceremonies are only valuable when they produce **decisions and ready backlog items**.

**Approach:**
- Backlog refinement: stories meet Definition of Ready (clear AC, dependencies flagged, sized)
- Sprint planning: commit to what the team can finish — protect focus from mid-sprint scope creep
- Reviews: demo to stakeholders; retros: one actionable improvement per sprint
- In SAFe/hybrid models: coordinate cross-team dependencies in PI planning, not in daily stand-ups

**Trade-off:** Strict ready criteria feels slow until you measure rework reduction.

**Next step:** Audit your top 5 backlog items — are they truly ready for development?

*Certified CSPO, SAFe 6 POPM, and PSM I — I operate in Scrum and SAFe delivery environments daily.*""",
    ),
    KnowledgeTopic(
        id="about",
        keywords=["who are you", "about you", "your background", "experience", "introduce", "tell me about"],
        weight=5,
        response=f"""I'm **{PERSONA['name']}** — a **{PERSONA['title']}** with **14+ years** in telecom BSS and digital transformation.

**What I do:**
- Bridge business and engineering on large-scale catalog, ordering, billing, and charging programmes
- Elicit requirements, design processes, write user stories, and drive backlog prioritisation
- Specify integration (REST, Kafka, TMF APIs) and legacy-to-digital migration paths

**Certifications:** {', '.join(PERSONA['certifications'][:3])} (+ AWS Cloud Practitioner)

**Operator experience:** {', '.join(PERSONA['operators'])}

**How I answer:** Structured PO thinking — recommendation, approach, trade-offs, and a concrete next step. Ask me about prioritisation, requirements, BSS/OSS, digital twins, or Agile delivery.

[Connect on LinkedIn]({PERSONA['linkedin']})""",
    ),
]

DEFAULT_RESPONSE = """**Recommendation:** Start by clarifying the **objective** and who the decision affects.

**Approach:**
- Define the problem before jumping to solutions
- Identify MVP scope and what is explicitly out of scope
- Deliver incrementally and validate with stakeholders early

**Trade-off:** Scope vs speed — faster delivery with unclear scope usually costs more later.

**Next step:** Tell me more context — is this about prioritisation, requirements, stakeholders, BSS/OSS, digital twin, or Agile delivery? I can go deeper.

*Try: "How do you prioritise when stakeholders disagree?" or "What is a digital twin in telecom?"*"""

# ---------------------------------------------------------------------------
# Response engine
# ---------------------------------------------------------------------------

def _score_topic(topic: KnowledgeTopic, text: str) -> int:
    lower = text.lower()
    score = 0
    for kw in topic.keywords:
        if kw in lower:
            score += topic.weight
    return score


def get_knowledge_response(prompt: str) -> tuple[str, Optional[str]]:
    """Return (response, matched_topic_id) from knowledge base."""
    scores = [(t, _score_topic(t, prompt)) for t in KNOWLEDGE_TOPICS]
    scores.sort(key=lambda x: x[1], reverse=True)
    best, best_score = scores[0]
    if best_score > 0:
        return best.response, best.id
    return DEFAULT_RESPONSE, None


def _build_system_prompt() -> str:
    certs = ", ".join(PERSONA["certifications"])
    domains = ", ".join(PERSONA["domains"])
    return f"""You are the AI digital twin of {PERSONA['name']}, a {PERSONA['title']} with 14+ years in telecom BSS.

Speak in first person as Shrirang. Be concise, structured, and practical — like an experienced Product Owner in a stakeholder meeting.

Always structure answers with these sections when relevant:
- **Recommendation** (clear PO decision or stance)
- **Approach** (bulleted steps)
- **Trade-off** (what you are choosing not to do, or cost of the choice)
- **Next step** (one concrete action)

Domain expertise: {domains}
Certifications: {certs}
Operators: {', '.join(PERSONA['operators'])}

PO principles:
- Design the software representation of networks/systems, not physical hardware config
- Prioritise business value and risk reduction
- Never proceed on vague requirements
- Bridge business, engineering, and operations
- Use data and demos to align stakeholders

Keep responses under 250 words unless the question needs depth. Do not invent specific project metrics beyond: ~95% pre-build alignment, ~20% fewer clarification cycles, ~30% process efficiency gains on integration programmes.
If asked something outside telecom/product, answer helpfully but briefly and tie back to PO thinking where natural."""


def get_ai_response(prompt: str, history: list[dict]) -> Optional[str]:
    """Call OpenAI if API key is configured; otherwise return None."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        messages = [{"role": "system", "content": _build_system_prompt()}]
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=600,
        )
        return completion.choices[0].message.content
    except Exception:
        return None


def respond(prompt: str, history: list[dict], use_ai: bool = True) -> tuple[str, str]:
    """
    Generate a response. Returns (content, mode) where mode is 'ai' or 'knowledge'.
    Falls back to knowledge base if AI unavailable or fails.
    """
    if use_ai:
        ai_text = get_ai_response(prompt, history)
        if ai_text:
            return ai_text, "ai"

    content, _ = get_knowledge_response(prompt)
    return content, "knowledge"
