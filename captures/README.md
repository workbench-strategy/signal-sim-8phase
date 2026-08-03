# Captures

Anonymized protocol or API traces used to **regress and learn** field behavior.

## Rules

- Strip credentials, public IPs of real devices if policy requires, and PII
- Prefer documentation-range addresses in redacted fixtures
- Name files: `<domain>_<sitecode>_<scenario>.json`
- Link each capture from a playbook when possible

## Suggested contents per file

- timestamp (UTC)
- profile_id
- request/response pairs (OIDs or API paths)
- expected domain snapshot after decode

Empty until you add your first field capture -- that is intentional.
