# Security Pilot Checklist
**Scope:** Open-source self-hosted stack (Plane, Postiz, Flask backend, landing page)  
**Goal:** Catch and fix security gaps before production use

---

## 1. Secrets Management

| Check | Status | Notes |
|-------|--------|-------|
| API keys stored in `.env` files, not code | ✅ | Root `.env`, `postiz/.env`, `plane/plane-app/.env` |
| `.env` files gitignored | ✅ | Verified via `git check-ignore` |
| No secrets in git history | ⚠️ | Run `git log --all -p -S 'sk-proj'` to audit |
| OpenAI keys rotated after chat exposure | 🔴 | **PENDING** — delete exposed keys, generate new ones |
| Plane admin password changed from temporary | 🔴 | **PENDING** — user must change after first login |
| Plane secrets auto-generated (DB, RabbitMQ, MinIO, Django) | ✅ | Done during setup |
| Postiz JWT secret is random | ✅ | Hardcoded but random enough for single-user |
| Backup of secret locations exists offline | 🔴 | **PENDING** — document in password manager |

---

## 2. Network Exposure

| Check | Status | Notes |
|-------|--------|-------|
| Only necessary ports open on Azure NSG | 🟡 | 22, 80, 443, 1935, 4007, 8083, 8969 open. Review if all needed |
| Direct Plane port 8091 closed | ✅ | Removed from UFW and Azure NSG |
| Direct Postiz/Temporal/Spotlight ports reviewed | 🟡 | 4007, 8083, 8969 still open. Should be behind domain + auth |
| UFW active with default-deny | ✅ | Only explicit ports allowed |
| Nginx server_tokens off | ✅ | Version hidden |
| No default server leaks internal info | ✅ | IP default block removed |

**Recommendation:** Move Postiz and Temporal UI behind domains too, with basic auth or restrict by IP.

---

## 3. SSL/TLS

| Check | Status | Notes |
|-------|--------|-------|
| HTTPS enabled for plane.trayini.ai | ✅ | Let's Encrypt certificate |
| HTTPS enabled for medha.trayini.ai | ✅ | Same certificate |
| HTTP → HTTPS redirect | ✅ | Certbot configured |
| SSL certificate auto-renewal | ✅ | Certbot cron/timer installed |
| Renewal dry-run tested | ✅ | `certbot certonly --dry-run --cert-name plane.trayini.ai` succeeded |
| HSTS header | ✅ | Added by Certbot's options-ssl-nginx.conf |
| Weak SSL protocols disabled | ✅ | TLS 1.2/1.3 only |
| Certificate expiry monitoring | 🔴 | **PENDING** — add UptimeRobot or cron check |

---

## 4. Authentication & Access Control

| Check | Status | Notes |
|-------|--------|-------|
| Plane admin account exists | ✅ | Created via CLI |
| Plane signup enabled | ⚠️ | Currently `enable_signup: true`. For single-user, consider disabling after creating your account |
| Plane workspace creation open | ⚠️ | `is_workspace_creation_disabled: false`. Restrict if not needed |
| Postiz registration open | ✅ | `DISABLE_REGISTRATION: true`. Container recreated. |
| Postiz admin created | 🔴 | **PENDING** — sign up and disable registration |
| SSH key-based auth preferred | 🟡 | Check Azure VM uses SSH keys, not passwords |
| Server login restricted | 🟡 | Confirm only authorized users have SSH access |

---

## 5. Container Security

| Check | Status | Notes |
|-------|--------|-------|
| Containers run as non-root where possible | 🟡 | Plane/Postiz official images; review `docker inspect` |
| Image versions pinned | 🟡 | Plane pinned to v1.3.1; Postiz uses `latest` |
| No unnecessary container capabilities | 🟡 | Default Docker capabilities |
| Container logs don't leak secrets | ✅ | Verified for OpenAI key |
| Docker socket not exposed to containers | ✅ | Not mounted |
| Resource limits on containers | 🔴 | **PENDING** — add memory/CPU limits in compose |

---

## 6. Database Security

| Check | Status | Notes |
|-------|--------|-------|
| Postgres passwords strong/random | ✅ | Plane and Postiz use generated passwords |
| Postgres not exposed to internet | ✅ | Only inside Docker networks |
| Postgres exposed on host port | ⚠️ | System Postgres on 5432; ensure auth is strong |
| Redis not exposed to internet | ✅ | Inside Docker networks |
| Redis exposed on host port | ⚠️ | System Redis on 6379; ensure no auth bypass |
| Database backups enabled | 🔴 | **PENDING** — weekly pg_dump for Plane and Postiz |

---

## 7. Dependency & Vulnerability Management

| Check | Status | Notes |
|-------|--------|-------|
| Plane version current | 🟡 | v1.3.1 — check for security advisories |
| Postiz version current | 🟡 | `latest` tag — pin and track |
| OS packages updated | 🟡 | Run `sudo apt update && sudo apt upgrade` |
| Container images scanned | 🔴 | **PENDING** — use `docker scout` or Trivy |
| Python dependencies audited | 🔴 | **PENDING** — run `pip-audit` on Flask backend venvs |

---

## 8. Logging & Monitoring

| Check | Status | Notes |
|-------|--------|-------|
| Nginx access logs enabled | ✅ | Default |
| Nginx error logs enabled | ✅ | Default |
| Docker logs retained | 🟡 | Default Docker logging; consider log rotation |
| Failed login monitoring | 🔴 | **PENDING** — watch `/var/log/nginx/` or fail2ban |
| Uptime monitoring | 🔴 | **PENDING** — UptimeRobot free plan |
| Disk space monitoring | 🔴 | **PENDING** — Docker volumes grow over time |
| Log aggregation | 🔴 | **PENDING** — optional: Loki/CloudWatch |

---

## 9. Backup & Disaster Recovery

| Check | Status | Notes |
|-------|--------|-------|
| Plane database backup script | ✅ | `scripts/backup-plane.sh` runs weekly via cron |
| Postiz database backup script | ✅ | `scripts/backup-postiz.sh` runs weekly via cron |
| Nginx config backup | ✅ | `/etc/nginx.backup.20260612_132849` |
| SSL certificate backup | 🟡 | `/etc/letsencrypt/` — backup separately |
| Backup storage off-server | 🔴 | **PENDING** — S3, rsync, or cloud storage |
| Documented restore procedure | 🔴 | **PENDING** |

---

## 10. Application-Specific Security

### Plane
- [ ] Disable public signup if single-user
- [ ] Change default admin email
- [ ] Change default admin password
- [ ] Review workspace/project permissions
- [ ] Disable telemetry if desired (`is_telemetry_enabled`)
- [ ] Configure SMTP for password reset (optional)

### Postiz
- [ ] Create admin account
- [ ] Disable registration (`DISABLE_REGISTRATION=true`)
- [ ] Add LinkedIn/X API keys via `.env`, not CLI
- [ ] Review storage provider (local vs Cloudflare R2)

### Flask Backend
- [ ] Review `backend/app.py` for hardcoded secrets
- [ ] Ensure OpenAI key not logged
- [ ] Add rate limiting if exposed
- [ ] Review CORS settings

### Nginx / Server
- [ ] Keep server packages updated
- [ ] Configure fail2ban for SSH/nginx
- [ ] Disable password-based SSH if enabled
- [ ] Review Azure NSG rules quarterly

---

## 11. Immediate Action Items (This Week)

1. **Rotate OpenAI keys** (HIGH)
2. **Disable Postiz registration** (HIGH)
3. **Change Plane admin password** (HIGH)
4. **Run OS updates** (HIGH)
5. **Create backup scripts** for Plane and Postiz databases (MEDIUM)
6. **Set up UptimeRobot monitoring** for https://plane.trayini.ai and https://medha.trayini.ai (MEDIUM)
7. **Add Docker log rotation** (MEDIUM)
8. **Review and disable Plane public signup** if not needed (MEDIUM)

---

## 12. Security Review Schedule

| Frequency | Task |
|-----------|------|
| Weekly | Check failed login attempts, disk space, service uptime |
| Monthly | OS updates, dependency audit, review NSG rules |
| Quarterly | SSL renewal test, secret rotation, backup restore test |
| Annually | Full access review, disaster recovery drill |

---

**Status legend:** ✅ Done | 🟡 Partial / Needs review | 🔴 Not done / High priority
