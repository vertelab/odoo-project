from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    is_lawyer = fields.Boolean(string='Is Lawyer Project')
    counterpart_id = fields.Many2one(comodel_name='res.partner',string="Counterpart")
    stakeholder_ids = fields.Many2many(comodel_name='res.partner',string="Stakeholders")
    conflict_of_interest = fields.Selection([('yes','Yes'),('no','No'),('-','-')],string='Conflict of interest')
    is_reviewed_customer_COI = fields.Boolean(string="", default=False)
    is_reviewed_counterpart_COI = fields.Boolean(string="", default=False)
    is_reviewed_stakeholders_COI = fields.Boolean(string="", default=False)

    @api.depends('partner_id','counterpart_id','stakeholder_ids')
    def autocheck_coi(self):
        coi_domain = [('id','=',self.counterpart_id)]
        partners = self.env['res.partner'].search([('id','=',self.counterpart_id)])
        projects = self.env['project.project'].search([('','','')])


    def action_privacy_lookup_customer(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('privacy_lookup.action_privacy_lookup_wizard')
        action['context'] = {
            'default_email': self.partner_id.email,
            'default_name': self.partner_id.name,
            'default_project_lookup_type': "customer",
            'default_project_id': self.id,
        }
        return action    
    
    def action_privacy_lookup_counterpart(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('privacy_lookup.action_privacy_lookup_wizard')
        action['context'] = {
            'default_email': self.counterpart_id.email,
            'default_name': self.counterpart_id.name,
            'default_project_lookup_type': "counterpart",
            'default_project_id': self.id,
        }
        return action    
    
    def action_privacy_lookup_stakeholders(self):
        # self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('project_lawyer.action_privacy_lookup_wizard_stakeholders')  
        priv_ids = []

        for stake in self.stakeholder_ids:
            priv_record = self.env['privacy.lookup.wizard'].search([
            ('email','=', stake.email),
            ('name','=',stake.name),
            ('project_lookup_type','=',"stakeholders"),
            ('project_id','=', self.id),

            ])
            if not priv_record:
                priv_record = self.env['privacy.lookup.wizard'].create({
                    'email': stake.email,
                    'name': stake.name,
                    'project_lookup_type': "stakeholders",
                    'project_id': self.id,
                })
            priv_ids.append(priv_record.id)

        action['domain'] = [('id','in',priv_ids)]

        action["context"] = {"default_wizard_ids": ",".join(map(str,priv_ids))}

        return action
