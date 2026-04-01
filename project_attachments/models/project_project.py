from odoo import models, fields, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def action_open_project_attachments(self):
        task_ids = self.task_ids.ids
        domain = [
            '|',
            '&', ('res_model', '=', 'project.project'), ('res_id', '=', self.id),
            '&', ('res_model', '=', 'project.task'), ('res_id', 'in', task_ids),
            ('type', '=', 'binary'),
        ]
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'views': [[False, 'kanban'], [False, 'list'], [False, 'form']],
            'domain': domain,
            'context': {},
        }