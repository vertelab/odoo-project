# Project: AI Coworkers (project_ai)

AI-coworkers för projektarbete — Project Task Manager (openai_api) med
task-verktyg. Innehåller även **kostnadskontext** på sessioner
(session-cost-context) för kostnadsuppföljning per projekt/kund.

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

- `task_get`, `task_set_status`, `task_link_module`, `task_update_fields` —
  taggar sessionen med den arbetade taskens projekt/partner
  (`_capture_session_from_task`).
- `cost_context_get` — läser sessionens projekt/uppgift/kund + bekräftelse.
- `cost_context_set` — skriver projekt/uppgift/kund och sätter
  `cost_context_confirmed = true` (HITL-skyddad skrivåtgärd).

### Skill

`skill_cost_context` ("Cost Context — kostnadsbärande arbete") är kopplad
till Project Task Manager: alla openai_api-sessioner är kostnadsbärande;
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

- Skrivåtgärder (task_set_status, task_link_module, task_update_fields,
  cost_context_set) utlöser godkännanden via `hitl_threshold`.
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
