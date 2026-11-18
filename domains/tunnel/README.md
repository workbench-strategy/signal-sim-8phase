# Domain: Tunnel ITS (crossover)

Tunnel systems combine roadway ITS (CCTV, VMS, data stations, often signals /
lane control) with facility / SCADA concerns.

## Lab approach

- Reuse CCTV + VMS + RWIS adapters
- Encode **scenarios** as playbooks (congestion, air quality, fire response
  coordination) -- not as a separate protocol stack on day one
- Keep SCADA credentials and safety PLCs out of this repo unless you build an
  explicit sanitized mock

## First playbook to write

"Verify portal camera + confirm VMS message during drill" using dry-run only.
