# Airport Lab (Sandbox Only)

Adjacent learning space for **airport systems** (security, video, access
concepts). This is intentionally isolated from roadway ITS write paths.

## Hard rules

1. Synthetic identities and mock APIs only
2. No production PACS/VMS credentials, badge data, or live camera URLs
3. No "shadowing" live airport security controls without written authority
4. Prefer architecture notes and workflow drills over integrations

## Suggested learning modules (create as you go)

| Module | Content |
|--------|---------|
| `notes/video_architecture.md` | How airport video relates to roadway CCTV/ONVIF skills |
| `notes/access_control_concepts.md` | Zones, badges, anti-passback (conceptual) |
| `mocks/` | Fake event JSON for door / alarm / camera workflows |
| `drills/` | Tabletop scripts (lost badge, camera offline) |

## Bridge from roadway ITS

Skills that transfer: CCTV presets/verify, event timelines, multi-system
playbooks, shadow-before-act discipline. Protocols and governance differ --
do not assume NTCIP patterns apply.
