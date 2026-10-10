# Project: AI Coworkers (project_ai)

AI-coworker för projektarbete — **Project** (supervisor) med två
specialist-agenter (Projektanalytiker + Odoo-utvecklare) och task-verktyg.
Innehåller även **kostnadskontext** på sessioner (session-cost-context)
för kostnadsuppföljning per projekt/kund.

## Arkitektur — coworker + agenter

```
┌──────────────────────────────────────────────────────────────────┐
│  ai.coworker #18 "Project"   (orchestration_mode = supervisor)   │
│                                                                  │
│  skills: 2 bas-skills (AI-plan-arbetsflödet, Cost Context)       │
│  tools:  5 task-/kostnadsverktyg                                 │
│  agenter (ai.coworker.agent):                                    │
│    ├── Projektanalytiker  (sequence 10) — steg 1–4: analys, plan │
│    └── Odoo-utvecklare    (sequence 20) — steg 5–6: bygge, tester│
└──────────────────────────────────────────────────────────────────┘
         ▲                              ▲
         │ lägger till SIN agent        │ lägger till SIN agent
         │ + länkrad                    │ + länkrad
    project_scrum_ai                 prd_ai
    (Scrum-master)                   (PRD-analytiker)
```

**Mönstret — additiv förmågeexpansion:** varje modul skapar sin egen agent
och lägger till en `ai.coworker.agent`-länkrad mot
`project_ai.coworker_project_task_manager`. Ingen modul skriver över en
delad lista → ingen ordningskänslighet, ren avinstallation (agenten +
länkraden försvinner, coworkern förblir intakt).

Se även `docs/additiv-formageexpansion.md` för hur nya AI-moduler följer
mönstret.

## Skills — två källor

| Källa | Var texten bor | Vad Odoo bär | Kostnad |
|-------|----------------|--------------|---------|
| **Pi-skill** (`odoo-18`, `odoo-crm`, …) | `/usr/local/share/pi/skills/<namn>/SKILL.md` | Namn + trigger + ~500-teckens sammanfattning | Billig — Pi laddar via `/skill:namn` |
| **Odoo-skill** (ägд av modulen) | `ai.skill.recipe_text` (data-XML) | Full text | Dyr — injiceras i prompten |

Coworkern och agenterna bär **bara** Odoo-skills som full text. Pi-skills
refereras som katalog (namn + trigger) — Pi laddar texten själv.

## Kostnadskontext — session-fält

`ai.coworker.session` får domänfält via arv:

| Fält | Typ | Beskrivning |
|------|-----|-------------|
| `project_id` | project.project | Projekt som sessionens kostnad belastar |
| `task_id` | project.task | Uppgift som sessionen arbetar med |
| `partner_id` | res.partner (core) | Kund — härleds via resolver-strategin |
| `pi_session_id` | Char (core) | Pi-sessionens UUID (1:1, index) |
| `cost_context_confirmed` | Boolean (core) | Kostnadskontext bekräftad (en gång/session) |

### Härledning (resolver "project_partner")

`partner_id` härleds normalt ur projektets partner:

- task känd → `task.project_id.partner_id`
- endast projekt → `project.partner_id`

Skrivpunkten är `_capture_context(task=None, project=None, partner=None)`
på sessionen (en enda plats; "senast arbetad kontext vinner" — inga
nollställningar).

### Verktyg

- `task_get`, `task_set_status`, `task_update_fields` — taggar sessionen
  med den arbetade taskens projekt/partner (`_capture_session_from_task`).
- `cost_context_get` — läser sessionens projekt/uppgift/kund + bekräftelse.
- `cost_context_set` — skriver projekt/uppgift/kund och sätter
  `cost_context_confirmed = true` (HITL-skyddad skrivåtgärd).

> **Borttaget:** `task_link_module` refererades tidigare här men har
> aldrig funnits i `project_tools.xml`. Referensen är borttagen
> (T/12020) — modulkoppling görs i stället via `ai_plan` + `sprint.module`
> enligt AI-plan-skillens steg 8.

### Skill

`skill_cost_context` ("Cost Context — kostnadsbärande arbete") är kopplad
till Project + båda agenterna: alla openai_api-sessioner är kostnadsbärande;
coworkern frågar en gång efter projekt (eller kund om projekt saknas) med
frågetexten från `cost_context_question` och bekräftar belastningen.

## Sessionlivscykel (Pi)

- Ny Pi-session (start/`/new`) → ny Odoo-session via
  `POST /ai/v1/sessions/lookup` (find-or-create på `pi_session_id`).
- Resume → samma Odoo-session återfinns (kontext + bekräftelse bevarade).
- Fork → ny session med kontext kopierad (`copy_from_pi_session_id`).

## Kostnadsuppföljning

- Pivot-vy "AI-kostnadsuppföljning" (meny: Session →
  AI-kostnadsuppföljning): tokens per kund/projekt.
- Smartknapp "AI-sessioner (tokens)" på `project.project` och
  `res.partner` (kundkortet) — antal sessioner + totala tokens.

## Test

`odoo --test-enable -u project_ai` (eller `checkmodule -t`): se
`tests/test_cost_context.py` (taggning, härledning, livscykel, flagga,
append-only, smartknappar).

## HITL via OpenAI tool_calls (openai-api-pi-orchestration)

När en Pi-agent (eller Cline/Continue.dev) ansluter via
`/ai/openai/<id>/v1/chat/completions` kan coworkern pausa loopen och
returnera `request_hitl_input`/`request_hitl_approval`-tool_calls i
OpenAI-svaret. Klienten exekverar dem (t.ex. via `ctx.ui.confirm`/`input`
i pi) och svarar med `role:"tool"`-meddelanden i nästa request — loopen
återupptas.

- Skrivåtgärder (task_set_status, task_update_fields, cost_context_set)
  utlöser godkännanden via `hitl_threshold`.
- Kostnadskontext-frågan ("Vilket projekt gäller detta arbete?") skickas
  som `request_hitl_input` när kontext saknas.
- Svaret innehåller `system_prompt_add` (instruktion till klienten) och
  `skill_to_load` (pi-kompatibel skill) — konfigureras via
  `pi_instruction` på openai_api-init-typen.
- Gäller ENBART init-typen `openai_api` — övriga init-typer orkestrerar
  som förut.

## Odoo 18-regler

- Vyer: `list` (aldrig `tree`), inga defensiva `<delete>`.
- Uppgradering: `--update project_ai` (inte `--init`).
