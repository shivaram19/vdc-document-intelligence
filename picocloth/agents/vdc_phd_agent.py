#!/usr/bin/env python3
"""
vdc_phd_agent.py — PhD-Level VDC Agent with Curiosity & Memory Retrieval Traits

Two of these agents interrogate each other on construction documents.
They behave like VDC PhDs who live and breathe specs/drawings daily:
- They ask deep, probing questions that expose gaps
- They cross-reference across disciplines
- They catch subtle contradictions and code compliance issues
- They demand specific citations (document name, section, page)

Traits:
  curiosity        — generates probing questions, detects knowledge gaps
  memory_retrieval — accesses shared embeddings, cross-references history
"""

import json
import re
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent))
from vdc_core import (
    load_embeddings, encode, cosine_similarity, detect_contradictions,
    synthesize_answer, llm_generate, append_event, audit,
    CHUNKS_DIR, EMB_DIR, SHARED_DIR, DOCS_DIR,
)

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------
@dataclass
class Question:
    text: str
    category: str
    expected_depth: int  # 1=fact, 2=analysis, 3=synthesis, 4=critique
    target_doc_hint: str = ""
    asked_by: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Answer:
    text: str
    sources: List[dict]
    contradictions_found: List[dict]
    confidence: float
    answered_by: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Critique:
    score: float  # 0-100
    strengths: List[str]
    weaknesses: List[str]
    missing_citations: List[str]
    suggested_followups: List[str]
    critique_by: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Curiosity Trait — Generates PhD-level probing questions
# ---------------------------------------------------------------------------
CURIOSITY_PROMPT = """You are a PhD-level VDC (Virtual Design & Construction) researcher examining construction documents.
Your job is to ask ONE deeply probing question that would challenge even an experienced VDC manager.

Documents available:
{doc_list}

Conversation history (last {history_len} exchanges):
{history}

Your question must:
1. Target a SPECIFIC technical domain (structural, MEP, fire protection, envelope, etc.)
2. Require cross-referencing MULTIPLE documents or sections
3. Expose potential gaps, contradictions, or constructability issues
4. Demand specific citations (document name, section number, sheet number)
5. Be something a senior VDC engineer would actually need to know before coordination

Categories to rotate through:
- SPEC_INTERPRETATION: "Section X says Y, but Section Z seems to imply W. How do we reconcile?"
- CODE_COMPLIANCE: "Does this design meet NFPA 13/ASHRAE 90.1/IBC requirement X? Where is the evidence?"
- COORDINATION_GAP: "The structural drawing shows A, but the MEP routing shows B. What's the clash resolution?"
- CONSTRUCTABILITY: "Can this actually be built in the field sequence shown? What access issues exist?"
- MISSING_INFO: "What critical information is absent that would block fabrication or permitting?"
- SUBMITTAL_CHAIN: "What submittals are required, and do the approved-shop drawings match the spec?"

Respond ONLY with a JSON object:
{{"question": "...", "category": "...", "expected_depth": 3, "target_doc_hint": "..."}}"""

FOLLOWUP_PROMPT = """You are critiquing a VDC engineer's answer to your previous question.

Your original question:
{question}

Their answer:
{answer}

Your critique must:
1. Score the answer 0-100 on: accuracy, depth, citation specificity, contradiction awareness
2. Identify what citations are MISSING (document name, section, page)
3. Point out any contradictions they missed
4. Suggest 2 follow-up questions that probe deeper
5. Be ruthless but fair — a PhD advisor reviewing a dissertation chapter

Respond ONLY with a JSON object:
{{"score": 75, "strengths": ["..."], "weaknesses": ["..."], "missing_citations": ["..."], "suggested_followups": ["..."]}}"""


class CuriosityTrait:
    """Generates probing questions and critiques answers like a PhD advisor."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.asked_questions: List[Question] = []
        self.seen_categories: set = set()

    def generate_question(
        self,
        project_id: str,
        opponent_history: List[Dict],
        doc_list: List[str],
    ) -> Question:
        """Use LLM to generate a deeply probing question."""
        history_text = self._format_history(opponent_history)
        prompt = CURIOSITY_PROMPT.format(
            doc_list="\n".join(f"- {d}" for d in doc_list),
            history_len=len(opponent_history),
            history=history_text or "(No prior conversation)",
        )
        raw = llm_generate(prompt, max_tokens=400)
        parsed = self._extract_json(raw)

        q = Question(
            text=parsed.get("question", "What are the key coordination requirements?"),
            category=parsed.get("category", "GENERAL"),
            expected_depth=parsed.get("expected_depth", 3),
            target_doc_hint=parsed.get("target_doc_hint", ""),
            asked_by=self.agent_id,
        )
        self.asked_questions.append(q)
        self.seen_categories.add(q.category)
        return q

    def critique_answer(
        self,
        question: Question,
        answer: Answer,
        project_id: str,
    ) -> Critique:
        """Critique an opponent's answer like a PhD advisor."""
        prompt = FOLLOWUP_PROMPT.format(
            question=question.text,
            answer=answer.text,
        )
        raw = llm_generate(prompt, max_tokens=500)
        parsed = self._extract_json(raw)

        return Critique(
            score=float(parsed.get("score", 50)),
            strengths=parsed.get("strengths", []),
            weaknesses=parsed.get("weaknesses", []),
            missing_citations=parsed.get("missing_citations", []),
            suggested_followups=parsed.get("suggested_followups", []),
            critique_by=self.agent_id,
        )

    def _format_history(self, history: List[Dict]) -> str:
        lines = []
        for h in history[-6:]:
            lines.append(f"Q: {h.get('question', '')[:200]}")
            lines.append(f"A: {h.get('answer', '')[:200]}")
        return "\n".join(lines)

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response, handling markdown fences."""
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to find any JSON object
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except:
                    pass
            return {}


# ---------------------------------------------------------------------------
# Memory Retrieval Trait — Deep document memory with cross-reference
# ---------------------------------------------------------------------------
class MemoryRetrievalTrait:
    """Retrieves and cross-references document memory like a PhD with photographic recall."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.query_history: List[Dict] = []
        self.fact_cache: Dict[str, Any] = {}

    def retrieve(
        self,
        project_id: str,
        query: str,
        top_k: int = 8,
    ) -> tuple:
        """Deep retrieval with contradiction detection."""
        embeddings, chunks = load_embeddings(project_id)
        if embeddings is None or len(chunks) == 0:
            return [], [], 0.0

        query_emb = encode([query])
        sims = cosine_similarity(query_emb, embeddings)[0]
        top_indices = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:top_k]

        sources = []
        context_parts = []
        for idx in top_indices:
            chunk = chunks[idx]
            score = float(sims[idx])
            sources.append({
                "score": round(score, 4),
                "text": chunk["text"][:600],
                "doc_name": chunk["doc_name"],
                "doc_type": chunk["doc_type"],
            })
            context_parts.append(
                f"[{chunk['doc_name']} | {chunk['doc_type']}]: {chunk['text'][:900]}"
            )

        top_score = float(sims[top_indices[0]]) if top_indices else 0.0

        # Detect contradictions among retrieved chunks
        retrieved_chunks = [chunks[idx] for idx in top_indices]
        contradictions = detect_contradictions(retrieved_chunks, query)

        # Cross-reference with prior queries for consistency
        consistency_notes = self._check_consistency(query, sources)
        if consistency_notes:
            context_parts.append("\n[MEMORY CROSS-REFERENCE]:\n" + "\n".join(consistency_notes))

        self.query_history.append({
            "query": query,
            "sources": [s["doc_name"] for s in sources],
            "timestamp": datetime.now().isoformat(),
        })

        return sources, context_parts, top_score, contradictions

    def _check_consistency(self, query: str, sources: List[dict]) -> List[str]:
        """Check if current sources contradict prior answers."""
        notes = []
        for prior in self.query_history[-5:]:
            # Simple heuristic: if same doc but different context, flag it
            prior_docs = set(prior.get("sources", []))
            current_docs = set(s["doc_name"] for s in sources)
            overlap = prior_docs & current_docs
            if overlap and prior.get("query") != query:
                notes.append(
                    f"Prior query '{prior['query'][:50]}...' also referenced {', '.join(overlap)}"
                )
        return notes

    def synthesize_phd_answer(
        self,
        query: str,
        context_parts: List[str],
        sources: List[dict],
        contradictions: List[dict],
    ) -> str:
        """Synthesize an answer at PhD depth with full citations."""
        doc_names = list(set(s["doc_name"] for s in sources))
        contra_text = ""
        if contradictions:
            contra_text = "\n\nPOTENTIAL CONTRADICTIONS DETECTED:\n"
            for c in contradictions:
                contra_text += f"- {c['unit'].upper()}: values {', '.join(c['values'])} across {', '.join(c['documents'][:3])}\n"

        ctx_joined = "\n\n".join(context_parts)
        prompt = f"""You are a PhD-level VDC engineer answering a technical question during a peer review session.
Answer based ONLY on the provided document context. Be exhaustive but precise.

Context:
{ctx_joined}
{contra_text}

Question: {query}

Requirements:
1. Cite SPECIFIC documents, sections, and page references where possible
2. Address any contradictions explicitly — do not hide conflicts
3. If information is missing, state exactly what is missing and why it matters
4. Connect implications across disciplines (structural -> MEP -> architectural)
5. If code compliance is relevant, reference the specific standard
6. End with a confidence assessment: "High Confidence" / "Moderate Confidence" / "Low Confidence — requires verification"

Answer:"""
        answer = llm_generate(prompt, max_tokens=500)
        return answer.rstrip() + f"\n\n**Sources:** {', '.join(doc_names)}"


# ---------------------------------------------------------------------------
# VDC PhD Agent — Combines curiosity + memory
# ---------------------------------------------------------------------------
class VDCPhDAgent:
    """A single PhD-level VDC agent with curiosity and memory traits."""

    def __init__(self, agent_id: str, specialization: str = "general"):
        self.agent_id = agent_id
        self.specialization = specialization
        self.curiosity = CuriosityTrait(agent_id)
        self.memory = MemoryRetrievalTrait(agent_id)
        self.score_total = 0.0
        self.questions_asked = 0
        self.answers_given = 0
        self.critiques_made = 0

    def ask(self, project_id: str, opponent_history: List[Dict], doc_list: List[str]) -> Question:
        """Generate a probing question for the opponent."""
        q = self.curiosity.generate_question(project_id, opponent_history, doc_list)
        self.questions_asked += 1
        append_event("phd_battle", {
            "type": "question",
            "agent": self.agent_id,
            "question": q.text,
            "category": q.category,
        })
        return q

    def answer(self, project_id: str, question: Question) -> Answer:
        """Answer a question using deep memory retrieval."""
        sources, context_parts, top_score, contradictions = self.memory.retrieve(
            project_id, question.text, top_k=8
        )
        if top_score < 0.30:
            answer_text = (
                f"[AGENT {self.agent_id}] The documents do not contain sufficient information "
                f"to answer this question with confidence. "
                f"Top retrieval score was {top_score:.3f}. "
                f"This may indicate a gap in the document set or that the question requires "
                f"information from as-built conditions not present in the design documents."
            )
        else:
            answer_text = self.memory.synthesize_phd_answer(
                question.text, context_parts, sources, contradictions
            )

        ans = Answer(
            text=answer_text,
            sources=sources,
            contradictions_found=contradictions,
            confidence=top_score,
            answered_by=self.agent_id,
        )
        self.answers_given += 1
        append_event("phd_battle", {
            "type": "answer",
            "agent": self.agent_id,
            "question": question.text,
            "answer": answer_text[:500],
            "confidence": top_score,
        })
        return ans

    def critique(self, question: Question, answer: Answer, project_id: str) -> Critique:
        """Critique an opponent's answer."""
        critique = self.curiosity.critique_answer(question, answer, project_id)
        self.critiques_made += 1
        self.score_total += critique.score
        append_event("phd_battle", {
            "type": "critique",
            "agent": self.agent_id,
            "target": answer.answered_by,
            "score": critique.score,
            "weaknesses": critique.weaknesses,
        })
        return critique

    def stats(self) -> dict:
        avg_score = self.score_total / max(self.critiques_made, 1)
        return {
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "questions_asked": self.questions_asked,
            "answers_given": self.answers_given,
            "critiques_made": self.critiques_made,
            "total_critique_score": round(self.score_total, 1),
            "average_critique_score": round(avg_score, 1),
        }
