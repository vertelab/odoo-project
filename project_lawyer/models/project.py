from odoo import models, api, fields


class Project(models.Model):
    _inherit = 'project.project'

    is_lawyer = fields.Boolean(string='Is Lawyer Project')
    counterpart_id = fields.Many2one(comodel_name='res.partner',string="Counterpart")
    stakeholder_ids = fields.Many2many(comodel_name='res.partner',string="Stakeholders")
    conflict_of_interest = fields.Selection([('yes','Yes'),('no','No'),('-','-')],string='Conflict of interest')

    @api.depends('partner_id','counterpart_id','stakeholder_ids')
    def autocheck_coi(self):
        coi_domain = [('id','=',self.counterpart_id)]
        partners = self.env['res.partner'].search([('id','=',self.counterpart_id)])
        projects = self.env['project.project'].search([('','','')])

 
    def check_coi(self):
        pass
