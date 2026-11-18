# ITS Systems Lab Strategy

**Audience:** Future you (transportation / ITS engineer).  
**Purpose:** Learn, grow, and innovate across roadway ITS, tunnel ITS, and
adjacent domains (airport security sandbox) without losing field fidelity.

## Mission

Build a **digital twin + interchange kit** for the systems you operate:

- Faithful enough to **replicate** cabinets, signs, sensors, and cameras you meet
- Flexible enough to **host new ideas** behind stable intents (shadow-first)
- Broad enough for **CCTV, data stations, RWIS, VMS, signals, tunnels**,
  with a walled **airport_lab** for security learning

Positioning line:

> A standards-true ITS workbench that can mirror field implementations and
> host experimental workflows behind the same interfaces agencies already trust.

## Your domain map

| Domain | Typical protocols / standards | Lab priority |
|--------|-------------------------------|--------------|
| VMS / DMS | NTCIP 1203, MULTI | High -- common ops surface |
| RWIS / ESS | NTCIP 1204 | High -- weather-responsive ops |
| CCTV | NTCIP 1205 and/or ONVIF/RTSP | High -- roadway + tunnel + airport bridge |
| Signals / ASC | NTCIP 1201 / 1202 | Active vertical (scaffold exists) |
| Data stations | TMDD, agency APIs, sometimes NTCIP | Medium -- performance measures |
| Tunnel ITS | ITS + SCADA scenario orchestration | Medium -- crossover playbooks |
| Airport security | PACS / video / SOP (sandbox only) | Low until formal authority; mocks only |

## Two tracks, one core

### Track A -- Replicate (earn ops trust)

Goal: clone existing implementations as data + tests.

Artifacts:

- **Device profile packs** in `profiles/` (vendor, firmware, protocol, objects/API, quirks)
- **Captures** in `captures/` (anonymized GET/SET/trap or API traces)
- **Playbooks** in `playbooks/` (ops language: patch VMS, sync time, verify camera)
- **Conformance as data** (what is RO vs RW; which objects exist)

### Track B -- Innovate (ship ideas safely)

Goal: try new engineering ideas without rewriting field stacks.

Artifacts:

- **Policies** in `policies/` / `src/its/policies/` implementing a small interface
- **Shadow mode** -- read live (or replay), log "would have done X", no write
- **Sim / GIS** -- prove spatial and timing impact before staging
- **Agent SIL** (later) -- local sim answers as if it were a field device

Creativity lives in policies and playbooks. Drivers and profiles stay boring.

## Architecture principles (non-negotiable)

1. **Stable core, volatile edges** -- protocol drivers and profiles change slowly;
   policies and playbooks change fast.
2. **Intents over raw protocol** -- business code says `post_vms_message` or
   `get_phase_status`, never scatters OIDs/URLs.
3. **Pluggable drivers** -- NTCIP, ONVIF, HTTP/TMDD, MQTT stubs share the same
   adapter shape (`DomainAdapter`).
4. **Shadow before write** -- every new policy defaults to observe/recommend.
5. **No secrets in git** -- communities, USM keys, badge data, prod URLs stay
   in local env / secret store. Profiles are sanitized.
6. **Airport isolation** -- `airport_lab/` is synthetic only until explicit
   authority exists. No prod security integrations by default.

## Promotion path

```
capture  ->  model  ->  simulate  ->  shadow  ->  field
 (trace)    (profile)   (sim/GIS)   (recommend)  (ops-approved write)
```

Gate questions:

| Gate | Question |
|------|----------|
| capture | Do we have a real (sanitized) example of behavior? |
| model | Is there a profile + typed intent for this asset? |
| simulate | Does the idea work offline against stub/sim? |
| shadow | Would ops accept the recommendation log? |
| field | Is there explicit write approval and rollback? |

## Weekly habit (growth loop)

After any field touch:

1. Half-page playbook in `playbooks/`
2. Profile stub update in `profiles/`
3. Optional anonymized capture in `captures/`
4. Failing or characterizing test if behavior surprised you
5. Only then a policy experiment

## Success criteria (when you return)

You can:

- [ ] Point a new engineer at `START_HERE.md` and they find the mission in 5 minutes
- [ ] Add a VMS or RWIS read path without rewriting the NTCIP ASC stack
- [ ] Drop a sanitized profile for a site you visited this month
- [ ] Run a policy in shadow mode and get a recommendation log
- [ ] Keep airport learning inside `airport_lab/` with zero prod credentials

## Related docs

- [`ARCHITECTURE.md`](ARCHITECTURE.md) -- platform seams to keep stable
- [`ROADMAP.md`](ROADMAP.md) -- ordered next steps
- [`ntcip_architecture.md`](ntcip_architecture.md) -- NTCIP layered stack detail
