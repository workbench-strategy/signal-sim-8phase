# Playbook: After any field touch

- **Domain:** meta
- **Risk:** n/a

## Goal

Turn every site visit or ticket into durable lab assets (learn / grow loop).

## Steps

1. Create or update `playbooks/<nn>_<short_name>.md` from `_template.md`
2. Add or edit a sanitized profile under `profiles/`
3. If you captured traffic or screenshots of MIB walks, redact and store under `captures/`
4. Note quirks (vendor firmware bugs, RO objects, weird MULTI limits)
5. Only then open `src/its/policies/` for an experiment
6. Run tests: `PYTHONPATH=src python -m pytest -v tests/its tests/ntcip`

## Definition of done

- Future You can replay the read path offline
- No secrets landed in git
- At least one sentence on what you would innovate next
