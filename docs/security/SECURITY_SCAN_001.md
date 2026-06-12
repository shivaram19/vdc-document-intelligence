# Security Scan Report — Medha Repo

**Date:** 2026-06-12
**Scanner 1:** Google OSV-Scanner v2.3.8 (`osv-scanner scan source -r .`)
**Scanner 2:** TruffleHog v3.95.5 (`trufflehog filesystem .` + `trufflehog git file://. --branch=<branch>`)

---

## 1. Dependency Vulnerabilities (OSV-Scanner)

**Summary:** 7 packages affected by 15 known vulnerabilities — 2 Critical, 4 High, 9 Medium. 12 are fixable by upgrading.

### Affected packages

| Package | Version | Severities | Fix path |
|---------|---------|------------|----------|
| `chromadb` | 1.5.6 | 2 Critical (CVSS 9.3) | Upgrade to ≥ 1.6.0 (outside affected range 1.0.0–1.5.9) |
| `gunicorn` | 20.1.0 | 2 High (CVSS 7.5, 8.2) | Upgrade to ≥ 22.0.0 |
| `requests` | 2.25.1 | 5 Medium (CVSS 4.4–6.1) | Upgrade to ≥ 2.33.0 |
| `torch` | 2.11.0 | 1 Medium (CVSS 5.3) | Check OSV advisory for fixed version |

### Source files

- `backend/requirements-chroma.txt`
- `backend/requirements-local-llm.txt`
- `backend/requirements-retrieval.txt`
- `backend/requirements.txt`
- `backend/requirements-pgvector.txt`

### Notable CVEs

- **GHSA-f4j7-r4q5-qw2c / CVE-2026-45829** — ChromaDB, CVSS 9.3 (Critical)
- **GHSA-w3h3-4rj7-4ph4** — Gunicorn request smuggling, CVSS 8.2 (High)
- **GHSA-hc5x-x2vx-497g** — Gunicorn, CVSS 7.5 (High)
- **PYSEC-2023-74** — Requests, CVSS 6.1 (Medium)

---

## 2. Secrets / Keys (TruffleHog)

### Confirmed live secret (filesystem)

| Detector | File | Line | Status | Action |
|----------|------|------|--------|--------|
| OpenAI API key | `.env` | 1 | **Verified live** | **Rotate immediately** |

The key is verified active and tied to a personal OpenAI org with MFA enabled. It is gitignored but present on the VM filesystem.

### Secrets in git history (all branches)

Scanned: `main`, `master`, `origin/main`, `origin/master`, plus all tags and reflog. No tags; no stashes.

| Detector | File | Branches | Status | Action |
|----------|------|----------|--------|--------|
| XAI API key | `picocloth-deploy/node-a-vdc-config.json` | main, master, origin/main, origin/master | Unverified | **Treat as exposed — rotate** |
| XAI API key | `picocloth-deploy/node-b-vdc-config.json` | main, master, origin/main, origin/master | Unverified | **Treat as exposed — rotate** |
| XAI API key | `picocloth-deploy/backups/node-a-config.json.orig` | main, master, origin/main, origin/master | Unverified | **Treat as exposed — rotate** |
| XAI API key | `picocloth-deploy/backups/node-b-config.json.orig` | main, master, origin/main, origin/master | Unverified | **Treat as exposed — rotate** |
| XAI API key | `SECURITY.md` | master, origin/master only | Unverified | **Treat as exposed — rotate** |

**Important:** These are unverified because TruffleHog could not reach the XAI verification endpoint, but the strings are valid-looking XAI API keys in plain text. They were emitted in the scan output and exist in git history, so they must be considered compromised.

The same XAI key appears in all five locations. It was also referenced in `SECURITY.md` (master branch) as an example for BFG history rewriting.

### Current working tree status (post-remediation)

The following commits removed the literal keys from the current working tree (history still contains them until `git filter-repo` is run):

- `main` commit `0c1a035` — replaced hardcoded XAI keys in `picocloth-deploy/*.json` with `__XAI_API_KEY__` placeholder; `deploy.sh` now substitutes from `XAI_API_KEY` env var.
- `master` commit `754bfdf` — removed literal XAI key from `SECURITY.md` and backup configs; added this scan report.

### Git history summary

- `main` / `origin/main`: 4 unverified secrets in history
- `master` / `origin/master`: 5 unverified secrets in history
- `trufflehog git file://. --only-verified` returned **0 verified** secrets in committed history.

### False positives

TruffleHog also flagged private keys inside `certbot-venv/lib/python3.10/site-packages/.../testdata/`. These are test fixture files shipped with the `acme` Python package, not real production secrets.

### Other `.env` files present

- `./plane/plane-app/.env`
- `./postiz/.env`
- `./.env.example` (example/template file)

These were scanned but did not surface as verified secrets. They should still be audited manually as part of routine secret hygiene.

---

## 3. Immediate Actions

1. **Rotate the OpenAI key** in `.env` and any other place it is used (Plane, Postiz, backend).
2. **Rotate the XAI key** found in `picocloth-deploy/*` configs and purge it from git history.
3. **Purge secrets from git history** using `git-filter-repo` or BFG:
   - Target file patterns: `picocloth-deploy/*.json`, `picocloth-deploy/backups/*.orig`, `SECURITY.md`
   - Replacement string for the XAI key: `YOUR_XAI_API_KEY_HERE`
4. **Force-push** cleaned history to `origin/main` and `origin/master` (will disrupt clones/forks).
5. **Pin and upgrade dependencies:**
   - `chromadb>=1.6.0`
   - `gunicorn>=22.0.0`
   - `requests>=2.33.0`
   - Review `torch` advisory for fixed version.
6. **Re-run OSV-Scanner** after upgrades until zero high/critical findings remain.
7. **Audit `.env` files** in `plane/plane-app/` and `postiz/` for stale credentials.
8. **Add `certbot-venv/` to TruffleHog ignore list** to reduce false positives in future scans.

### History purge command

A replacement file has been created at `scripts/git-filter-repo-replacements.txt` (do **not** commit it). After rotating both keys, run:

```bash
# Ensure git-filter-repo is installed
pip install git-filter-repo

# Run from repo root
git filter-repo --replace-text scripts/git-filter-repo-replacements.txt --force

# Force-push rewritten history
git push origin main --force
git push origin master --force

# Delete the replacement file
rm scripts/git-filter-repo-replacements.txt
```

**Warning:** `git filter-repo` removes the origin remote and rewrites all refs. Ensure you have a fresh backup clone before running.

---

## 4. Commands to reproduce

```bash
# OSV-Scanner
curl -sL -A "Mozilla/5.0" https://github.com/google/osv-scanner/releases/download/v2.3.8/osv-scanner_linux_amd64 -o /tmp/osv-scanner
chmod +x /tmp/osv-scanner
/tmp/osv-scanner scan source -r .

# TruffleHog filesystem scan
trufflehog filesystem .

# TruffleHog all branches
for branch in main master origin/main origin/master; do
  echo "Scanning $branch"
  trufflehog git file://. --branch=$branch
done

# History purge example (git-filter-repo)
git filter-repo --replace-text <(echo 'xai-REPLACE_ME==>YOUR_XAI_API_KEY_HERE')
```
