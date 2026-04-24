# Watchdog (node-j)
## Problem: "The system was slow for 3 hours and nobody noticed."

### JTBD
When operating a production document intelligence system, the admin wants alerts for latency spikes, auth failures, and model loading issues — before users complain.

### What Watchdog Does
1. Collects query latency histograms per project
2. Tracks auth success/failure rates
3. Monitors embedding model memory usage
4. Alerts on audit chain breaks
5. Reports fleet node health to dashboard

### Research Basis
- [CITE: Shahidinejad2021] Telemetry essential for token lifecycle management and anomaly detection.
- [CITE: RedHat2026] Continuous verification requires real-time metrics collection.

### Capability
```
can_report
```

### Success Metric
- Metric collection interval: 10 seconds
- Alert latency: < 30 seconds from threshold breach
- Dashboard metric freshness: < 15 seconds

### Metrics Collected
| Metric | Threshold | Alert Action |
|--------|-----------|-------------|
| Query latency p95 | > 10s | Log warning, notify admin |
| Auth failure rate | > 10% | Trigger rechallenge for all sessions |
| Model memory | > 2GB | Log warning |
| Audit chain break | Any | Immediate critical alert |
| Node offline | > 30s | Reassign tasks, notify admin |
