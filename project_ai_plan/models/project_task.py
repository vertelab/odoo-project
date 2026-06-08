from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    ai_plan = fields.Text(string='AI Plan')
    ai_usecase = fields.Html(string='AI Use Case', sanitize=False)
    ai_usecase_mermaid = fields.Text(string='AI Use Case Mermaid')
