# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in this repository, please do NOT open a public issue. Instead, email the maintainers directly.

## Known Security Incidents

### 2026-05-03 — API Keys Sanitized from Public Repository

**Status:** Resolved (keys rotated, history sanitized where possible)  
**Severity:** High — live API keys were present in committed configuration files

#### What Was Found

After making this repository public, a security scan revealed the following secrets in tracked files:

| Secret | Location | Status |
|--------|----------|--------|
| `xai-NAncu...` (xAI API key) | `picocloth-deploy/node-a-vdc-config.json` (lines 40, 50) | **Sanitized + rotated** |
| `xai-NAncu...` (xAI API key) | `picocloth-deploy/node-b-vdc-config.json` (lines 40, 50) | **Sanitized + rotated** |
| `6ed6a68c...` (Pico channel token) | `picocloth-deploy/node-a-vdc-config.json` (line 29) | **Sanitized** |
| `119c0e1c...` (Pico channel token) | `picocloth-deploy/node-b-vdc-config.json` (line 29) | **Sanitized** |

#### What Was NOT in Git (Good)

- `.env` file — correctly gitignored, never committed
- No database connection strings with passwords
- No AWS/GCP/Azure credentials
- No SSH private keys
- No GitHub personal access tokens

#### Actions Taken

1. **Sanitized configuration files** — replaced all live keys with `YOUR_XAI_API_KEY_HERE` and `YOUR_PICO_CHANNEL_TOKEN_HERE` placeholders
2. **Committed sanitization** with explicit security commit message
3. **Advised repository owner to rotate keys** at provider console

#### Important Note on Git History

The sanitized commit removes secrets from the **current HEAD**, but the secrets remain in **previous commits** in the git history. Because this repository was public while the secrets were present, the keys are considered **compromised**.

**To fully remove secrets from history**, use [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) or `git filter-repo`:

```bash
# Using BFG (recommended)
bfg --replace-text secrets.txt

# Where secrets.txt contains:
xai-NAncuOYy8VqcSlBMzTI1n8FV1lx2GWUj6Q0irGUyHuFpbuwuxFJX6zvwUHeUwAaZgmWqOLpTtG5Oeq7n==>YOUR_XAI_API_KEY_HERE
6ed6a68cbd0ec752932b63c983be8606==>YOUR_PICO_CHANNEL_TOKEN_HERE
119c0e1c2e5da08ff9f63120e0aaed7a==>YOUR_PICO_CHANNEL_TOKEN_HERE
```

**Warning:** Rewriting history requires force-pushing and will disrupt any forks or clones.

## Prevention

- `.env` is gitignored — always store secrets there, never in tracked files
- Use `.env.example` with placeholder values for documentation
- Run `git-secrets` or `truffleHog` before making repositories public
- Review all configuration files for hardcoded credentials before committing
