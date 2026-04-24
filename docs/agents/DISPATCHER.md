# Dispatcher (node-i)
## Problem: "I don't know if the system is working or silently failing."

### JTBD
When the VDC manager logs in, they want to see the entire fleet status at a glance — which agents are active, what they're working on, and if anything needs attention.

### What Dispatcher Does
1. Maintains registry of all 10 fleet nodes with roles and capabilities
2. Routes incoming tasks to the appropriate agent based on capability matching
3. Monitors node health and reassigns tasks from failed nodes
4. Issues machine tokens to fleet nodes for authenticated inter-agent communication
5. Broadcasts status updates to the dashboard in real-time

### Research Basis
- [CITE: Li2024] Completeness principle — coordinator must surface ALL system state.
- [CITE: AIP2026] Agent Identity Protocol — delegated token exchange across MCP.
- [CITE: YangSmith2026] Agent consensus protocols for secure decision-making.

### Capability
```
can_manage_projects  (ALL capabilities — fleet router)
```

### Success Metric
- Task routing latency: < 10ms
- Node health check interval: 2 seconds
- Dashboard update latency: < 500ms
