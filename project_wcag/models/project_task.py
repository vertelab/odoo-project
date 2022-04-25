import logging
import base64
import json
import traceback

from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'
    task_wcag_ids = fields.One2many(comodel_name='project.task.wcag', string="Wcags", help="Is a list of wcag criteria for this task/object", inverse_name='task_id', ondelete='cascade')
    ainspector_report = fields.Binary()

    rule_count = fields.Integer(compute='_compute_rule_count', string="Task Count")
    def _compute_rule_count(self):
        self.rule_count = len(self.task_wcag_ids) or 0

    unfinished_rule_count = fields.Integer(compute='_compute_unfinished_rule_count', string="Unfinished Task Count")
    def _compute_unfinished_rule_count(self):
        self.unfinished_rule_count = len([x for x in self.task_wcag_ids if x.wcag_state is False]) or 0

    def parse_data(self, wcag_rule, file_data):
        for wcag_rule in self.task_wcag_ids:
            if wcag_rule.wcag_state:
                # Do not update if the state is already set.
                continue
            results = []
            for rule_result in file_data.get("rule_results", []):
                if rule_result.get('success_criteria_code') == wcag_rule.wcag_id.w3c_no:
                    results.append(rule_result.get('result_value_nls'))
            if 'V' in results:
                wcag_rule.wcag_state = '1'
            elif 'MC' in results:
                wcag_rule.wcag_state = '5' # TODO: option for this
                wcag_rule.extra_notes = _("Set as OK due to MC rule")
            elif 'P' in results:
                wcag_rule.wcag_state = '5'
            elif 'N/A' in results and len(list(x for x in results if x != 'N/A')) == 0:
                wcag_rule.extra_notes = _("Set as N/A due to:\n1. No violations\n2. No Manulal checks\n3. No Pass")
                wcag_rule.wcag_state = '3'
            elif results:
                wcag_rule.wcag_state = '5'

    def add_ainspector_file(self, ainspector_value):
        try:
            file_data = json.loads(base64.b64decode(ainspector_value))
            for wcag_rule in self.task_wcag_ids:
                self.parse_data(wcag_rule, file_data)

            filename = datetime.now().strftime("Report_added_%Y%m%d%H%M%S.json")
            attachment_vals = {
                    'res_model': 'project.task',
                    'res_id': self.id,
                    'datas': ainspector_value,
                    'name': filename,
                    }
            self.env['ir.attachment'].create(attachment_vals)
        except:
            _logger.warning(traceback.format_exc())
            raise UserError(_("Unexpected file added to task."))

    def write(self, vals):
        if 'ainspector_report' in vals:
            ainspector_value = vals.get('ainspector_report')
            vals['ainspector_report'] = None
            self.add_ainspector_file(ainspector_value)

        return super(ProjectTask, self).write(vals)
