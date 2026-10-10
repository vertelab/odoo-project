# Mönstret "additiv förmågeexpansion"

Hur en ny AI-modul lägger till förmågor på en befintlig coworker **utan**
att röra den ägande modulens data. Infört med `project_ai` /
`project_scrum_ai` / `prd_ai` (T/12020).

## Problemet

En coworker kan behöva växa med förmågor från flera moduler. Naiv lösning:
varje modul skriver till coworkerns `skill_ids`/`agent_ids` med
`(6, 0, [...])`. Det ger två fel:

1. **Ordningskänslighet** — sista modulen som installeras vinner; de andra
   modulernas förmågor försvinner tyst.
2. **Oren avinstallation** — avinstallerar man en modul blir dess poster
   kvar som döda referenser, eller så raderas den andra modulens poster.

## Mönstret

**Varje modul äger sina egna poster och lägger till länkrader.**

```
project_ai          skapar agent_project_analyst
                    + coworker_agent_project_analyst (länkrad)
project_scrum_ai    skapar agent_scrum_master
                    + coworker_agent_scrum_master (länkrad)
prd_ai              skapar agent_prd_analyst
                    + coworker_agent_prd_analyst (länkrad)
```

Alla länkrader pekar på **samma** coworker
(`project_ai.coworker_project_task_manager`). Ingen modul skriver en
`(6, 0, [...])`-lista på coworkerns `agent_ids` — de lägger bara till en rad.

### Regler

| Regel | Varför |
|-------|--------|
| Skapa agenten i **din** modul, med ditt xmlid-prefix | Avinstallation tar bort exakt dina poster |
| Lägg till en `ai.coworker.agent`-rad — skriv aldrig över `agent_ids` | Ingen kollision mellan moduler |
| Sätt `sequence` så ordningen blir deterministisk | Undvik slumpad routing-ordning |
| Referera coworkern via `ref('project_ai.coworker_project_task_manager')` och lägg `project_ai` i `depends` | Explicit beroende, ingen tyst krasch |
| Koppla Pi-skills som **katalog** (namn + trigger), inte som prompttext | Promptkostnaden (T/12020 task 1.4: ~64 % besparing) |
| Skapa agenten **före** länkraden i manifestets `data`-lista | Länkraden refererar agentens xmlid |

### Vad som INTE ska göras

- ❌ Skriva `(6, 0, [...])` på en coworker som en annan modul äger.
- ❌ Referera ett verktyg/en skill som inte finns i din egen modul (t.ex.
  `task_link_module` — död referens → `--update` kraschar med
  "External ID not found").
- ❌ Kopiera Pi-skill-text in i `recipe_text` — dubbel sanning + dyr prompt.

## Filer

```
<modul>/data/<modul>_agents.xml    ← agent + länkrad (ny fil per modul)
<modul>/__manifest__.py            ← 'data/<modul>_agents.xml' FÖRE ev. coworker-fil
```

## Verifiering

```bash
# Agenten finns och är länkad
odoo shell -d <db> --no-http <<'EOF'
c = env.ref('project_ai.coworker_project_task_manager')
print([(r.agent_id.name, r.role, r.sequence) for r in c.agent_ids])
EOF

# Avinstallation tar bort rätt poster
#   → avinstallera prd_ai: PRD-analytikern + dess länkrad försvinner,
#     Projektanalytiker och Odoo-utvecklare ligger kvar.
```

## Referensimplementation

`project_ai/data/project_agents.xml` — Projektanalytiker + Odoo-utvecklare.
