# odoo-project
Project related modules

## Porteringsstatus

18.0 är baseline. 19.0/20.0 visar om p-filen har ett villkor för utgåvan
— inte om grenen finns. Blockerare är `depends` som saknas i 20.0
(kärna + alla 20.0-grenar).

| Modul | Beskrivning | Manifest | p-fil | 19.0 | 20.0 | Blockerare |
|---|---|---|---|---|---|---|
| customer_project_user | A user type for project customers. | 0.3.0 | 5 | ✓ | ✓ | — |
| project_ai | AI coworkers for project management — Task Manager + Proj... | 3.0.1 | 1 | — | — | `web_widget_mermaid_field` |
| project_archiving | A user type for project customers. | 0.1.0 | 0 | — | — | — |
| project_attachments | Embedded action to view attachment connected to task and ... | 0.1.0 | 0 | — | — | — |
| project_branch_sync | Short (1 phrase/line) summary of the module's purpose, us... | 1.0 | 6 | — | — | `queue_job` |
| project_ci | Adds CI pipeline tracking to projects. | 1.0.0 | 0 | — | — | — |
| project_ci_base | Provides base models for CI pipeline tracking in projects. | 1.0.0 | 0 | — | — | — |
| project_equity_portfolio | Each project of this type is a equity portfolio | 1.0 | 11 | — | — | — |
| project_github | Creates releations between Github and a projec. | 1.0.0 | 0 | — | — | — |
| project_github_task | Short (1 phrase/line) summary of the module's purpose, us... | 1.0 | 4 | — | — | — |
| project_github_webhook | Short (1 phrase/line) summary of the module's purpose, us... | 1.0 | 4 | — | — | — |
| project_hr_validation | Project HR Validation | 1.0.0 | 0 | — | — | — |
| project_mis_budget | Setup a link between budget and projekt/task. | 0.1 | 9 | — | — | — |
| project_module_monitor | We have the need to keep track of our modules. | 1.0.0 | 0 | — | — | — |
| project_tags_company | Add company_id to project.tags. | 1.0.0 | 0 | — | — | — |
| project_task_add_default_stage | Adds an option to set default project task stages. These ... | 1.1.0 | 1 | — | — | — |
| project_task_closed | Adds a closed state to project tasks. | 1.0.0 | 0 | — | — | — |
| project_task_monitor | Add montitor capabilities to a project | 1.0 | 9 | — | — | — |
| project_task_number | Gives every task an uniq id | 1.0 | 6 | — | — | — |
| project_task_offer_action | Creates an offer from a project task. | 0.0.0 | 0 | — | — | — |
| project_task_payment | Create a payment from a task, for the person who should b... | 1.1.0 | 0 | — | — | — |
| project_task_swot | add SWOT capabilities to a project | 1.0 | 8 | — | — | `web_widget_mermaid_field` |
| project_task_weekno | Project Task WeekNo. | 0.1.0 | 0 | — | — | — |
| project_timesheet_activity_begin_end | Task Timesheet Activities -- Set start // stop!. | 1.0.3 | 0 | — | — | — |
| project_track_subproject | Project Track Subtask. | 0.0.0 | 0 | — | — | — |
| project_wcag | Project WCAG. | 0.1.0 | 0 | — | — | — |
| website_project_wcag | Website Project WCAG. | 0.1.0 | 1 | — | ✓ | — |
