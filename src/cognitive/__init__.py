"""
cognitive — Autonomous Cognitive Decision-Making System for Medha.

A metacognitive architecture implementing Dual-Process Theory,
Active Inference, and Bayesian strategy selection for construction
document intelligence.

Modules:
    types          — Shared data structures (SOLID: ISP)
    system1_heuristic   — Fast pattern recognition (Type 1 processing)
    system2_analytical  — Chain-of-thought reasoning (Type 2 processing)
    system3_retrieval   — Active information seeking
    system4_metacognitive — Confidence monitoring & halting
    orchestrator        — Bayesian strategy arbitration

Usage:
    from cognitive import System5CognitiveOrchestrator
    
    orchestrator = System5CognitiveOrchestrator(
        system1=System1HeuristicEngine(),
        system2=System2AnalyticalEngine(llm_client),
        system3=System3RetrievalController(v_search, g_search, k_search),
        system4=System4MetacognitiveMonitor(),
        tools={"lookup_section": lookup_fn, ...},
    )
    
    result = orchestrator.decide(
        "Does Section 23 05 13 contradict Drawing A-101?"
    )
    print(result.answer)
    print(result.confidence)
    print(result.reasoning_chain)

Date: 2026-05-03
"""

from .types import (
    CognitiveState,
    CognitiveOutput,
    EpistemicStatus,
    ReasoningStrategy,
    QueryType,
    Evidence,
)
from .system1_heuristic import System1HeuristicEngine
from .system2_analytical import System2AnalyticalEngine, ReasoningStep
from .system3_retrieval import System3RetrievalController
from .system4_metacognitive import System4MetacognitiveMonitor
from .orchestrator import System5CognitiveOrchestrator

__all__ = [
    "CognitiveState",
    "CognitiveOutput",
    "EpistemicStatus",
    "ReasoningStrategy",
    "QueryType",
    "Evidence",
    "System1HeuristicEngine",
    "System2AnalyticalEngine",
    "ReasoningStep",
    "System3RetrievalController",
    "System4MetacognitiveMonitor",
    "System5CognitiveOrchestrator",
]
