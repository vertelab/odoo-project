from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
import os
import requests

from lxml import html


ZERO_WIDTH_CHAR = '\u200b'
VALIDATION_SELECTIONS = [('auto', 'Automatic'), ('mixed', 'Mixed'), ('manual', 'Manual')]

#Gonna be a list of rules based on a excel spread sheet
class WcagRule(models.Model):
    _name = 'wcag.rule'
    _rec_name = 'display_wcag_name'
    display_wcag_name = fields.Char()
    wcag_url = fields.Char()
    w3c_no = fields.Char()
    conformance_level = fields.Char()
    description = fields.Char()
    validate_method = fields.Selection(VALIDATION_SELECTIONS,'Validate Method', default='manual')

    @api.model
    def create(self, vals):
        display_wcag_name = vals.get('w3c_no') or "" + " " + vals.get('conformance_level') or "" + " " +  vals.get('description') or ""
        vals['display_wcag_name'] = display_wcag_name
        res = super(WcagRule, self).create(vals)
         # ~ if res.self.task_id:
            # ~ res.task_project_id = res.task_id.project_id
        return res

    def write(self, values):
        if values.get('description') or values.get('w3c_no') or values.get('conformance_level'):
            w3c_no = values.get('w3c_no') or self.w3c_no or ""
            conformance_level = values.get('conformance_level') or self.conformance_level or ""
            description = values.get('description') or self.description or ""
            values['display_wcag_name'] = f"{w3c_no}{conformance_level}: {description}"
        res = super(WcagRule, self).write(values)
        return res

    @api.model
    def set_urls(self):
        for x in self.get_urls():
            if rule := self.env['wcag.rule'].search([("w3c_no",'=',x[0])]):
                rule.wcag_url = x[1]


    def get_urls(self):
        url = 'https://www.w3.org/TR/WCAG21/'
        try:
            data = html.document_fromstring(requests.get(url).text)
            for list_elem in data.xpath("//li[@class='tocline']/a[@class='tocxref']"):
                if span := list_elem.xpath("./span[@class='secno']"):
                    yield (span[0].text.strip(), os.path.join(url, list_elem.get('href')))
        except Exception as e:
            _logger.warning(e)

# ~ #A class so we can have a unique wcag rule per projects, gets default values from a wcag.rule
# ~ #############
class WcagProjectRule(models.Model):
    _name = 'wcag.project.rule'
    _rec_name = 'display_wcag_name'
    wcag_id = fields.Many2one(comodel_name = "wcag.rule", string = "Wcag Rule", required=True)
    display_wcag_name = fields.Char()
    wcag_url = fields.Char()
    w3c_no = fields.Char()
    conformance_level = fields.Char()
    description = fields.Char()
    validate_method = fields.Selection(VALIDATION_SELECTIONS,'Validate Method', default='manual')
    project_id = fields.Many2one(comodel_name = "project.project", string = "Project", help = "The project which this rule belongs to",ondelete='cascade')

    @api.model
    def create(self, vals):
        #Get default values from selected wcag.rule
        if vals.get('wcag_id'):
            vals['wcag_url'] = self.env['wcag.rule'].browse(vals['wcag_id']).wcag_url
            vals['w3c_no'] = self.env['wcag.rule'].browse(vals['wcag_id']).w3c_no
            vals['conformance_level'] = self.env['wcag.rule'].browse(vals['wcag_id']).conformance_level
            vals['description'] = self.env['wcag.rule'].browse(vals['wcag_id']).description
            vals['validate_method'] = self.env['wcag.rule'].browse(vals['wcag_id']).validate_method
            vals['display_wcag_name'] = self.env['wcag.rule'].browse(vals['wcag_id']).display_wcag_name
        res = super(WcagProjectRule, self).create(vals)

        return res

    def write(self, values):
        if values.get('description') or values.get('w3c_no') or values.get('conformance_level'):
            w3c_no = values.get('w3c_no') or self.w3c_no or ""
            conformance_level = values.get('conformance_level') or self.conformance_level or ""
            description = values.get('description') or self.description or ""
            values['display_wcag_name'] = f"{w3c_no}{conformance_level}: {description}"

        res = super(WcagProjectRule, self).write(values)
        return res


# ~ ##############


class ProjectTaskWcag(models.Model):
    _name = 'project.task.wcag'
    _rec_name = 'display_wcag_name'
    wcag_id = fields.Many2one(comodel_name = "wcag.rule", string = "Wcag Rule", readonly=True)
    wcag_project_id = fields.Many2one(comodel_name = "wcag.project.rule", string = "Wcag Project Rule", required=True)
    wcag_url = fields.Char(related='wcag_id.wcag_url')
    validate_method = fields.Selection(VALIDATION_SELECTIONS,'Validate Method', default='manual')
    task_id = fields.Many2one(comodel_name = "project.task",string = "Task",ondelete='cascade')
    wcag_state = fields.Selection(
            [('1', 'Failed'),('2', '*blank*'),('3', 'Not relevant'), ('4', 'Partial'), ('5', 'OK')],
            'State',
            default=False,
            group_operator="max")
    notes = fields.Text(String = "Notes", group_operator="max")
    display_wcag_name = fields.Char()

    def get_project_id(self):
        if self.task_id:
            return self.task_id.project_id
        else:
            return False

    task_project_id = fields.Many2one(comodel_name="project.project", default=get_project_id, readonly=True, string = "Project")

    @api.model
    def create(self, vals):
        if vals.get('task_id'):
            vals['task_project_id'] = self.env['project.task'].browse(vals['task_id']).project_id.id
        else:
            vals['task_project_id'] = False

        if vals.get('wcag_project_id'):
             vals['validate_method'] = self.env['wcag.project.rule'].browse(vals['wcag_project_id']).validate_method
             vals['wcag_id'] = self.env['wcag.project.rule'].browse(vals['wcag_project_id']).wcag_id.id
             vals['display_wcag_name'] = self.env['wcag.project.rule'].browse(vals['wcag_project_id']).display_wcag_name
        else:
            vals['validate_method'] = False
            vals['wcag_id'] = False
        res = super(ProjectTaskWcag, self).create(vals)
        return res

    def write(self, values):
        if 'task_id' in values:
            if values.get('task_id'):
                values['task_project_id'] = self.env['project.task'].browse(values['task_id']).project_id
            else:
                values['task_project_id'] = False

        if 'wcag_project_id' in values:
            values['wcag_id'] = self.env['wcag.project.rule'].browse(values['wcag_project_id']).wcag_id.id
            values['display_wcag_name'] = self.env['wcag.project.rule'].browse(values['wcag_project_id']).display_wcag_name

        res = super(ProjectTaskWcag, self).write(values)
        return res


    def action_read_task_rule(self):
        self.ensure_one()
        return {
            'name': self.display_wcag_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task.wcag',
            'res_id': self.id,
        }
