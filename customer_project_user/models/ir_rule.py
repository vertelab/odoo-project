from odoo import api, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class IrRule(models.Model):
    _inherit = 'ir.rule'

    def _compute_domain(self, model_name, mode="read"):
        if self.env.user.has_group('customer_project_user.group_project_customer_user'):
            if model_name in ('project.project', 'project.task'):
                rules = self._get_rules(model_name, mode=mode)
                if not rules:
                    return []
                eval_context = self._eval_context()
                user_groups = self.env.user.groups_id
                base_group_user = self.env.ref('base.group_user')
                group_domains = []
                global_domains = []
                for rule in rules.sudo():
                    dom = safe_eval(rule.domain_force, eval_context) if rule.domain_force else []
                    dom = expression.normalize_domain(dom)
                    if not rule.groups:
                        global_domains.append(dom)
                    elif rule.groups & user_groups:
                        if base_group_user not in rule.groups:
                            group_domains.append(dom)
                if not group_domains:
                    return expression.AND(global_domains)
                return expression.AND(global_domains + [expression.OR(group_domains)])
        return super()._compute_domain(model_name, mode=mode)
