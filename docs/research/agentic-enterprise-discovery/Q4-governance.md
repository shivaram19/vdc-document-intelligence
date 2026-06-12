# Q4: How Do We Govern Agents in an Enterprise?

**Research Question:** What governance structures make an agentic enterprise trustworthy, auditable, and safe — without making it so slow that it loses its advantage?

---

## Why This Matters for Medha

Agents will have access to data, tools, and potentially money. Without governance, one bad agent action can destroy trust, leak secrets, or waste budget. With too much governance, the agents become useless.

---

## Sub-Questions

### 4.1 Authorization and Boundaries
1. How do we define what each agent is allowed to do?
2. Are there open-source authorization frameworks for agents (RBAC, ABAC, policy-as-code)?
3. How do we enforce least-privilege access for agents?
4. Can agents have "scopes" or "capabilities" like OAuth tokens?

### 4.2 Audit and Traceability
1. What must be logged for every agent action?
2. How long should logs be retained?
3. What makes an audit trail legally or operationally useful?
4. How do we make agent reasoning inspectable?

### 4.3 Safety and Guardrails
1. What categories of agent actions need human approval? (spend, external comms, data deletion, code deploy, etc.)
2. How do we detect when an agent is drifting outside its bounds?
3. What kill switches or circuit breakers are needed?
4. How do we prevent prompt injection or tool misuse?

### 4.4 Compliance and Liability
1. What regulations apply to agentic enterprises? (EU AI Act, GDPR, sector-specific)
2. How is liability assigned when agents act on behalf of a company?
3. What documentation is needed to prove compliance?
4. How do contracts with customers address agent involvement?

### 4.5 Governance Without Bureaucracy
1. How do fast-moving startups govern agents without becoming enterprises?
2. What is the minimum viable governance framework?
3. How do governance rules scale as the company grows?
4. What is the right balance between autonomy and oversight?

---

## Current Hypotheses

1. Governance should be **capability-based and action-specific**, not role-based in the traditional sense.
2. Every agent should have a clear **scope document** listing allowed tools, spend limits, and approval requirements.
3. All actions should be logged with **who, what, when, cost, and reasoning**.
4. Humans should have **one-command kill switches** for any agent.

---

## What Would Change Our Mind

- Discovery of a widely adopted open-source agent governance framework
- Evidence that lightweight governance is insufficient for legal liability
- Case studies showing that heavy governance killed startup velocity

---

## Where to Look for Answers

- EU AI Act and NIST AI Risk Management Framework
- Open-source policy engines (Open Policy Agent, Casbin)
- Agent security research (prompt injection, tool misuse)
- Enterprise AI governance platforms and their open-source alternatives

---

## Medha-Specific Translation

For Medha's first agents:
- No agent spends money or sends customer-facing messages without approval
- Every agent has a daily cost cap
- All agent actions append to a log in `logs/agents/`
- Founder can disable any agent via Plane task or shell command
- Secrets never leave environment variables

---

**Next action:** Draft a "Minimum Viable Agent Governance" policy for Medha and store it in `docs/decisions/`.
