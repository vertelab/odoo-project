# -*- coding: utf-8 -*-
"""project.project och project.task — OKF-indexerbara (project_ai).

VARFÖR: ett projekt och dess uppgifter ÄR kunskap om vad som ska göras
och varför. `description` (Html) ligger i en kolumn som varken BM25
eller embeddings ser.

Modellerna äger sina KÄLLOR; `ai.okf.mixin` äger fälten och flaggan.
"""

from odoo import models, fields


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'ai.okf.mixin']

    # OKF-taggar: egen relationstabell (en many2many kan inte ligga
    # pa en abstrakt mixin — den ger samma tabell for alla arvande).
    okf_tags = fields.Many2many(
        'ai.okf.tag', 'project_project_okf_tag_rel', 'res_id', 'tag_id',
        string='OKF Tags')

    # ── Källor ─────────────────────────────────────────────────────────
    #
    # `okf_body`  generisk: `name` + `description`
    # `okf_tags`  generisk: `tag_ids` (målmodellen project.tags)
    # `okf_links` generisk: `partner_id` (res.partner bär mixinen via
    #             base_ai), `user_id` (res.users), `company_id`

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12)."""
        return 'project_project'

    def _okf_summary_source(self):
        """Projektets EGEN sammanfattning: namn + kund.

        Deterministisk — samma projekt ger samma text varje gång. Utan
        denna föll sammanfattningen tillbaka på en LLM-tur per post
        (okf-mixin-install D2/D3).

        Kunden (`partner_id`) är det som gör projektet sökbart vid sidan
        av namnet. Saknas kunden byggs texten av namnet enbart — ingen
        tom eller felaktig text uppstår.
        """
        self.ensure_one()
        bits = [self.name or '']
        if self.partner_id:
            bits.append('Kund: %s' % self.partner_id.name)
        return ' — '.join(b for b in bits if b) or None

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        Räknare (`task_count`, `ai_session_count`, `ai_token_total`)
        ändras ofta och säger inget om texten.
        """
        return {'name', 'description', 'partner_id', 'user_id',
                'date_start', 'date', 'active'}

    def _okf_skip_reason(self):
        """Arkiverat projekt = "tomt just nu", inte "tomt för alltid"."""
        return None

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera modellen för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är
        `@api.model` på en abstrakt modell (mätt på luke18 2026-09-22).
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('project.project')
        return res


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'ai.okf.mixin']

    # OKF-taggar: egen relationstabell.
    okf_tags = fields.Many2many(
        'ai.okf.tag', 'project_task_okf_tag_rel', 'res_id', 'tag_id',
        string='OKF Tags')

    # ── Källor ─────────────────────────────────────────────────────────
    #
    # `okf_body`  generisk: `name` + `description`
    # `okf_tags`  generisk: `tag_ids`
    # `okf_links` generisk: `project_id` (project.project bär mixinen),
    #             `partner_id`, `user_ids`, `parent_id` (self-relation)

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12)."""
        return 'project_task'

    def _okf_summary_source(self):
        """Uppgiftens EGEN sammanfattning: namn + etapp + projekt.

        Deterministisk — samma uppgift ger samma text varje gång. Utan
        denna föll sammanfattningen tillbaka på en LLM-tur per post, och
        `project.task` är den mest indexerade modellen i drift (>15 000
        koncept, okf-mixin-install D2/D3).

        Etappen och projektet är det som gör uppgiften sökbar vid sidan av
        namnet. Saknas etappen eller projektet byggs texten av de fält som
        finns — ingen tom eller felaktig text uppstår.
        """
        self.ensure_one()
        bits = [self.name or '']
        if self.stage_id:
            bits.append('Etapp: %s' % self.stage_id.name)
        if self.project_id:
            bits.append('Projekt: %s' % self.project_id.name)
        return ' — '.join(b for b in bits if b) or None

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        `stage_id` ingår: etappen är en del av uppgiftens mening.
        Räknare och datum utan innehåll utesluts.
        """
        return {'name', 'description', 'stage_id', 'project_id',
                'partner_id', 'user_ids', 'priority', 'active'}

    def _okf_skip_reason(self):
        """Arkiverad uppgift = "tomt just nu", inte "tomt för alltid"."""
        return None

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera modellen för dirty-indexering."""
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('project.task')
        return res
