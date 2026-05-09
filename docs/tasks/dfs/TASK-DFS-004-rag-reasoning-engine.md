# TASK-DFS-004: Graph RAG + ReAct Reasoning Engine

**Date:** 2026-05-03  
**Scope:** Depth-first implementation of the reasoning engine that combines Graph RAG for cross-reference resolution with ReAct for tool-augmented reasoning  
**Personas:** First-Principles Engineer, Distributed Systems Architect, Diagnostic Problem-Solver  
**Status:** Pending BFS Completion

---

## 1. Objective

Build a reasoning engine that can:
- Traverse cross-references between specs, drawings, and codes (Graph RAG)
- Use tools to look up specific sections, query drawing indexes, calculate tolerances (ReAct)
- Generate chain-of-thought explanations for contradiction detection
- Achieve <500ms end-to-end latency for simple queries, <2s for complex multi-hop reasoning

## 2. Architecture

```
User Query
    ↓
[Intent Router] — classify: simple lookup | contradiction | compliance | RFI draft
    ↓
[Graph RAG Retriever] — traverse document graph for evidence
    ↓
[ReAct Loop] — reason → act (tool call) → observe → repeat (max 5 iterations)
    ↓
[SLM Generator] — synthesize answer with citations
    ↓
[Output Validator] — check hallucination, format JSON
    ↓
Structured Response {answer, citations, confidence, reasoning_chain}
```

## 3. Graph RAG Implementation

### 3.1 Document Graph Schema

```python
@dataclass
class DocumentNode:
    id: str
    type: Literal["spec", "drawing", "code", "rfi", "contract"]
    title: str
    project_id: str

@dataclass
class ChunkNode:
    id: str
    document_id: str
    level: int
    text: str
    embedding: List[float]

@dataclass
class Edge:
    source: str  # chunk_id or document_id
    target: str
    type: Literal["references", "contradicts", "implements", "supersedes"]
    confidence: float
```

### 3.2 Graph Construction

```python
class DocumentGraphBuilder:
    def build(self, chunks: List[Chunk]) -> nx.DiGraph:
        """
        1. Create chunk nodes
        2. Create parent-child edges (hierarchy)
        3. Detect cross-reference edges via regex
        4. Detect contradiction edges via SLM classifier
        5. Store in Neo4j or NetworkX + pgvector hybrid
        """
```

### 3.3 Graph Retrieval

```python
class GraphRetriever:
    def retrieve(self, query: str, entry_points: List[str]) -> List[Chunk]:
        """
        1. Vector search for entry point chunks
        2. Graph traversal (BFS/DFS) to find related chunks
        3. Rank by combined vector similarity + graph distance
        4. Return top-k chunks with provenance paths
        """
```

## 4. ReAct Implementation

### 4.1 Tools

| Tool | Input | Output | When Used |
|------|-------|--------|-----------|
| `lookup_section` | division, section | full section text | User asks about specific spec section |
| `query_drawing_index` | drawing_number | sheet metadata | User references a drawing |
| `check_code_compliance` | spec_text, code_reference | compliance_report | Compliance checking task |
| `calculate_tolerance` | nominal_value, tolerance_class | min/max values | Engineering calculation |
| `search_similar_projects` | query, project_type | related_project_docs | Analogical reasoning |
| `draft_rfi` | contradiction, context | rfi_json | RFI generation task |

### 4.2 ReAct Loop

```python
class ReActReasoner:
    def reason(self, query: str, context: List[Chunk]) -> ReasoningResult:
        """
        Loop:
        1. Generate Thought: "I need to check Section 23 05 13 for motor requirements"
        2. Select Action: tool=lookup_section, args={"division": "23", "section": "05 13"}
        3. Execute Action: retrieve section text
        4. Observe Result: add to context
        5. Repeat until answer or max iterations
        6. Generate Final Answer with citations
        """
```

## 5. SLM Integration

```python
class ReasoningEngine:
    def __init__(self, model: SLM, retriever: GraphRetriever, tools: ToolRegistry):
        self.model = model
        self.retriever = retriever
        self.tools = tools
    
    def query(self, user_query: str) -> StructuredResponse:
        # Phase 1: Retrieve evidence
        chunks = self.retriever.retrieve(user_query)
        
        # Phase 2: ReAct reasoning
        result = self.react_loop(user_query, chunks)
        
        # Phase 3: Generate structured output
        return self.format_response(result)
```

## 6. Latency Budget

| Component | Target | Max | Optimization |
|-----------|--------|-----|--------------|
| Intent routing | 10ms | 50ms | Rule-based classifier |
| Graph retrieval | 100ms | 300ms | HNSW index + cached graph |
| ReAct iteration | 200ms | 500ms | vLLM batching, speculative decoding |
| Output generation | 300ms | 1000ms | Streaming, early stopping |
| **Total simple** | **<500ms** | **<1s** | — |
| **Total complex** | **<1.5s** | **<3s** | — |

## 7. Implementation Tasks

- [ ] **Subtask 1:** Implement `DocumentGraphBuilder` with Neo4j backend
- [ ] **Subtask 2:** Implement cross-reference detection (regex + LLM fallback)
- [ ] **Subtask 3:** Implement contradiction edge detection (fine-tuned classifier)
- [ ] **Subtask 4:** Implement `GraphRetriever` with hybrid vector+graph search
- [ ] **Subtask 5:** Implement ToolRegistry and 6 construction-specific tools
- [ ] **Subtask 6:** Implement ReAct loop with observation history
- [ ] **Subtask 7:** Integrate fine-tuned SLM via vLLM for inference
- [ ] **Subtask 8:** Implement streaming response with early stopping
- [ ] **Subtask 9:** Add hallucination detection (citation verification)
- [ ] **Subtask 10:** Benchmark latency and accuracy on 500 test queries

## 8. Acceptance Criteria

1. Cross-reference traversal: retrieve related chunks in <200ms
2. Contradiction detection: F1 >0.75 on held-out test set
3. Tool use accuracy: >90% correct tool selection
4. End-to-end latency: P95 <500ms for simple queries, <2s for complex
5. Citation accuracy: >95% of cited chunks actually support the claim
6. Hallucination rate: <5% on factual queries

---

## References

[^1]: ReAct: Synergizing Reasoning and Acting in Language Models. 2022. https://arxiv.org/abs/2210.03629
[^2]: Self-RAG: Learning to Retrieve, Generate, and Critique. 2023. https://arxiv.org/abs/2310.11511
[^3]: From Local to Global: A Graph RAG Approach. 2024. https://arxiv.org/abs/2404.16130
[^4]: vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention. 2023. https://arxiv.org/abs/2309.06180
