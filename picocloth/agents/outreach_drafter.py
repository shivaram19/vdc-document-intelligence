#!/usr/bin/env python3
"""
outreach_drafter.py — Personalized Outreach Message Drafter

Uses LLM + structured research data to draft context-aware messages.
Each message references a specific project, role, or pain point.

RESEARCH BASIS:
- [CITE: Gracker2025] Gracker.ai analysis (20M+ outreach attempts). Personalized outreach outperforms templated by 3x. https://gracker.ai/blog/increase-linkedin-acceptance-rate
- [CITE: MEDHA_OUTREACH_STRATEGY] JTBD-aligned messages focus on outcomes, not features.
- [CITE: Cialdini1984] Social proof: referencing similar firms increases response rates.

SRP: ONLY drafts messages. No sending, no tracking.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from vdc_core import llm_generate


def draft_message(target: dict, sender_name: str = "Medha Team") -> dict:
    """Draft a personalized outreach message for a target company."""
    contacts = target.get("contacts", [])
    primary_contact = contacts[0] if contacts else {"role": "VDC Manager", "name": "Team"}

    prompt = f"""You are a senior B2B sales development representative for Medha, a construction document intelligence platform.

TARGET COMPANY: {target['name']}
LOCATION: {target['location']}
TARGET ROLE: {primary_contact['role']}
COMPANY PAIN POINT: {target['pain']}

DRAFT A LINKEDIN CONNECTION REQUEST (300 characters max) AND A FOLLOW-UP EMAIL (150 words max).

RULES:
1. Reference a SPECIFIC project, location, or industry context
2. Ask ONE specific question about their pain point
3. Mention a SPECIFIC outcome (time saved, risk reduced)
4. End with a LOW-FRICTION CTA (10-min conversation, not a demo)
5. NO generic "I hope this email finds you well"
6. NEVER use these forbidden words: AI, RAG, embeddings, LLM, machine learning, neural network, vector database, generative AI, artificial intelligence, GPT, Claude, copilot, agentic. Not even once. Not in quotes. Not in parentheses.
7. YES to outcomes ("catch contradictions before $50K rework")

OUTPUT JSON:
{{"linkedin": "...", "email_subject": "...", "email_body": "...", "why_this_works": "..."}}
"""

    import re
    FORBIDDEN = ["ai", "rag", "embeddings", "llm", "machine learning", "neural network",
                 "vector database", "generative ai", "artificial intelligence", "gpt",
                 "claude", "copilot", "agentic"]

    def sanitize(text: str) -> str:
        lowered = text.lower()
        for word in FORBIDDEN:
            # Word-boundary match to avoid false positives (e.g., "India", "email", "detail")
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, lowered):
                raise ValueError(f"Contains forbidden feature word: '{word}'")
        return text

    try:
        raw = llm_generate(prompt, max_tokens=800)
        # Extract JSON from markdown fences if present
        text = raw.get("answer", raw) if isinstance(raw, dict) else raw
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        drafted = json.loads(text)
        # Post-process sanitization: catch any forbidden words LLM slipped in
        sanitize(drafted.get("linkedin", ""))
        sanitize(drafted.get("email_body", ""))
        sanitize(drafted.get("email_subject", ""))
    except Exception as e:
        # Fallback to template if LLM fails or injects forbidden words
        drafted = {
            "linkedin": fallback_linkedin(target, primary_contact),
            "email_subject": f"{target['name']} + spec lookup time",
            "email_body": fallback_email(target, primary_contact, sender_name),
            "why_this_works": f"References {target['name']}'s specific pain: {target['pain'][:80]}... (Fallback after: {str(e)[:60]})",
        }

    return {
        "target": target["name"],
        "contact": primary_contact,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **drafted,
    }


def fallback_linkedin(target: dict, contact: dict) -> str:
    return (
        f"Hi [Name], saw {target['name']}'s work in {target['location'].split(',')[0]}. "
        f"Quick question: how does your {contact['role']} handle spec lookups when the model doesn't have the answer? "
        f"We built something that finds answers in 10 sec across 10,000 pages. Worth connecting?"
    )[:300]


def fallback_email(target: dict, contact: dict, sender: str) -> str:
    return (
        f"Hi [Name],\n\n"
        f"I saw {target['name']}'s projects in {target['location']}. Impressive scale.\n\n"
        f"Quick question: When your {contact['role']} gets asked for a spec clarification during a pour — "
        f"how long does it take to find the answer across all documents?\n\n"
        f"Most teams we speak to say 15–45 minutes of hunting through PDFs, emails, and shared drives.\n\n"
        f"We built Medha to cut that to under 10 seconds — and catch contradictions automatically before they become RFIs.\n\n"
        f"Worth a 10-minute conversation?\n\n"
        f"{sender}\n"
        f"Medha — Document Intelligence for VDC Teams"
    )


def batch_draft(targets: list, sender_name: str = "Medha Team") -> list:
    """Draft messages for multiple targets."""
    results = []
    for t in targets:
        results.append(draft_message(t, sender_name))
    return results


if __name__ == "__main__":
    # Demo: draft for Turner Construction
    demo_target = {
        "name": "Turner Construction",
        "location": "New York, US",
        "contacts": [{"role": "VDC Regional Manager", "name": "Gary Chapman"}],
        "pain": "10+ megaprojects simultaneously. Document review is manual despite having BIM models.",
    }
    result = draft_message(demo_target)
    print(json.dumps(result, indent=2))
