from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt
from odoo.osv import expression


class ProjectTask(models.Model):
    _inherit = "project.task"

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **kwargs):
    #     print(domain)
    #     # if 'project_id' in self.env.context:
    #     #     tag_ids = self._name_search()
    #     #     domain = expression.AND([domain, [('id', 'in', tag_ids)]])
    #     #     return self.arrange_tag_list_by_id(
    #     #         super().search_read(domain=domain, fields=fields, offset=offset, limit=limit), tag_ids)
    #     return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)