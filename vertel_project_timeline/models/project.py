from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt
from odoo.osv import expression

class ProjectTaskType(models.Model):
    _inherit = "project.task.type"
    
    crossed_over_in_timeline = fields.Boolean(string="Crossed Over Timeline")

class ProjectTask(models.Model):
    _inherit = "project.task"

    crossed_over_in_timeline = fields.Boolean(
        related='stage_id.crossed_over_in_timeline',  # Use the related field from the stage model
        store=True,
        readonly=True
    )

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **kwargs):
        if kwargs.get('timeline', False):
            # print(domain)
            for onedomain in domain:
                if type(onedomain) == list and 'display_project_id' == onedomain[0]:
                    onedomain[0] = "project_id"
            # print(domain)
        # if 'project_id' in self.env.context:
        #     tag_ids = self._name_search()
        #     domain = expression.AND([domain, [('id', 'in', tag_ids)]])
        #     return self.arrange_tag_list_by_id(
        #         super().search_read(domain=domain, fields=fields, offset=offset, limit=limit), tag_ids)
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        
    
