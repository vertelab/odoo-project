# odoo-project — gren 19.0

> **Denna gren är avsiktligt tom.** Modulerna är INTE portade till Odoo 19.
> Grenen finns så att dev-miljöer (`hansolo19`) kan klona den utan att falla,
> men den påstår ingenting om att koden är portad.

## Baseline

| | |
|---|---|
| Källa | `20.0` |
| Moduler | **27** |
| Grenar i repot | `12.0`, `12.0-af`, `12.0-test`, `13.0`, `14.0`, `14.0_notebook_documents`, `14.0_start_stop_time_on_caledar`, `16.0`, `17.0`, `18.0`, `20.0`, `Dev-12.0-Fenix-Sprint-02`, `Dev-13-project_wbs`, `customer-project-user`, `master` |

## Moduler

- `customer_project_user`
- `project_ai`
- `project_archiving`
- `project_attachments`
- `project_branch_sync`
- `project_ci`
- `project_ci_base`
- `project_equity_portfolio`
- `project_github`
- `project_github_task`
- `project_github_webhook`
- `project_hr_validation`
- `project_mis_budget`
- `project_module_monitor`
- `project_tags_company`
- `project_task_add_default_stage`
- `project_task_closed`
- `project_task_monitor`
- `project_task_number`
- `project_task_offer_action`
- `project_task_payment`
- `project_task_swot`
- `project_task_weekno`
- `project_timesheet_activity_begin_end`
- `project_track_subproject`
- `project_wcag`
- `website_project_wcag`

## Blockerare

**3 externa beroenden saknas** i Odoo 19-kärnan och OCA 19.0:

| Beroende | Behövs av |
|---|---|
| `account_mis_budget` | `project_mis_budget` |
| `queue_job` | `project_branch_sync` |
| `web_widget_mermaid_field` | `project_ai`, `project_task_swot` |

### Prioritering

Ett beroende som blockerar många moduler ger mest nytta att lösa först:

- `web_widget_mermaid_field` — frisläpper **2** modul(er)
- `account_mis_budget` — frisläpper **1** modul(er)
- `queue_job` — frisläpper **1** modul(er)

## Nästa steg

Portering sker på `*-pfile`-maskin med versionsagnostisk kod
(`.p.py` / `.p.xml`). Se `/skill:odoo-pfiles`.
